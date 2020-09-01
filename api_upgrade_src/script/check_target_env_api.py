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

from __future__ import absolute_import
import importlib
import argparse
import types
import sys
import re
import io
import os
import json
from api_upgrade_src.upgrade_models_api_utils import print_info, import_module, check_paddle, load_config
import paddle

REPORT_FOLDER='./report_unusable_api/'
OUTPUT_PATH='./report_unusable_api/report.txt'
OUTPUT_DICT_REPORT='./report_unusable_api/dict_report.txt'

def api_reader(path):
    print_info("\033[1;32m start to read data.json\033[0m")
    api_json = []
    try: 
        path = os.path.join(os.path.dirname(__file__), path)
        with open(path, 'r') as fr: 
            api_json = json.load(fr)
    except: 
        print_info("\033[1;31m %s read data.json fail\033[0m")
        api_json = dict()
    return api_json


def check_target_env_api_json(api_json_path):
    api_dict = api_reader(api_json_path)
    if not api_dict:
        print("parser json dict error")
        exit(1)
    api_ls = []
    print_info("\033[1;32m start to lead api_dic\033[0m")
    for item in api_dict["Sheet1"]:
        api_ls.append(item["paddle2.0"])

    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_PATH)
    if os.path.isfile(output_path) and os.access(output_path, os.R_OK):
        print("File exists and generate new report")
        os.remove(output_path)
    
    for each_api in api_ls:
        try:
            each_api_list = each_api.split('.')
            api_name = each_api_list[-1]
            folder_name = ".".join(i for i in each_api_list[:-1])
            code_str = "from {0} import {1}".format(folder_name, api_name)
            exec(code_str)
        except:
            info_str = "\033[1;31m %s api {0} error, we can't find api in target env\033[0m".format(each_api)
            print_info(info_str)
            if not os.path.exists(OUTPUT_PATH):
                print_info("\033[1;33m %s create output folder\033[0m")
                os.mkdirs(OUTPUT_PATH)
            
            with open(output_path, 'aw') as fw:
                fw.write(info_str)

def check_modify_dict(dict_path):
    api_dict = api_reader(dict_path)
    if not api_dict:
        print("parser json dict error")
        exit(1)
    api_ls = []
    print_info("\033[1;32m start to lead api_dic\033[0m")
    for k, v in api_dict.items():
        api_ls.append(v["name"])

    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_DICT_REPORT)
    if os.path.isfile(output_path) and os.access(output_path, os.R_OK):
        print("File exists and generate new report")
        os.remove(output_path)

    for each_api in api_ls:
        try:
            each_api_list = each_api.split('.')
            api_name = each_api_list[-1]
            folder_name = ".".join(i for i in each_api_list[:-1])
            code_str = "from {0} import {1}".format(folder_name, api_name)
            exec(code_str)
        except:
            info_str = "\033[1;31m api {0} error, we can't find api in target env\n\033[0m".format(each_api)
            print_info(info_str)
            if not os.path.exists(REPORT_FOLDER):
                print_info("\033[1;33m %s create output folder\033[0m")
                os.mkdir(REPORT_FOLDER)
            
            with open(output_path, 'a') as fw:
                fw.write(each_api+'\n')

if __name__ == "__main__": 
    upgrade_api_args = {
                        "original_api_json": "../dict/data.json",
                        "modify_dict": "../dict/modify.dict",
                        }
    check_target_env_api_json(upgrade_api_args["original_api_json"])
    check_modify_dict(upgrade_api_args["modify_dict"])
