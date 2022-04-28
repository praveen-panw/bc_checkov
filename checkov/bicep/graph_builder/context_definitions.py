from pathlib import Path
from typing import cast, List, Tuple, Dict, Any

from checkov.common.util.suppression import collect_suppressions_for_report

from pycep.typing import BicepJson


BICEP_COMMENT = "//"
DEFINITIONS_KEY_TO_PARSE = {"parameters": "parameters", "resources": "resources"}


def build_definitions_context(
        definitions: Dict[Path, BicepJson], definitions_raw: Dict[Path, List[Tuple[int, str]]]
) -> Dict[str, Dict[str, Any]]:
    definitions_context: Dict[str, Dict[str, Any]] = {}
    for file_path_object, file_path_definitions in definitions.items():
        file_path = str(file_path_object)
        definitions_context[file_path] = {}
        for definition_attribute, resources in file_path_definitions.items():
            if definition_attribute not in DEFINITIONS_KEY_TO_PARSE.values():
                continue
            definitions_context[file_path][definition_attribute] = {}
            for resource_key, resource_attributes in resources.items():
                definition_resource = {}

                definition_resource["start_line"] = resource_attributes["__start_line__"]
                definition_resource["end_line"] = resource_attributes["__end_line__"]

                if definition_attribute == DEFINITIONS_KEY_TO_PARSE["resources"]:
                    definition_key = f"{resource_attributes['type']}.{resource_key}"
                    int_start_line = cast(int, definition_resource["start_line"])
                    int_end_line = cast(int, definition_resource["end_line"])
                    code_lines_for_suppressions_check = definitions_raw[file_path_object][int_start_line: int_end_line]
                    supressions = collect_suppressions_for_report(code_lines=code_lines_for_suppressions_check)
                    skipped_checks = [result for result in supressions.items()]
                    definition_resource['skipped_checks'] = skipped_checks
                if definition_attribute == DEFINITIONS_KEY_TO_PARSE["parameters"]:
                    definition_key = resource_key
                    definition_resource["type"] = resource_attributes['type']

                start_line = resource_attributes["__start_line__"]
                end_line = min(resource_attributes["__end_line__"], len(definitions_raw[file_path_object]))
                first_line_index = 0
                # skip empty lines
                while not str.strip(definitions_raw[file_path_object][first_line_index][1]):
                    first_line_index += 1

                # check if the file is a json file
                if str.strip(definitions_raw[file_path_object][first_line_index][1])[0] == "{":
                    start_line += 1
                    end_line += 1
                else:
                    # add resource comments to definition lines
                    current_line = str.strip(definitions_raw[file_path_object][start_line - 1][1])
                    while not current_line or current_line[0] == BICEP_COMMENT:
                        start_line -= 1
                        current_line = str.strip(definitions_raw[file_path_object][start_line - 1][1])

                    # remove next resource comments from definition lines
                    current_line = str.strip(definitions_raw[file_path_object][end_line - 1][1])
                    while not current_line or current_line[0] == BICEP_COMMENT:
                        end_line -= 1
                        current_line = str.strip(definitions_raw[file_path_object][end_line - 1][1])

                definition_resource["code_lines"] = definitions_raw[file_path_object][start_line - 1: end_line]
                definitions_context[file_path][definition_attribute][definition_key] = definition_resource

        return definitions_context
