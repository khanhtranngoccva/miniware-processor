import psycopg
from psycopg import sql, rows


def insert_strings(conn: psycopg.Connection, analysis_id, strings):
    with conn.cursor(row_factory=rows.dict_row) as cur:
        insert_string_args = []
        single_row = sql.SQL("({0})").format(sql.SQL(", ").join(sql.Placeholder() * 4))
        parameters = sql.SQL(", ").join(single_row * len(strings))
        unfilled_query = sql.SQL(
            "INSERT INTO strings (analysis_id, local_order, score, data) VALUES {parameters} RETURNING local_order, id")
        query = unfilled_query.format(parameters=parameters)
        for local_order, string in enumerate(strings):
            insert_string_args.extend([analysis_id, local_order, string["score"], string["data"]])
        id_bindings = cur.execute(query, insert_string_args).fetchall()

        with cur.copy("COPY string_tags (string_id, tag) FROM STDIN") as copy_tags:
            for binding in id_bindings:
                index = binding["local_order"]
                database_string_id = binding["id"]
                target_string = strings[index]
                for tag in target_string["analysis"]["tags"]:
                    copy_tags.write_row([database_string_id, tag])
        with cur.copy('COPY string_matches (string_id, start, "end", definition) FROM STDIN') as copy_matches:
            for binding in id_bindings:
                index = binding["local_order"]
                database_string_id = binding["id"]
                target_string = strings[index]
                for match in target_string["analysis"]["matches"]:
                    start, end = match["match"]
                    definition_name = match["definition"]
                    copy_matches.write_row([database_string_id, start, end, definition_name])
