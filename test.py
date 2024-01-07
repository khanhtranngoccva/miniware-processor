import pefile_processor
import pprint

results = pefile_processor.analyze_file("./test_coccoc.exe")

pprint.pp(results["strings"])