import psycopg
from psycopg import sql, rows


def insert_strings(conn: psycopg.Connection, analysis_id, strings):
    with conn.cursor(row_factory=rows.dict_row) as cur:
        with cur.copy("COPY strings (analysis_id, local_order, score, data) FROM stdin") as copy_strings:
            for local_order, string in enumerate(strings):
                copy_strings.write_row([analysis_id, local_order, string["score"], string["data"]])
        id_bindings = cur.execute("SELECT id, local_order FROM strings WHERE analysis_id = %s",
                                  [analysis_id]).fetchall()

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
