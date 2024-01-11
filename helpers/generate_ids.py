from server.database import db_connect


def generate_insert_operation_id():
    with db_connect() as conn:
        with conn.cursor() as cur:
            new_id = cur.execute('INSERT INTO "_insert_operation_ids" DEFAULT VALUES RETURNING id;').fetchone()[0]
        conn.commit()
    return new_id


if __name__ == '__main__':
    print(generate_insert_operation_id())
