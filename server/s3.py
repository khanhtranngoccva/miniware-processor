import asyncio
import hashlib
import math
import os
import aiobotocore.response
import aiofiles
import aioboto3 as boto3
import mimetypes

import botocore.exceptions

from helpers import asyncio_patch

if __name__ == '__main__':
    import server.env

_session = boto3.session.Session()

ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
PRIMARY_BUCKET = os.environ.get("PRIMARY_BUCKET")
ENDPOINT = os.environ.get("ENDPOINT")

AWS_MULTIPART_BYTES_PER_CHUNK = 10000000


def _get_s3_client_context():
    return _session.client(service_name='s3',
                           aws_access_key_id=ACCESS_KEY,
                           aws_secret_access_key=SECRET_ACCESS_KEY,
                           endpoint_url=ENDPOINT)


async def download(asset_key, location, filename=None):
    async def _download(_asset_key, _location, _filename=None):
        async with _get_s3_client_context() as client:

            obj = await client.get_object(Bucket=PRIMARY_BUCKET, Key=_asset_key)

            if not obj:
                raise Exception("Cloud asset not found.")

            stream_body = obj["Body"]

            extension = mimetypes.guess_extension(obj['ResponseMetadata']['HTTPHeaders']['content-type']) or ""
            if _filename is None:
                _filename = os.path.basename(_asset_key)
            _filename += extension

            async with aiofiles.open(os.path.join(_location, _filename), "bw") as file:
                async for chunk in stream_body.iter_chunks():
                    await file.write(chunk)

    while True:
        try:
            await _download(asset_key, location, filename)
        except aiobotocore.response.AioReadTimeoutError:
            pass
        except Exception as e:
            raise e
        else:
            break


async def object_exists(asset_key):
    try:
        async with _get_s3_client_context() as client:
            await client.head_object(Bucket=PRIMARY_BUCKET, Key=asset_key)
    except botocore.exceptions.ClientError as e:
        try:
            if str(e.response["Error"]["Code"]) == "404":
                return False
        except KeyError:
            raise e
    return True


async def upload(asset_key, file_path):
    async with aiofiles.open(file_path, "rb") as file_handle:
        async with _get_s3_client_context() as client:
            _, ext = os.path.splitext(file_handle.name)
            file_type, _ = mimetypes.guess_type(file_handle.name)
            file_binary = await file_handle.read()
            result = await client.put_object(Bucket=PRIMARY_BUCKET, Key=asset_key, ContentType=file_type,
                                             Body=file_binary)
    return result


async def multipart_upload(asset_key, file_path):
    part_info = []
    file_shared_lock = asyncio.Lock()
    bytes_per_chunk = AWS_MULTIPART_BYTES_PER_CHUNK

    async with aiofiles.open(file_path, "rb") as file_handle:
        async with _get_s3_client_context() as client:
            async def upload_chunk(_chunk_number: int):
                offset = _chunk_number * bytes_per_chunk
                remaining_bytes = source_size - offset
                bytes_to_read = min([remaining_bytes, bytes_per_chunk])
                part_number = _chunk_number + 1

                async with file_shared_lock:
                    await file_handle.seek(offset)
                    chunk = await file_handle.read(bytes_to_read)

                resp = await client.upload_part(
                    Bucket=PRIMARY_BUCKET,
                    Body=chunk,
                    UploadId=upload_id,
                    PartNumber=part_number,
                    Key=asset_key
                )

                part_info.append({
                    "PartNumber": part_number,
                    "ETag": resp["ETag"]
                })

            source_size = os.stat(file_path).st_size
            chunks_count = int(math.ceil(source_size / float(bytes_per_chunk)))

            create_multipart_upload_resp = await client.create_multipart_upload(
                Bucket=PRIMARY_BUCKET,
                Key=asset_key
            )

            upload_id = create_multipart_upload_resp["UploadId"]

            tasks = []
            for chunk_number in range(chunks_count):
                tasks.append(upload_chunk(chunk_number))
            await asyncio.gather(*tasks)

            part_info.sort(key=lambda part: part["PartNumber"])

            list_part_resp = await client.list_parts(
                Bucket=PRIMARY_BUCKET,
                Key=asset_key,
                UploadId=upload_id,
            )

            if len(list_part_resp["Parts"]) == chunks_count:
                await client.complete_multipart_upload(
                    Bucket=PRIMARY_BUCKET,
                    Key=asset_key,
                    UploadId=upload_id,
                    MultipartUpload={
                        "Parts": part_info
                    }
                )
            else:
                await client.abort_multipart_upload(
                    Bucket=PRIMARY_BUCKET,
                    Key=asset_key,
                    UploadId=upload_id
                )


async def delete(asset_key):
    async with _get_s3_client_context() as client:
        result = await client.delete_object(Bucket=PRIMARY_BUCKET, Key=asset_key)
    return result


async def download_many(asset_keys, location):
    requests = (download(asset_id, location) for asset_id in asset_keys)
    await asyncio.gather(*requests)


async def get_download_url(asset_key):
    async with _get_s3_client_context() as client:
        result = await client.generate_presigned_url('get_object', Params={'Bucket': PRIMARY_BUCKET, 'Key': asset_key}, ExpiresIn=3600)

    return result


if __name__ == '__main__':
    async def test():
        async with aiofiles.open("../test_upload.m4v", "br") as file:
            original = hashlib.sha256(await file.read()).hexdigest()

        await multipart_upload("test/upload", "../test_upload.m4v")
        await download("test/upload", "..", "test_upload_2.m4v")

        async with aiofiles.open("../test_upload_2.m4v", "br") as file:
            downloaded = hashlib.sha256(await file.read()).hexdigest()

        assert original == downloaded


    async def test2():
        print(await object_exists("test/upload"))


    asyncio.run(test())
    asyncio.run(test2())
