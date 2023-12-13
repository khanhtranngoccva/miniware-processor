CREATE TABLE files
(
    "id"   SERIAL8 PRIMARY KEY,
    "size" BIGINT
);

CREATE TYPE ANALYSIS_STATE AS ENUM ('processing', 'complete');

CREATE TABLE file_hashes
(
    "id"        SERIAL8 PRIMARY KEY,
    "file_id"   BIGINT,
    "algorithm" VARCHAR,
    "value"     VARCHAR,
    CONSTRAINT "file_id"
        FOREIGN KEY ("file_id") REFERENCES files ("id")
            ON DELETE CASCADE,
    UNIQUE ("file_id", "algorithm")
);

CREATE TABLE "analyses"
(
    "id"       SERIAL8 PRIMARY KEY,
    "file_id"  BIGINT,
    "filename" VARCHAR,
    "state"    ANALYSIS_STATE,
    CONSTRAINT "file_id"
        FOREIGN KEY ("file_id") REFERENCES files ("id")
            ON DELETE CASCADE
);

CREATE TABLE "basic_information"
(
    -- 1-1 relationship
    "analysis_id" BIGINT PRIMARY KEY,
    "entropy"     FLOAT,
    "isPacked"    BOOLEAN,
    "impHash"     VARCHAR,
    "version"     VARCHAR,
    "description" VARCHAR,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE file_headers
(
    -- 1-1 relationship
    "analysis_id"             BIGINT PRIMARY KEY,
    "machine"                 VARCHAR,
    "compiled_at"             TIMESTAMP,
    "sections"                INT,
    "pointer_to_symbol_table" BIGINT,
    "number_of_symbols"       BIGINT,
    "size_of_optional_header" BIGINT,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "file_header_characteristics"
(
    -- 1-1 relationship
    "analysis_id"                        BIGINT PRIMARY KEY,
    "relocation_stripped"                BOOLEAN,
    "executable"                         BOOLEAN,
    "coff_line_numbers_stripped"         BOOLEAN,
    "coff_local_symbol_table_stripped"   BOOLEAN,
    "aggressive_trim_working_set"        BOOLEAN,
    "large_address_aware"                BOOLEAN,
    "little_endian"                      BOOLEAN,
    "32bit"                              BOOLEAN,
    "debug_stripped"                     BOOLEAN,
    "load_to_swap_if_on_removable_media" BOOLEAN,
    "load_to_swap_if_on_network"         BOOLEAN,
    "system_image"                       BOOLEAN,
    "dynamic_link_library"               BOOLEAN,
    "uniprocessor_only"                  BOOLEAN,
    "big_endian"                         BOOLEAN,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE optional_headers
(
    -- 1-1 relationship
    "analysis_id"                    BIGINT PRIMARY KEY,
    "magic"                          INT,
    "major_linker_version"           INT,
    "minor_linker_version"           INT,
    "size_of_code"                   BIGINT,
    "size_of_initialized_data"       BIGINT,
    "size_of_uninitialized_data"     BIGINT,
    "address_of_entry_point"         BIGINT,
    "base_of_code"                   BIGINT,
    "base_of_data"                   BIGINT,
    "image_base"                     BIGINT,
    "section_alignment"              BIGINT,
    "file_alignment"                 BIGINT,
    "major_operating_system_version" INT,
    "minor_operating_system_version" INT,
    "major_image_version"            INT,
    "minor_image_version"            INT,
    "major_subsystem_version"        INT,
    "minor_subsystem_version"        INT,
    "size_of_image"                  BIGINT,
    "size_of_headers"                BIGINT,
    "checksum"                       BIGINT,
    "subsystem"                      VARCHAR,
    "size_of_stack_reserve"          BIGINT,
    "size_of_stack_commit"           BIGINT,
    "size_of_heap_reserve"           BIGINT,
    "size_of_heap_commit"            BIGINT,
    "loader_flags"                   INT,
    "number_of_rva_and_sizes"        BIGINT,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "optional_header_dll_characteristics"
(
    -- 1-1 relationship
    "analysis_id"                        BIGINT PRIMARY KEY,
    "high_entropy_virtual_address_space" BOOLEAN,
    "dynamic_base"                       BOOLEAN,
    "force_code_integrity"               BOOLEAN,
    "nx_compatible"                      BOOLEAN,
    "no_isolation"                       BOOLEAN,
    "no_structured_exception_handling"   BOOLEAN,
    "no_bind"                            BOOLEAN,
    "force_app_container"                BOOLEAN,
    "wdm_driver"                         BOOLEAN,
    "supports_control_flow_guard"        BOOLEAN,
    "terminal_server_aware"              BOOLEAN,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "imports"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT,
    "name"        VARCHAR,
    "address"     BIGINT,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "exports"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT,
    "name"        VARCHAR,
    "address"     BIGINT,
    "ordinal"     INT,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "resources"
(
    "id"               SERIAL8 PRIMARY KEY,
    "analysis_id"      BIGINT,
    "local_id"         INT,
    "name"             VARCHAR,
    "primary_language" VARCHAR,
    "sub_language"     VARCHAR,

    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "sections"
(
    "id"              SERIAL8 PRIMARY KEY,
    "analysis_id"     BIGINT,
    "virtual_size"    BIGINT,
    "virtual_address" BIGINT,
    "raw_size"        BIGINT,
    "raw_address"     BIGINT,
    "name"            VARCHAR,
    "entropy"         FLOAT,

    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "section_hashes"
(
    "id"         SERIAL8 PRIMARY KEY,
    "section_id" BIGINT,
    "algorithm"  VARCHAR,
    "value"      VARCHAR,
    CONSTRAINT "section_id"
        FOREIGN KEY ("section_id") REFERENCES sections ("id")
            ON DELETE CASCADE,
    UNIQUE ("section_id", "algorithm")
);

CREATE TABLE "section_characteristics"
(
    -- 1-1 relationship.
    "section_id"                               BIGINT PRIMARY KEY,
    "object_file_pad_to_next_boundary"         BOOLEAN,
    "has_executable_code"                      BOOLEAN,
    "has_initialized_data"                     BOOLEAN,
    "has_uninitialized_data"                   BOOLEAN,
    "object_file_section_contains_info"        BOOLEAN,
    "object_file_section_to_remove_from_image" BOOLEAN,
    "object_file_section_includes_comdat"      BOOLEAN,
    "has_global_pointer_data"                  BOOLEAN,
    "memory_purgeable"                         BOOLEAN,
    "memory_16bit"                             BOOLEAN,
    "memory_locked"                            BOOLEAN,
    "memory_preload"                           BOOLEAN,
    "object_file_alignment_bytes"              INT,
    "contains_extended_relocations"            BOOLEAN,
    "discardable"                              BOOLEAN,
    "cacheable"                                BOOLEAN,
    "pageable"                                 BOOLEAN,
    "shareable"                                BOOLEAN,
    "executable"                               BOOLEAN,
    "readable"                                 BOOLEAN,
    "writeable"                                BOOLEAN,
    CONSTRAINT "section_id"
        FOREIGN KEY ("section_id") REFERENCES sections ("id")
            ON DELETE CASCADE
);

CREATE TABLE "strings"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT,
    "score"       FLOAT,
    "data"        VARCHAR,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES analyses ("id")
            ON DELETE CASCADE
);

CREATE TABLE "string_tags"
(
    "id"        SERIAL8 PRIMARY KEY,
    "string_id" BIGINT,
    "tag"       VARCHAR,
    CONSTRAINT "string_id"
        FOREIGN KEY ("string_id") REFERENCES strings ("id")
            ON DELETE CASCADE
);

CREATE TABLE "string_matches"
(
    "id"         SERIAL8 PRIMARY KEY,
    "string_id"  BIGINT,
    "match"      VARCHAR,
    "definition" VARCHAR,
    CONSTRAINT "string_id"
        FOREIGN KEY ("string_id") REFERENCES strings ("id")
            ON DELETE CASCADE
);