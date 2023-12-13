import pprint

import pefile
import win32api
import pefile_processor

ExecutablePath = "./test_coccoc.exe"
res = pefile_processor.analyze_file("./test_coccoc.exe")
pprint.pp(res["strings"])