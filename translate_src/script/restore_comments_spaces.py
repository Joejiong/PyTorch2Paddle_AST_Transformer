import sys
import os
import re

INDENT_CONST=4
PREFIX_LINE="*&&^"


def counting_indent_space(line):
    diff = len(line) - len(line.lstrip(' '))
    return diff
        

def diff_indent_space(cur_line, next_line):
    diff = counting_indent_space(next_line) - counting_indent_space(cur_line)
    return diff


def recover(input, output): 
    src_lines = open(input, 'r').readlines()
    trg_lines = open(output, 'r').readlines()

    null_doc_list = []
    null_doc = {}
    for i in range(len(src_lines)): 
        line = src_lines[i].strip("\n")
        if not line.strip() or line.strip().startswith("#"): 
            if i == 0: 
                null_doc_list.append(("^start", [line]))
            else: 
                last_line = src_lines[i - 1].strip("\n")
                if not last_line.strip() or last_line.strip().startswith("#"): 
                    null_doc_list[-1][-1].append(line)
                else: 
                    if last_line.strip().startswith("import ") or last_line.strip().startswith("from "): 
                        prefix_line = last_line.strip()
                    else: 
                        prefix_line = src_lines[i - 1].strip().split()[0]
                    null_doc_list.append((prefix_line, [line]))
    null_doc = {v[0]: "\n".join(v[1]) for v in null_doc_list}

    recover_list = []
    if "^start" in null_doc: 
        recover_list.append(null_doc["^start"])

    prefix_line = PREFIX_LINE
    for idx, line in enumerate(trg_lines): 
        line = line.strip("\n")

        if prefix_line.strip("\n") != line.strip("\n"):   
            recover_list.append(line)
        else:
            continue

        if not line.strip(): 
            continue

        if line.strip().startswith("import ") or line.strip().startswith("from "): 
            prefix = line.strip()
        else: 
            prefix = line.strip().split()[0]

        if idx < len(trg_lines) - 1 and diff_indent_space(line, next_line=trg_lines[idx+1]) == INDENT_CONST:
            recover_list.append(trg_lines[idx+1])
            prefix_line = trg_lines[idx+1]
            recover_list.append(null_doc[prefix])
        else:
            recover_list.append(null_doc[prefix])

    return recover_list


def get_files(path): 
    file_py_dict = {}
    if not os.path.isdir(path):
        dirpath, filename = os.path.split(path)
        path = os.path.abspath(path)
        file_py_dict[filename] = path
        return file_py_dict

    for root, dirs, files in os.walk(path): 
        for file in files:
            if not os.path.splitext(file)[1] == '.py': 
                continue
            abs_path = os.path.join(root, file)
            file_py_dict[file] = abs_path
    return file_py_dict


def main(input_dir, output_dir, temp_dir="./temp"): 
    if not os.path.exists(temp_dir): 
        os.makedirs(temp_dir)
    
    input_file_dict = get_files(input_dir)  
    output_file_dict = get_files(output_dir)
    for filename in output_file_dict: 
        if filename not in input_file_dict: 
            continue
        print("recover file %s" % input_file_dict[filename])
        recover_list = recover(input_file_dict[filename], output_file_dict[filename])
        new_file = os.path.join(temp_dir, filename)
        with open(new_file, 'w') as fw: 
            out_str = "\n".join(recover_list)
            out_str = re.sub("\n\n\n", "\n\n", out_str)
            fw.write(out_str)


if __name__ == "__main__": 
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)



 
