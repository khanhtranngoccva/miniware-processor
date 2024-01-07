CREATE OR REPLACE VIEW full_analyses AS
SELECT analyses.*,
       TO_JSON(basic_information)                                                 basic_information,
       TO_JSON(file_headers)                                                      file_header,
       TO_JSON(optional_headers)                                                  optional_header,
       COALESCE(TO_JSON(imports.import_data), TO_JSON(ARRAY []::record[]))     AS imports,
       COALESCE(TO_JSON(exports.export_data), TO_JSON(ARRAY []::record[]))     AS exports,
       COALESCE(TO_JSON(resources.resource_data), TO_JSON(ARRAY []::record[])) AS resources,
       COALESCE(TO_JSON(strings.strings_data), TO_JSON(ARRAY []::record[]))    AS strings,
       COALESCE(TO_JSON(sections.section_data), TO_JSON(ARRAY []::record[]))   AS sections
FROM analyses
-- basic information
         INNER JOIN basic_information ON analyses.id = basic_information.analysis_id
-- file header and characteristics
         INNER JOIN (SELECT file_headers.*, TO_JSON(characteristics) characteristics
                     FROM file_headers
                              INNER JOIN file_header_characteristics "characteristics"
                                         ON "characteristics".analysis_id = "file_headers".analysis_id) file_headers
                    ON analyses.id = file_headers.analysis_id
-- optional header and characteristics
         INNER JOIN (SELECT optional_headers.*, TO_JSON(characteristics) dll_characteristics
                     FROM optional_headers
                              INNER JOIN optional_header_dll_characteristics "characteristics"
                                         ON "characteristics".analysis_id = "optional_headers".analysis_id) optional_headers
                    ON analyses.id = optional_headers.analysis_id
-- imports
         LEFT JOIN (SELECT analysis_id, ARRAY_AGG(imports) AS import_data
                    FROM imports
                    GROUP BY analysis_id) imports ON imports.analysis_id = analyses.id
-- exports
         LEFT JOIN (SELECT analysis_id, ARRAY_AGG(exports) AS export_data
                    FROM exports
                    GROUP BY analysis_id) exports ON exports.analysis_id = analyses.id
-- resources
         LEFT JOIN (SELECT analysis_id, ARRAY_AGG(resources) AS resource_data
                    FROM (SELECT resources.*, TO_JSON("resource_hashes") AS "hashes"
                          FROM resources
                                   INNER JOIN resource_hashes ON resources.id = resource_hashes.resource_id) resources
                    GROUP BY analysis_id) resources ON resources.analysis_id = analyses.id
-- strings
         LEFT JOIN (SELECT analysis_id, ARRAY_AGG(strings) AS strings_data
                    FROM (SELECT strings.*,
                                 TO_JSON(ARRAY_REMOVE(ARRAY_AGG(string_tags), NULL))    AS "tags",
                                 TO_JSON(ARRAY_REMOVE(ARRAY_AGG(string_matches), NULL)) AS "matches"
                          FROM strings
                                   LEFT JOIN (SELECT string_id, ARRAY_AGG(string_tags)
                                              FROM string_tags
                                              GROUP BY string_id) string_tags
                                             ON strings.id = string_tags.string_id
                                   LEFT JOIN (SELECT string_id, ARRAY_AGG(string_matches)
                                              FROM string_matches
                                              GROUP BY string_id) string_matches
                                             ON strings.id = string_matches.string_id
                          GROUP BY strings.id) strings
                    GROUP BY analysis_id) strings ON strings.analysis_id = analyses.id
-- sections
         LEFT JOIN (SELECT analysis_id, TO_JSON(ARRAY_AGG(sections)) AS section_data
                    FROM (SELECT sections.*, ARRAY_REMOVE(ARRAY_AGG(section_hashes), NULL) AS hashes
                          FROM sections
                                   LEFT JOIN section_hashes ON sections.id = section_hashes.section_id
                          GROUP BY sections.id) sections
                    GROUP BY analysis_id) sections ON sections.analysis_id = analyses.id
WHERE state = 'complete';


SELECT *
FROM full_analyses
WHERE id = 5