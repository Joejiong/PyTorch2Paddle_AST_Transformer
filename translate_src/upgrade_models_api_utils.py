#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import re


def load_replace_dict(dict_file):
    """
    load paddle replace api dict file
    """
    replace_dict = {}
    with open(dict_file, 'r') as fr:
        for line in fr:
            elems = line.strip().split('\t')
            assert len(elems) == 2
            replace_dict[elems[0]] = elems[1]
            key = elems[0]
            if key.startswith("paddle."):
                key = key.lstrip("paddle.")
                replace_dict[key] = elems[1]
            if key.startswith("fluid."):
                key = key.lstrip("fluid.")
                replace_dict[key] = elems[1]
    return replace_dict


def load_modify_dict(dict_file):
    """
    load upgrade api dict and params
    """
    with open(dict_file, 'r') as fr:
        modify_dict = json.load(fr)
    add_dict = {}
    for key in modify_dict:
        value = modify_dict[key]
        if key.startswith("paddle."):
            key = key.lstrip("paddle.")
            add_dict[key] = value
        if key.startswith("fluid."):
            key = key.lstrip("fluid.")
            add_dict[key] = value
    modify_dict.update(add_dict)
    return modify_dict


def load_delete_dict(dict_file):
    """
    load upgrade delete dict
    """
    delete_list = []
    with open(dict_file, 'r') as fr:
        for line in fr:
            line = line.strip()
            elems = line.split('.')
            for i in range(len(elems) - 1):
                idx = len(elems) - i - 1
                pattern = ".".join(elems[i:])
                delete_list.append(pattern)
    return delete_list


def get_file_list(path):
    """
    get file list from input directory
    """
    file_py_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if not os.path.splitext(file)[1] == '.py':
                continue
            file_py_list.append(os.path.join(root, file))
    return file_py_list


def get_cur_file_list():
    """
    get file list from current directory
    """
    file_py_list = []
    for root, dirs, files in os.walk("."):
        root = root.lstrip("./")
        if "translate_src" in root:
            continue
        for file in files:
            if "upgrade_models_api_run.py" in file:
                continue
            if "_ce.py" in file:
                continue
            if "ci.yaml" in file or "ci.yml" in file:
                continue
            suffix = os.path.splitext(file)[1]
            if suffix == '.py' or suffix == '.sh' or suffix == '.yaml' or '.md':
                file_py_list.append(os.path.join(root, file))
    return file_py_list


def check_dir(path):
    """
    check input path is a directory or file
    """
    if os.path.isdir(path):
        file_list = get_file_list(path)
        return file_list
    elif os.path.isfile(path):
        return path
    else:
        return None


def import_module(path):
    """
    input: path = aaa/bbb/ccc/ddd.py
    out: from aaa.bbb.ccc import ddd
    """
    (dirpath, filename) = os.path.split(path)
    module_name = filename.rstrip(".py")
    module_dir = re.sub("/", ".", dirpath).strip(".")
    if not module_dir:
        import_module_str = "import " + module_name
    else:
        import_module_str = "from " + module_dir + " import " + module_name
    return import_module_str


def print_info(info):
    print(info)


def check_paddle(file):
    fr = open(file, 'r').read()
    import_stat = re.search("import(\s+)paddle", fr)
    from_stat = re.search("from(\s+)paddle", fr)
    if import_stat or from_stat:
        return 0
    return -1


def check_built_in_func():
    cache_dict = {}
    build_in_fun = dir(__builtins__)
    for fun in build_in_fun:
        cache_fun = "%s_cache.py" % fun
        fun_src = "%s.py" % fun
        cache_dict[fun_src] = cache_fun
    return cache_dict


def load_config(conf_file):
    conf_dict = {"input_path": None, "output_path": None}
    with open(conf_file, 'r') as fr:
        for line in fr:
            line = line.strip()
            if line.startswith("input_path"):
                conf_dict["input_path"] = line.split("=")[1].strip()
            if line.startswith("output_path"):
                conf_dict["output_path"] = line.split("=")[1].strip()
    return conf_dict
