import pprint
import pefile_processor

out = pefile_processor.analyze_file("./test_coccoc.exe")
for data in out['strings']:
    print(data)
    # pass
