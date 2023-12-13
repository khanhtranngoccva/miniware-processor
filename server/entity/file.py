import asyncio
import os
from server import s3
from server.database import database
from pefile_processor import get_hashes


def get_asset_key_from_hash(sha256: str):
    return f"executables/{sha256}"


def upload_file(path: str, sha256: str):
    asset_key = get_asset_key_from_hash(sha256)

    async def _upload():
        if await s3.object_exists(asset_key):
            return
        await s3.multipart_upload(asset_key, path)

    asyncio.run(_upload())


def create_file(path: str):
    with database:
        with database.cursor() as cur:
            size = os.stat(path).st_size

            # TODO: Hash from disk.
            with open(path, "rb") as file:
                buf = file.read()

            hashes = get_hashes(buf)

            # Commits should always be delayed to last.
            file_id = cur.execute("INSERT INTO files (size) VALUES (%s) RETURNING id", (size,)).fetchone()[0]
            for (algorithm, value) in hashes.items():
                cur.execute("INSERT INTO file_hashes (file_id, algorithm, value) VALUES (%s, %s, %s)", [
                    file_id, algorithm, value
                ])
