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

from collections import OrderedDict
import json
import codecs
import xlrd
import csv

ORIGIN_EXCEL_PATH = '../dict/origin_csv.xlsx'
OUTPUT_JSON_PATH = '../dict/intermediate_data.json'

workbook = xlrd.open_workbook(ORIGIN_EXCEL_PATH)

convert_list = []
sh = workbook.sheet_by_index(0)
title = sh.row_values(1)
for row_num in range(2, sh.nrows):
    row_value = sh.row_values(row_num)
    single = OrderedDict()
    for colnum in range(0, len(row_value)):
        single[title[colnum]] = row_value[colnum]
    convert_list.append(single)

j = json.dumps(convert_list)

with codecs.open(OUTPUT_JSON_PATH, "w", "utf-8") as f:
    f.write(j)
