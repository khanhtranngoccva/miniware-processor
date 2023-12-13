import asyncio
import os

import psycopg.rows

from server import s3
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


def search_sha256(conn, file_sha256: str):
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        query = "SELECT * FROM file_hashes WHERE algorithm = 'sha256' AND value = %s"
        result = cur.execute(query, [file_sha256]).fetchone()

    return result


def create_file(conn, path: str):
    with conn.cursor() as cur:
        size = os.stat(path).st_size

        # TODO: Hash from disk.
        with open(path, "rb") as file:
            buf = file.read()

        hashes = get_hashes(buf)
        file_sha256 = hashes["sha256"]

        possible_stored_file_hash_entry = search_sha256(conn, file_sha256)
        if possible_stored_file_hash_entry:
            stored_id = possible_stored_file_hash_entry["file_id"]
            print(f"File already exists, ID: {stored_id}")
            return stored_id

        upload_file(path, file_sha256)
        # Database writes should always be delayed to last.
        file_id = cur.execute("INSERT INTO files (size) VALUES (%s) RETURNING id", (size,)).fetchone()[0]
        for (algorithm, value) in hashes.items():
            cur.execute("INSERT INTO file_hashes (file_id, algorithm, value) VALUES (%s, %s, %s)", [
                file_id, algorithm, value
            ])
        conn.commit()

    return file_id
