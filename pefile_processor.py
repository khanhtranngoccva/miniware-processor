import math
import re
import subprocess
import typing
import string_analyzer
import pefile
import datetime
import hashlib
import os


def analyze_file(path: str):
    pe = pefile.PE(path)
    with open(path, "rb") as file:
        buf = file.read()
    return {
        "hashes": get_hashes(buf),
        "size": get_size(path),
        # TODO: Shannon entropy is correct here, but what do we need to extract to match the PEStudio's output?
        "entropy": shannon_entropy(buf),
        # TODO
        "dos_header": get_dos_header(pe),
        "file_header": get_file_header(pe),
        "optional_header": get_optional_header(pe),
        "imports": get_imports(pe),
        # TODO: Verify this, should be tested with a DLL file
        "exports": get_exports(pe),
        "resources": get_resources(pe),
        "sections": get_sections(pe),
        "strings": analyze_strings(path),
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


def get_resources(pe: pefile.PE):
    results = []
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
    optional_header_dict = pe.OPTIONAL_HEADER.dump_dict()
    return {
        "magic": optional_header_dict["Magic"]["Value"],
        "major_linker_version": optional_header_dict["MajorLinkerVersion"]["Value"],
        "minor_linker_version": optional_header_dict["MinorLinkerVersion"]["Value"],
        "size_of_code": optional_header_dict["SizeOfCode"]["Value"],
        "size_of_initialized_data": optional_header_dict["SizeOfInitializedData"]["Value"],
        "size_of_uninitialized_data": optional_header_dict["SizeOfUninitializedData"]["Value"],
        "address_of_entry_point": optional_header_dict["AddressOfEntryPoint"]["Value"],
        "base_of_code": optional_header_dict["BaseOfCode"]["Value"],
        "base_of_data": optional_header_dict["BaseOfData"]["Value"],
        "image_base": optional_header_dict["ImageBase"]["Value"],
        "section_alignment": optional_header_dict["SectionAlignment"]["Value"],
        "file_alignment": optional_header_dict["FileAlignment"]["Value"],
        "major_operating_system_version": optional_header_dict["MajorOperatingSystemVersion"]["Value"],
        "minor_operating_system_version": optional_header_dict["MinorOperatingSystemVersion"]["Value"],
        "major_image_version": optional_header_dict["MajorImageVersion"]["Value"],
        "minor_image_version": optional_header_dict["MinorImageVersion"]["Value"],
        "major_subsystem_version": optional_header_dict["MajorSubsystemVersion"]["Value"],
        "minor_subsystem_version": optional_header_dict["MinorSubsystemVersion"]["Value"],
        "size_of_image": optional_header_dict["SizeOfImage"]["Value"],
        "size_of_headers": optional_header_dict["SizeOfHeaders"]["Value"],
        "checksum": optional_header_dict["CheckSum"]["Value"],
        "subsystem": pefile.SUBSYSTEM_TYPE[optional_header_dict["Subsystem"]["Value"]],
        "size_of_stack_reserve": optional_header_dict["SizeOfStackReserve"]["Value"],
        "size_of_stack_commit": optional_header_dict["SizeOfStackCommit"]["Value"],
        "size_of_heap_reserve": optional_header_dict["SizeOfHeapReserve"]["Value"],
        "size_of_heap_commit": optional_header_dict["SizeOfHeapCommit"]["Value"],
        "loader_flags": optional_header_dict["LoaderFlags"]["Value"],
        "number_of_rva_and_sizes": optional_header_dict["NumberOfRvaAndSizes"]["Value"],
        "dll_characteristics": parse_optional_header_dll_characteristics(
            optional_header_dict["DllCharacteristics"]["Value"])
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
        "object_file_alignment_bytes": int("".join(map(lambda x: str(int(x)), bit_array[20:24])), 2),
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
    for imp in pe.DIRECTORY_ENTRY_IMPORT:
        import_list: list[pefile.ImportData] = imp.imports
        try:
            for import_obj in import_list:
                obj = {
                    "name": import_obj.name.decode("ascii"),
                    "address": import_obj.address + pe.OPTIONAL_HEADER.ImageBase,
                }
                results.append(obj)
        except:
            continue

    return results


def get_exports(pe: pefile.PE):
    results = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            try:
                obj = {
                    "name": exp.name.decode("ascii"),
                    "address": exp.address + pe.OPTIONAL_HEADER.ImageBase,
                }
                results.append(obj)
            except:
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
