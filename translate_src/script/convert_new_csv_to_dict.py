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

import sys
import json

OLD_EXCEL_API_COLUMN = "1.x_api_name_list"
NEW_EXCEL_API_COLUMN = "final_name"
OUTPUT_PATH = "../dict/modify_origin_csv.dict"


def load_src_json(f):
    try:
        with open(f, 'r') as fr:
            json_dict = json.load(fr)
    except Exception as e:
        print("load exception with error: ", e)
        json_dict = dict()
    return json_dict


def get_key_value(term):
    value = term.strip("\"").strip("\'").split("|")
    key_value = {}
    for v in value:
        print(v)
        prek, prev = v.split('=')
        if prev in ['None', 'False', 'True'] or prev.isnumeric():
            prev = eval(prev)
        key_value[prek] = prev
    return key_value


def check_value_by_key(term):
    # 新词表规则下，value可能填充成None，过滤一下
    value = term.strip("\"").strip("\'").split("|")
    print("value", value)
    return not (value[0] == 'None' and len(value) == 1)


def get_key(term):
    value = term.strip("\"").strip("\'").split("|")
    key_value = {v: None for v in value}
    return key_value


def check_conflict(add_dict, rename_dict):
    rename_list = rename_dict.values()
    add_list = add_dict.keys()
    inter = set(rename_list).intersection(set(add_list))
    print("-----inter------", inter)
    if not inter:
        return add_dict, rename_dict
    else:
        for c in inter:
            add_dict.pop(c)
    return add_dict, rename_dict


def convert_dict(f):
    json_dict = load_src_json(f)
    upgrade_api = dict()
    if not json_dict:
        print("parse json dict error")
        exit(1)

    json_dict_src = json_dict
    for term in json_dict_src:
        name = term.get(OLD_EXCEL_API_COLUMN, None)
        upgrade_name = term.get(NEW_EXCEL_API_COLUMN, None)

        assert name, "old version doesn't exist"
        assert upgrade_name, "new version doesn't exist"
        print(term)
        add_dict = dict()
        if "add" in term and check_value_by_key(term["add"]):
            print(check_value_by_key(term['add']))
            add_dict = get_key_value(term["add"])

        rename_dict = dict()
        if "rename" in term and check_value_by_key(term["rename"]):
            rename_dict = get_key_value(term["rename"])

        delete_dict = dict()
        if "delete" in term and check_value_by_key(term["delete"]):
            delete_dict = get_key(term["delete"])

        if rename_dict and add_dict:
            add_dict, rename_dict = check_conflict(add_dict, rename_dict)

        if upgrade_name == "None":
            print("upgrade name none: ", upgrade_name)
            continue

        repeated_api_list = name.split('---')
        if "---" in name:
            print("--- in api, so we have multi to one mapping", name)
            print("the repeated api list is", repeated_api_list)

        for name in repeated_api_list:
            upgrade_api[name] = dict()
            upgrade_api[name]["name"] = upgrade_name
            if delete_dict:
                upgrade_api[name]["delete"] = delete_dict
            if add_dict:
                upgrade_api[name]["add"] = add_dict
            if rename_dict:
                upgrade_api[name]["rename"] = rename_dict

    res = json.dumps(upgrade_api, sort_keys=True, indent=4)
    return res


if __name__ == "__main__":
    # default cmds:
    # python3 convert_origin.py ../dict/intermediate_data.json
    json_file = convert_dict(sys.argv[1])
    with open(OUTPUT_PATH, "w") as outfile:
        outfile.write(json_file)
