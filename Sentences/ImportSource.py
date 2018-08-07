import os
import re
import sys
PATH = "../Sentences"
os.chdir(PATH)  # so that it will always be on reference
all_files = list(filter(lambda x: True if x.endswith(".py") and x.startswith("T") and x[1:x.index(".")].isnumeric() else False, os.listdir(PATH)))
def_pattern = re.compile("def *(.+?)\(.+?\):")
newest_process = 0
newest_process_func_name = ""
newest_process_func_file = ""
newest_extractor = 0
newest_extractor_func_name = ""
newest_extractor_func_file = ""
newest_harness = 0
newest_harness_func_name = ""
newest_harness_func_file = ""
for fpath in all_files:
    with open(fpath, "r") as f:
        source = f.read()
        functions = re.findall(def_pattern, source)
        for func in functions:
            if func.startswith("process"):
                num = float(fpath[1:fpath.index(".")]+"."+"".join(func.split("_")[1:]))
                if num > newest_process:
                    newest_process_func_name = func
                    newest_process_func_file = fpath
            elif func.startswith("extract"):
                num = float(fpath[1:fpath.index(".")]+"."+func.split("_")[1])
                if num > newest_extractor:
                    newest_extractor_func_name = func
                    newest_extractor_func_file = fpath
            elif func.startswith("harness"):
                num = float(fpath[1:fpath.index(".")]+"."+func.split("_")[1])
                if num > newest_harness:
                    newest_harness_func_name = func
                    newest_harness_func_file = fpath
exec("from "+newest_extractor_func_file.strip(".py")+" import "+newest_extractor_func_name+" as ltex")
exec("from "+newest_process_func_file.strip(".py")+" import "+newest_process_func_name+" as ltpc")
exec("from "+newest_harness_func_file.strip(".py")+" import "+newest_harness_func_name+" as lths")
