CREATE TABLE files
(
    "id"   SERIAL8 PRIMARY KEY,
    "size" BIGINT NOT NULL
);

CREATE TYPE ANALYSIS_STATE AS ENUM ('processing', 'complete');

CREATE TABLE file_hashes
(
    "id"        SERIAL8 PRIMARY KEY,
    "file_id"   BIGINT  NOT NULL,
    "algorithm" VARCHAR NOT NULL,
    "value"     VARCHAR NOT NULL,
    CONSTRAINT "file_id"
        FOREIGN KEY ("file_id") REFERENCES files ("id")
            ON DELETE CASCADE,
    UNIQUE ("file_id", "algorithm")
);

CREATE TABLE "analyses"
(
    "id"       SERIAL8 PRIMARY KEY,
    "file_id"  BIGINT         NOT NULL,
    "filename" VARCHAR        NOT NULL,
    "state"    ANALYSIS_STATE NOT NULL,
    CONSTRAINT "file_id"
        FOREIGN KEY ("file_id") REFERENCES files ("id")
            ON DELETE CASCADE
);

CREATE TABLE "basic_information"
(
    -- 1-1 relationship
    "analysis_id"       BIGINT PRIMARY KEY,
    "entropy"           FLOAT NOT NULL,
    "imphash"           VARCHAR,
    "company"           VARCHAR,
    "description"       VARCHAR,
    "version"           VARCHAR,
    "internal_name"     VARCHAR,
    "copyright"         VARCHAR,
    "original_filename" VARCHAR,
    "product_name"      VARCHAR,
    "product_version"   VARCHAR,
    "language_id"       VARCHAR,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE file_headers
(
    -- 1-1 relationship
    "analysis_id"             BIGINT PRIMARY KEY,
    "machine"                 VARCHAR   NOT NULL,
    "compiled_at"             TIMESTAMP NOT NULL,
    "sections"                INT       NOT NULL,
    "pointer_to_symbol_table" BIGINT    NOT NULL,
    "number_of_symbols"       BIGINT    NOT NULL,
    "size_of_optional_header" BIGINT    NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "file_header_characteristics"
(
    -- 1-1 relationship
    "analysis_id"                        BIGINT PRIMARY KEY,
    "relocation_stripped"                BOOLEAN NOT NULL,
    "executable"                         BOOLEAN NOT NULL,
    "coff_line_numbers_stripped"         BOOLEAN NOT NULL,
    "coff_local_symbol_table_stripped"   BOOLEAN NOT NULL,
    "aggressive_trim_working_set"        BOOLEAN NOT NULL,
    "large_address_aware"                BOOLEAN NOT NULL,
    "little_endian"                      BOOLEAN NOT NULL,
    "32bit"                              BOOLEAN NOT NULL,
    "debug_stripped"                     BOOLEAN NOT NULL,
    "load_to_swap_if_on_removable_media" BOOLEAN NOT NULL,
    "load_to_swap_if_on_network"         BOOLEAN NOT NULL,
    "system_image"                       BOOLEAN NOT NULL,
    "dynamic_link_library"               BOOLEAN NOT NULL,
    "uniprocessor_only"                  BOOLEAN NOT NULL,
    "big_endian"                         BOOLEAN NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE optional_headers
(
    -- 1-1 relationship
    "analysis_id"                    BIGINT PRIMARY KEY,
    "magic"                          INT     NOT NULL,
    "major_linker_version"           INT     NOT NULL,
    "minor_linker_version"           INT     NOT NULL,
    "size_of_code"                   BIGINT  NOT NULL,
    "size_of_initialized_data"       BIGINT  NOT NULL,
    "size_of_uninitialized_data"     BIGINT  NOT NULL,
    "address_of_entry_point"         BIGINT  NOT NULL,
    "base_of_code"                   BIGINT  NOT NULL,
    "base_of_data"                   BIGINT,
    "image_base"                     BIGINT  NOT NULL,
    "section_alignment"              BIGINT  NOT NULL,
    "file_alignment"                 BIGINT  NOT NULL,
    "major_operating_system_version" INT     NOT NULL,
    "minor_operating_system_version" INT     NOT NULL,
    "major_image_version"            INT     NOT NULL,
    "minor_image_version"            INT     NOT NULL,
    "major_subsystem_version"        INT     NOT NULL,
    "minor_subsystem_version"        INT     NOT NULL,
    "size_of_image"                  BIGINT  NOT NULL,
    "size_of_headers"                BIGINT  NOT NULL,
    "checksum"                       BIGINT  NOT NULL,
    "subsystem"                      VARCHAR NOT NULL,
    "size_of_stack_reserve"          BIGINT  NOT NULL,
    "size_of_stack_commit"           BIGINT  NOT NULL,
    "size_of_heap_reserve"           BIGINT  NOT NULL,
    "size_of_heap_commit"            BIGINT  NOT NULL,
    "loader_flags"                   INT     NOT NULL,
    "number_of_rva_and_sizes"        BIGINT  NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "optional_header_dll_characteristics"
(
    -- 1-1 relationship
    "analysis_id"                        BIGINT PRIMARY KEY,
    "high_entropy_virtual_address_space" BOOLEAN NOT NULL,
    "dynamic_base"                       BOOLEAN NOT NULL,
    "force_code_integrity"               BOOLEAN NOT NULL,
    "nx_compatible"                      BOOLEAN NOT NULL,
    "no_isolation"                       BOOLEAN NOT NULL,
    "no_structured_exception_handling"   BOOLEAN NOT NULL,
    "no_bind"                            BOOLEAN NOT NULL,
    "force_app_container"                BOOLEAN NOT NULL,
    "wdm_driver"                         BOOLEAN NOT NULL,
    "supports_control_flow_guard"        BOOLEAN NOT NULL,
    "terminal_server_aware"              BOOLEAN NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "imports"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT  NOT NULL,
    "name"        VARCHAR NOT NULL,
    "address"     BIGINT  NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "exports"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT  NOT NULL,
    "name"        VARCHAR NOT NULL,
    "address"     BIGINT  NOT NULL,
    "ordinal"     INT     NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "resources"
(
    "id"               SERIAL8 PRIMARY KEY,
    "analysis_id"      BIGINT  NOT NULL,
    "local_id"         INT     NOT NULL,
    "name"             VARCHAR,
    "primary_language" VARCHAR NOT NULL,
    "sub_language"     VARCHAR NOT NULL,
    "type"             VARCHAR,
    "offset"           BIGINT  NOT NULL,
    "size"             BIGINT  NOT NULL,

    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "resource_hashes"
(
    "id"          SERIAL8 PRIMARY KEY,
    "resource_id" BIGINT  NOT NULL,
    "algorithm"   VARCHAR NOT NULL,
    "value"       VARCHAR NOT NULL,
    CONSTRAINT "resource_id"
        FOREIGN KEY ("resource_id") REFERENCES resources ("id")
            ON DELETE CASCADE,
    UNIQUE ("resource_id", "algorithm")
);

CREATE TABLE "sections"
(
    "id"              SERIAL8 PRIMARY KEY,
    "analysis_id"     BIGINT  NOT NULL,
    "virtual_size"    BIGINT  NOT NULL,
    "virtual_address" BIGINT  NOT NULL,
    "raw_size"        BIGINT  NOT NULL,
    "raw_address"     BIGINT  NOT NULL,
    "name"            VARCHAR NOT NULL,
    "entropy"         FLOAT   NOT NULL,

    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES "analyses" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "section_hashes"
(
    "id"         SERIAL8 PRIMARY KEY,
    "section_id" BIGINT  NOT NULL,
    "algorithm"  VARCHAR NOT NULL,
    "value"      VARCHAR NOT NULL,
    CONSTRAINT "section_id"
        FOREIGN KEY ("section_id") REFERENCES sections ("id")
            ON DELETE CASCADE,
    UNIQUE ("section_id", "algorithm")
);

CREATE TABLE "section_characteristics"
(
    -- 1-1 relationship.
    "section_id"                               BIGINT PRIMARY KEY,
    "object_file_pad_to_next_boundary"         BOOLEAN NOT NULL,
    "has_executable_code"                      BOOLEAN NOT NULL,
    "has_initialized_data"                     BOOLEAN NOT NULL,
    "has_uninitialized_data"                   BOOLEAN NOT NULL,
    "object_file_section_contains_info"        BOOLEAN NOT NULL,
    "object_file_section_to_remove_from_image" BOOLEAN NOT NULL,
    "object_file_section_includes_comdat"      BOOLEAN NOT NULL,
    "has_global_pointer_data"                  BOOLEAN NOT NULL,
    "memory_purgeable"                         BOOLEAN NOT NULL,
    "memory_16bit"                             BOOLEAN NOT NULL,
    "memory_locked"                            BOOLEAN NOT NULL,
    "memory_preload"                           BOOLEAN NOT NULL,
    "object_file_alignment_bytes"              INT     NOT NULL,
    "contains_extended_relocations"            BOOLEAN NOT NULL,
    "discardable"                              BOOLEAN NOT NULL,
    "cacheable"                                BOOLEAN NOT NULL,
    "pageable"                                 BOOLEAN NOT NULL,
    "shareable"                                BOOLEAN NOT NULL,
    "executable"                               BOOLEAN NOT NULL,
    "readable"                                 BOOLEAN NOT NULL,
    "writeable"                                BOOLEAN NOT NULL,
    CONSTRAINT "section_id"
        FOREIGN KEY ("section_id") REFERENCES sections ("id")
            ON DELETE CASCADE
);

CREATE TABLE "strings"
(
    "id"          SERIAL8 PRIMARY KEY,
    "analysis_id" BIGINT NOT NULL,
    "score"       FLOAT,
    "data"        VARCHAR,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES analyses ("id")
            ON DELETE CASCADE
);

CREATE TABLE "string_tags"
(
    "id"        SERIAL8 PRIMARY KEY,
    "string_id" BIGINT NOT NULL,
    "tag"       VARCHAR,
    CONSTRAINT "string_id"
        FOREIGN KEY ("string_id") REFERENCES strings ("id")
            ON DELETE CASCADE
);

CREATE TABLE "string_matches"
(
    "id"         SERIAL8 PRIMARY KEY,
    "string_id"  BIGINT NOT NULL,
    "start"      INT,
    "end"        INT,
    "definition" VARCHAR,
    CONSTRAINT "string_id"
        FOREIGN KEY ("string_id") REFERENCES strings ("id")
            ON DELETE CASCADE
);


CREATE TABLE "capa_entries"
(
    "id"             SERIAL8 PRIMARY KEY,
    "analysis_id"    BIGINT  NOT NULL,
    "rule_name"      varchar NOT NULL,
    "rule_namespace" varchar NOT NULL,
    "rule_scope"     varchar NOT NULL,
    CONSTRAINT "analysis_id"
        FOREIGN KEY ("analysis_id") REFERENCES analyses ("id")
            ON DELETE CASCADE
);

CREATE TYPE LOCATION_TYPE AS ENUM ('absolute');

CREATE TABLE "capa_matches"
(
    "id"             SERIAL8 PRIMARY KEY,
    "capa_entry_id"  BIGINT        NOT NULL,
    "location_type"  LOCATION_TYPE NOT NULL,
    "location_value" BIGINT        NOT NULL,
    CONSTRAINT "capa_entry_id"
        FOREIGN KEY ("capa_entry_id") REFERENCES "capa_entries" ("id")
            ON DELETE CASCADE
);

CREATE TYPE CAPA_NODE_TYPE AS ENUM ('feature', 'statement');

CREATE TABLE "capa_nodes"
(
    "id"             SERIAL8 PRIMARY KEY,
    -- Easy reference to match_id. Allows removing all at once once analysis object is deleted, and allow the frontend
    -- to do the heavy work of reconstructing the node tree.
    "capa_match_id"  BIGINT         NOT NULL,
    -- root node has this attribute set to null.
    "parent_node_id" BIGINT,
    "success"        BOOLEAN        NOT NULL,
    "type"           CAPA_NODE_TYPE NOT NULL,
    -- combination of "subtype" and "type"
    "subtype"        varchar        NOT NULL,
    -- in case the type is "feature", otherwise null
    "feature_data"   VARCHAR,
    CONSTRAINT "capa_match_id"
        FOREIGN KEY ("capa_match_id") REFERENCES "capa_matches" ("id")
            ON DELETE CASCADE,
    CONSTRAINT "parent_node_id"
        FOREIGN KEY ("parent_node_id") REFERENCES "capa_nodes" ("id")
            ON DELETE CASCADE
);

CREATE TABLE "capa_node_locations"
(
    "id"             SERIAL8 PRIMARY KEY,
    "capa_node_id"   BIGINT        NOT NULL,
    "location_type"  LOCATION_TYPE NOT NULL,
    "location_value" BIGINT        NOT NULL,
    CONSTRAINT "capa_node_id"
        FOREIGN KEY ("capa_node_id") REFERENCES "capa_entries" ("id")
            ON DELETE CASCADE
);
