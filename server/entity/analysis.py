import pprint

import server.entity.strings
from helpers import errors
import psycopg.rows
import pefile_processor


def create_analysis(conn, file_id: int, filename: str):
    with conn.cursor() as cur:
        analysis_id = cur.execute("INSERT INTO analyses (file_id, filename, state) "
                                  "VALUES (%s, %s, %s) RETURNING id", [
                                      file_id, filename, "processing"
                                  ]).fetchone()[0]
        conn.commit()
    return analysis_id


def get_complete_analysis(conn, analysis_id: int):
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        query = "SELECT * FROM full_analyses WHERE id = %s"
        analysis = cur.execute(query, [analysis_id]).fetchone()

        if analysis is None:
            fallback = cur.execute("SELECT * FROM analyses WHERE id = %s", [analysis_id]).fetchone()
            if fallback is None:
                raise errors.NotFoundError
            else:
                raise errors.ResourceNotReadyError

    return analysis


def initiate_analysis(conn, analysis_id: int, file_path: str):
    output = pefile_processor.analyze_file(file_path)

    with conn.cursor() as cur:
        file_info = output["file_info"]
        cur.execute(
            "INSERT INTO basic_information ("
            "analysis_id, entropy, imphash, company, "
            "description, version, internal_name, copyright, "
            "original_filename, product_name, product_version, language_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                analysis_id, output["entropy"], output["imphash"], file_info["company"],
                file_info["description"], file_info["version"],
                file_info["internal_name"], file_info["copyright"],
                file_info["original_filename"], file_info["product_name"],
                file_info["product_version"], file_info["language_id"]
            ])

        file_header = output["file_header"]
        cur.execute(
            "INSERT INTO file_headers ("
            "analysis_id, machine, compiled_at, sections, "
            "pointer_to_symbol_table, number_of_symbols, size_of_optional_header) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [
                analysis_id, file_header["machine"],
                file_header["compiled_at"], file_header["sections"],
                file_header["pointer_to_symbol_table"], file_header["number_of_symbols"],
                file_header["size_of_optional_header"]
            ])

        file_header_characteristics = file_header["characteristics"]
        cur.execute(
            "INSERT INTO file_header_characteristics ("
            "analysis_id, relocation_stripped, executable, "
            "coff_line_numbers_stripped, coff_local_symbol_table_stripped, aggressive_trim_working_set, "
            "large_address_aware, little_endian, \"32bit\", "
            "debug_stripped, load_to_swap_if_on_removable_media, load_to_swap_if_on_network, "
            "system_image, dynamic_link_library, uniprocessor_only, "
            "big_endian) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                analysis_id, file_header_characteristics["relocation_stripped"],
                file_header_characteristics["executable"], file_header_characteristics["coff_line_numbers_stripped"],
                file_header_characteristics["coff_local_symbol_table_stripped"],
                file_header_characteristics["aggressive_trim_working_set"],
                file_header_characteristics["large_address_aware"], file_header_characteristics["little_endian"],
                file_header_characteristics["32bit"], file_header_characteristics["debug_stripped"],
                file_header_characteristics["load_to_swap_if_on_removable_media"],
                file_header_characteristics["load_to_swap_if_on_network"], file_header_characteristics["system_image"],
                file_header_characteristics["dynamic_link_library"],
                file_header_characteristics["uniprocessor_only"], file_header_characteristics["big_endian"],
            ])

        optional_header = output["optional_header"]
        cur.execute(
            "INSERT INTO optional_headers ("
            "analysis_id, magic, major_linker_version, "
            "minor_linker_version, size_of_code, size_of_initialized_data, "
            "size_of_uninitialized_data, address_of_entry_point, base_of_code, "
            "base_of_data, image_base, section_alignment, "
            "file_alignment, major_operating_system_version, minor_operating_system_version, "
            "major_image_version, minor_image_version, major_subsystem_version, "
            "minor_subsystem_version, size_of_image, size_of_headers, "
            "checksum, subsystem, size_of_stack_reserve, "
            "size_of_stack_commit, size_of_heap_reserve, size_of_heap_commit, "
            "loader_flags, number_of_rva_and_sizes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                analysis_id, optional_header["magic"], optional_header["major_linker_version"],
                optional_header["minor_linker_version"], optional_header["size_of_code"],
                optional_header["size_of_initialized_data"],
                optional_header["size_of_uninitialized_data"], optional_header["address_of_entry_point"],
                optional_header["base_of_code"],
                optional_header["base_of_data"], optional_header["image_base"], optional_header["section_alignment"],
                optional_header["file_alignment"], optional_header["major_operating_system_version"],
                optional_header["minor_operating_system_version"],
                optional_header["major_image_version"], optional_header["minor_image_version"],
                optional_header["major_subsystem_version"],
                optional_header["minor_subsystem_version"], optional_header["size_of_image"],
                optional_header["size_of_headers"],
                optional_header["checksum"], optional_header["subsystem"], optional_header["size_of_stack_reserve"],
                optional_header["size_of_stack_commit"], optional_header["size_of_heap_reserve"],
                optional_header["size_of_heap_commit"],
                optional_header["loader_flags"], optional_header["number_of_rva_and_sizes"]
            ]
        )

        optional_header_dll_characteristics = optional_header["dll_characteristics"]
        cur.execute(
            "INSERT INTO optional_header_dll_characteristics ("
            "analysis_id, high_entropy_virtual_address_space, dynamic_base, "
            "force_code_integrity, nx_compatible, no_isolation, "
            "no_structured_exception_handling, no_bind, force_app_container, "
            "wdm_driver, supports_control_flow_guard, terminal_server_aware) VALUES ("
            "%s, %s, %s,"
            "%s, %s, %s,"
            "%s, %s, %s,"
            "%s, %s, %s)",
            [
                analysis_id, optional_header_dll_characteristics["high_entropy_virtual_address_space"],
                optional_header_dll_characteristics["dynamic_base"],
                optional_header_dll_characteristics["force_code_integrity"],
                optional_header_dll_characteristics["nx_compatible"],
                optional_header_dll_characteristics["no_isolation"],
                optional_header_dll_characteristics["no_structured_exception_handling"],
                optional_header_dll_characteristics["no_bind"],
                optional_header_dll_characteristics["force_app_container"],
                optional_header_dll_characteristics["wdm_driver"],
                optional_header_dll_characteristics["supports_control_flow_guard"],
                optional_header_dll_characteristics["terminal_server_aware"]
            ]
        )

        imports = output["imports"]
        for import_obj in imports:
            cur.execute("INSERT INTO imports (analysis_id, name, address) VALUES (%s, %s, %s)", [
                analysis_id, import_obj["name"], import_obj["address"]
            ])

        exports = output["exports"]
        for export_obj in exports:
            cur.execute("INSERT INTO exports (analysis_id, name, address, ordinal) VALUES (%s, %s, %s, %s)", [
                analysis_id, export_obj["name"], export_obj["address"], export_obj["ordinal"]
            ])

        resources = output["resources"]
        for resource in resources:
            resource_id = cur.execute(
                "INSERT INTO resources (analysis_id, local_id, name, primary_language, sub_language, type, \"offset\", size) VALUES "
                "(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", [
                    analysis_id, resource["id"], resource["name"], resource["language"]["primary"],
                    resource["language"]["sub"], resource["type"], resource["offset"], resource["size"],
                ]).fetchone()[0]

            for (algorithm, value) in resource["hashes"].items():
                cur.execute("INSERT INTO resource_hashes (resource_id, algorithm, value) VALUES (%s, %s, %s)", [
                    resource_id, algorithm, value
                ])

        sections = output["sections"]
        for section in sections:
            section_id = cur.execute(
                "INSERT INTO sections (analysis_id, virtual_size, virtual_address, raw_size, raw_address, name, entropy) VALUES "
                "(%s, %s, %s, %s, %s, %s, %s) RETURNING id", [
                    analysis_id, section["virtual_size"], section["virtual_address"], section["raw_size"],
                    section["raw_address"],
                    section["name"], section["entropy"]
                ]).fetchone()[0]

            for (algorithm, value) in section["hashes"].items():
                cur.execute("INSERT INTO section_hashes (section_id, algorithm, value) VALUES (%s, %s, %s)", [
                    section_id, algorithm, value
                ])

            section_characteristics = section["characteristics"]
            cur.execute(
                "INSERT INTO section_characteristics ("
                "section_id, object_file_pad_to_next_boundary, has_executable_code, "
                "has_initialized_data, has_uninitialized_data, object_file_section_contains_info, "
                "object_file_section_to_remove_from_image, object_file_section_includes_comdat, has_global_pointer_data,"
                "memory_purgeable, memory_16bit, memory_locked, "
                "memory_preload, object_file_alignment_bytes, contains_extended_relocations, "
                "discardable, cacheable, pageable, "
                "shareable, executable, readable,"
                "writeable) VALUES ("
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s, %s, %s,"
                "%s"
                ")", [
                    section_id, section_characteristics["object_file_pad_to_next_boundary"],
                    section_characteristics["has_executable_code"],
                    section_characteristics["has_initialized_data"], section_characteristics["has_uninitialized_data"],
                    section_characteristics["object_file_section_contains_info"],
                    section_characteristics["object_file_section_to_remove_from_image"],
                    section_characteristics["object_file_section_includes_comdat"],
                    section_characteristics["has_global_pointer_data"],
                    section_characteristics["memory_purgeable"], section_characteristics["memory_16bit"],
                    section_characteristics["memory_locked"],
                    section_characteristics["memory_preload"], section_characteristics["object_file_alignment_bytes"],
                    section_characteristics["contains_extended_relocations"],
                    section_characteristics["discardable"], section_characteristics["cacheable"],
                    section_characteristics["pageable"],
                    section_characteristics["shareable"], section_characteristics["executable"],
                    section_characteristics["readable"],
                    section_characteristics["writeable"],
                ])

        strings = output["strings"]
        server.entity.strings.insert_strings(conn,
                                             analysis_id=analysis_id,
                                             strings=strings)
        # for string in strings:
        #     string_id = cur.execute(
        #         "INSERT INTO strings (analysis_id, score, data) VALUES (%s, %s, %s) RETURNING id",
        #         [analysis_id, string["score"], string["data"]]
        #     ).fetchone()[0]
        #
        #     string_analysis = string["analysis"]
        #     string_tags = string_analysis["tags"]
        #     string_matches = string_analysis["matches"]
        #
        #     for tag in string_tags:
        #         cur.execute("INSERT INTO string_tags (string_id, tag) VALUES (%s, %s)", [
        #             string_id, tag
        #         ])
        #
        #     for match in string_matches:
        #         match_start, match_end = match["match"]
        #         match_definition = match["definition"]
        #
        #         cur.execute(
        #             "INSERT INTO string_matches (string_id, start, \"end\", definition) VALUES (%s, %s, %s, %s)", [
        #                 string_id, match_start, match_end, match_definition
        #             ])

        complete_analysis(conn, analysis_id)


def complete_analysis(conn, analysis_id: int):
    with conn.cursor() as cur:
        cur.execute("UPDATE analyses SET state = 'complete' WHERE id = %s", [
            analysis_id
        ])
        conn.commit()
