import math
import re
import subprocess
import typing
import peutils
from helpers.directory import get_application_path
from application import string_analyzer
import pefile
import datetime
import hashlib
import os

with open(get_application_path("/peid_signatures/userdb.txt"), encoding="windows-1252") as file:
    peid_signatures = file.read()

signature_database = peutils.SignatureDatabase(data=peid_signatures)

def analyze_file(path: str):
    pe = pefile.PE(path)
    with open(path, "rb") as file:
        buf = file.read()

    out = {
        # Removed in the actual code.
        # "hashes": get_hashes(buf),
        # "size": get_size(path),
        # TODO: Shannon entropy is correct here, but what do we need to extract to match the PEStudio's output?
        "entropy": shannon_entropy(buf),
        "imphash": pe.get_imphash(),
        "file_info": get_fixed_file_info(pe),
        # TODO: Possibly retired (not important)
        # "dos_header": get_dos_header(pe),
        "file_header": get_file_header(pe),
        "optional_header": get_optional_header(pe),
        "imports": get_imports(pe),
        "exports": get_exports(pe),
        "resources": get_resources(pe),
        "sections": get_sections(pe),
        "strings": analyze_strings(path),
        "packers": get_packer_result(pe),
        # Missing: CAPA, Graph
    }

    pe.close()
    return out


def get_fixed_file_info(pe):
    entries = {}
    if hasattr(pe, "FileInfo"):
        for file_info_list in pe.FileInfo:
            for file_info in file_info_list:
                if file_info.Key == b'StringFileInfo':
                    for st in file_info.StringTable:
                        for _key, _value in st.entries.items():
                            key = _key.decode("UTF-8")
                            value = _value.decode("UTF-8")
                            entries[key] = value
    return {
        "company": entries.get("CompanyName"),
        "description": entries.get("FileDescription"),
        "version": entries.get("FileVersion"),
        "internal_name": entries.get("InternalName"),
        "copyright": entries.get("LegalCopyright"),
        "original_filename": entries.get("OriginalFilename"),
        "product_name": entries.get("ProductName"),
        "product_version": entries.get("ProductVersion"),
        "language_id": entries.get("LanguageId"),
    }


def analyze_strings(path):
    # TODO: Allows users to customize min characters
    strings_capture_proc = subprocess.Popen(["flarestrings", "-n", "5", path], stdout=subprocess.PIPE)
    strings_rank_proc = subprocess.Popen(["rank_strings", "-s"],
                                         stdin=strings_capture_proc.stdout,
                                         stdout=subprocess.PIPE, text=True)
    output, error = strings_rank_proc.communicate()

    line_data = []
    strings = output.split("\n")
    regex = re.compile(f"^(-?[0-9]*(.[0-9]+)?),(.*)$")
    for line in strings:
        line_contents = regex.findall(line)
        if line_contents:
            line_tuple = line_contents[0]
            line_data.append({
                "score": float(line_tuple[0]),
                "data": line_tuple[2],
                "analysis": string_analyzer.analyze_string(line_tuple[2]),
            })
    return line_data


def get_packer_result(pe: pefile.PE):
    arr = []

    matches = signature_database.match_all(pe, ep_only=True)
    if matches:
        for result in matches:
            for item in result:
                arr.append(item)

    return arr


def get_resources(pe: pefile.PE):
    results = []
    if not hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
        return results
    resource_data: pefile.ResourceDirData = pe.DIRECTORY_ENTRY_RESOURCE

    for res0 in resource_data.entries:
        for res1 in res0.directory.entries:
            name = None
            if res1.name:
                name = str(res1.name)
            elif res0.name:
                name = str(res0.name)

            for res2 in res1.directory.entries:
                lang = res2.data.lang
                sub = res2.data.sublang
                sub = pefile.get_sublang_name_for_lang(lang, sub)
                lang = pefile.LANG.get(lang, '')
                results.append({
                    'id': res1.id,
                    'name': name,
                    'language': {
                        'primary': lang.replace('LANG_', ''),
                        'sub': sub.replace('SUBLANG_', '')
                    },
                    'type': pefile.RESOURCE_TYPE.get(res0.id, "").replace('RT_', '') or None,
                    'offset': res2.data.struct.OffsetToData,
                    'size': res2.data.struct.Size,
                    'hashes': get_hashes(pe.get_data(res2.data.struct.OffsetToData, res2.data.struct.Size))
                })
    return results

def get_sections(pe: pefile.PE):
    res = []
    for section in pe.sections:
        res.append(get_section(section))
    return res


def get_section(section):
    pe: pefile.PE = section.pe
    out = {
        "virtual_size": section.Misc_VirtualSize,
        "virtual_address": section.VirtualAddress,
        "raw_size": section.SizeOfRawData,
        "raw_address": section.PointerToRawData,
        "name": section.Name.decode("UTF-8").strip("\x00"),
        "hashes": get_hashes(section.get_data()),
        "entropy": section.get_entropy(),
        "characteristics": parse_section_characteristics(section.Characteristics)
    }
    return out

def get_size(path: str):
    return os.stat(path).st_size


def get_dos_header(pe: pefile.PE):
    # print(pe.DOS_HEADER)
    pass

def get_file_header(pe: pefile.PE):
    file_header_dict = pe.FILE_HEADER.dump_dict()
    raw_timestamp = file_header_dict["TimeDateStamp"]["Value"]
    timestamp_hex = re.search(r"^0x[0-9a-f]+", raw_timestamp, flags=re.IGNORECASE)
    timestamp = datetime.datetime.fromtimestamp(int(timestamp_hex.group(), 16))

    return {
        "machine": pefile.MACHINE_TYPE[file_header_dict["Machine"]["Value"]],
        "compiled_at": timestamp,
        "sections": file_header_dict["NumberOfSections"]["Value"],
        "pointer_to_symbol_table": file_header_dict["PointerToSymbolTable"]["Value"],
        "number_of_symbols": file_header_dict["NumberOfSymbols"]["Value"],
        "size_of_optional_header": file_header_dict["SizeOfOptionalHeader"]["Value"],
        "characteristics": parse_file_header_characteristics(file_header_dict["Characteristics"]["Value"])
    }


def get_optional_header(pe: pefile.PE):
    def _get_attr(key, nullable=False):
        if nullable:
            return getattr(pe.OPTIONAL_HEADER, key, None)
        else:
            return getattr(pe.OPTIONAL_HEADER, key)

    return {
        "magic": _get_attr("Magic"),
        "major_linker_version": _get_attr("MajorLinkerVersion"),
        "minor_linker_version": _get_attr("MinorLinkerVersion"),
        "size_of_code": _get_attr("SizeOfCode"),
        "size_of_initialized_data": _get_attr("SizeOfInitializedData"),
        "size_of_uninitialized_data": _get_attr("SizeOfUninitializedData"),
        "address_of_entry_point": _get_attr("AddressOfEntryPoint"),
        "base_of_code": _get_attr("BaseOfCode"),
        "base_of_data": _get_attr("BaseOfData", nullable=True),
        "image_base": _get_attr("ImageBase"),
        "section_alignment": _get_attr("SectionAlignment"),
        "file_alignment": _get_attr("FileAlignment"),
        "major_operating_system_version": _get_attr("MajorOperatingSystemVersion"),
        "minor_operating_system_version": _get_attr("MinorOperatingSystemVersion"),
        "major_image_version": _get_attr("MajorImageVersion"),
        "minor_image_version": _get_attr("MinorImageVersion"),
        "major_subsystem_version": _get_attr("MajorSubsystemVersion"),
        "minor_subsystem_version": _get_attr("MinorSubsystemVersion"),
        "size_of_image": _get_attr("SizeOfImage"),
        "size_of_headers": _get_attr("SizeOfHeaders"),
        "checksum": _get_attr("CheckSum"),
        "subsystem": pefile.SUBSYSTEM_TYPE.get(_get_attr("Subsystem")),
        "size_of_stack_reserve": _get_attr("SizeOfStackReserve"),
        "size_of_stack_commit": _get_attr("SizeOfStackCommit"),
        "size_of_heap_reserve": _get_attr("SizeOfHeapReserve"),
        "size_of_heap_commit": _get_attr("SizeOfHeapCommit"),
        "loader_flags": _get_attr("LoaderFlags"),
        "number_of_rva_and_sizes": _get_attr("NumberOfRvaAndSizes"),
        "dll_characteristics": parse_optional_header_dll_characteristics(_get_attr("DllCharacteristics"))
    }


def parse_file_header_characteristics(characteristic_flag: int):
    bit_array = []
    for i in range(16):
        flag_enabled = bool((characteristic_flag >> i) & 1)
        bit_array.append(flag_enabled)
    return {
        "relocation_stripped": bit_array[0],
        "executable": bit_array[1],
        "coff_line_numbers_stripped": bit_array[2],
        "coff_local_symbol_table_stripped": bit_array[3],
        "aggressive_trim_working_set": bit_array[4],
        "large_address_aware": bit_array[5],
        "little_endian": bit_array[7],
        "32bit": bit_array[8],
        "debug_stripped": bit_array[9],
        "load_to_swap_if_on_removable_media": bit_array[10],
        "load_to_swap_if_on_network": bit_array[11],
        "system_image": bit_array[12],
        "dynamic_link_library": bit_array[13],
        "uniprocessor_only": bit_array[14],
        "big_endian": bit_array[15],
    }


def parse_section_characteristics(characteristic_flag: int):
    bit_array = []
    for i in range(32):
        flag_enabled = bool((characteristic_flag >> i) & 1)
        bit_array.append(flag_enabled)
    return {
        "object_file_pad_to_next_boundary": bit_array[3],
        "has_executable_code": bit_array[5],
        "has_initialized_data": bit_array[6],
        "has_uninitialized_data": bit_array[7],
        "object_file_section_contains_info": bit_array[9],
        "object_file_section_to_remove_from_image": bit_array[11],
        "object_file_section_includes_comdat": bit_array[12],
        "has_global_pointer_data": bit_array[15],
        "memory_purgeable": bit_array[16],
        "memory_16bit": bit_array[17],
        "memory_locked": bit_array[18],
        "memory_preload": bit_array[19],
        "object_file_alignment_bytes": 2 ** (
                int("".join(map(lambda x: str(int(x)), reversed(bit_array[20:24]))), 2) - 1),
        "contains_extended_relocations": bit_array[24],
        "discardable": bit_array[25],
        "cacheable": not bit_array[26],
        "pageable": not bit_array[27],
        "shareable": bit_array[28],
        "executable": bit_array[29],
        "readable": bit_array[30],
        "writeable": bit_array[31],
    }


def parse_optional_header_dll_characteristics(characteristic_flag: int):
    bit_array = []
    for i in range(16):
        flag_enabled = bool((characteristic_flag >> i) & 1)
        bit_array.append(flag_enabled)
    return {
        "high_entropy_virtual_address_space": bit_array[5],
        "dynamic_base": bit_array[6],
        "force_code_integrity": bit_array[7],
        "nx_compatible": bit_array[8],
        "no_isolation": bit_array[9],
        "no_structured_exception_handling": bit_array[10],
        "no_bind": bit_array[11],
        "force_app_container": bit_array[12],
        "wdm_driver": bit_array[13],
        "supports_control_flow_guard": bit_array[14],
        "terminal_server_aware": bit_array[15],
    }


def get_imports(pe: pefile.PE):
    results = []

    imp: pefile.ImportDescData
    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        for imp in pe.DIRECTORY_ENTRY_IMPORT:
            if hasattr(imp, "imports"):
                import_list: list[pefile.ImportData] = imp.imports
                for import_obj in import_list:
                    try:
                        obj = {
                            "name": import_obj.name.decode("ascii"),
                            "address": import_obj.address + pe.OPTIONAL_HEADER.ImageBase,
                        }
                        results.append(obj)
                    except AttributeError:
                        pass

    return results


def get_exports(pe: pefile.PE):
    results = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            try:
                obj = {
                    "name": exp.name.decode("ascii"),
                    "address": exp.address + pe.OPTIONAL_HEADER.ImageBase,
                    "ordinal": exp.ordinal,
                }
                results.append(obj)
            except AttributeError:
                continue
    return results


def get_hashes(buf: typing.Union[bytes, str]):
    return {
        "md5": hashlib.md5(buf).hexdigest(),
        "sha1": hashlib.sha1(buf).hexdigest(),
        "sha224": hashlib.sha224(buf).hexdigest(),
        "sha256": hashlib.sha256(buf).hexdigest(),
        "sha384": hashlib.sha384(buf).hexdigest(),
        "sha512": hashlib.sha512(buf).hexdigest(),
    }


def shannon_entropy(data):
    # 256 different possible values
    possible = dict(((chr(x), 0) for x in range(0, 256)))

    for byte in data:
        possible[chr(byte)] += 1

    data_len = len(data)
    entropy = 0.0

    # compute
    for i in possible:
        if possible[i] == 0:
            continue

        p = float(possible[i] / data_len)
        entropy -= p * math.log(p, 2)
    return entropy
