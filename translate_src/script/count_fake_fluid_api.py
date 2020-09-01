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
from convert_new_csv_to_dict import load_src_json

OUTPUT_PATH = "../dict/final_fluid_api.dict"
ORIGINAL_COLUMN = "1.x_api_name_list"
COLUMN_TO_CHECK = "final_name"
# count = 0


def check_fluid_by_key(term):
    # 新词表规则下，check final_name contain fluid
    value = term.strip("\"").strip("\'").split("|")
    return ["fluid" in v_item for v_item in value]


def check_fluid_dict(f):
    json_dict = load_src_json(f)
    upgrade_api = dict()
    if not json_dict:
        print("parse json dict error")
        exit(1)

    json_dict_src = json_dict
    count = 0
    for term in json_dict_src:

        name = term.get(ORIGINAL_COLUMN, None)
        check_name = term.get(COLUMN_TO_CHECK, None)

        assert name, "old version doesn't exist"
        assert check_name, "new version doesn't exist"

        repeated_api_list = check_name.split('---')

        for name in repeated_api_list:
            if True in check_fluid_by_key(check_name):
                upgrade_api[name] = dict()
                upgrade_api[name]["name"] = check_name
                # global count
                count += 1

    res = json.dumps(upgrade_api, sort_keys=True, indent=4)
    print("we have %s final api still contain fluid" % (count))
    return res


if __name__ == "__main__":
    # default cmds:
    # python3 count_fake_fluid_api.py ../dict/intermediate_data.json
    json_file = check_fluid_dict(sys.argv[1])
    with open(OUTPUT_PATH, "w") as outfile:
        outfile.write(json_file)
