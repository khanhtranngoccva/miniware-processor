import pprint

import pefile_processor

res = pefile_processor.analyze_file("./test_coccoc.exe")
pprint.pp(res["optional_header"])
