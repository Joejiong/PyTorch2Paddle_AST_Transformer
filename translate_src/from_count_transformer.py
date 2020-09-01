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

import astor
import gast
import inspect

MDL_NAME = "__future__"


class FromCountVisitor(gast.NodeVisitor):
    """
    ImportVisitor will analyze module's import & from statement,
    and record how many "__future__" has been imported.
    """
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.from_import_count = 0

    def visit_ImportFrom(self, node):
        self.generic_visit(node)
        print('NameFrom--->:', type(node).__name__)

        module_name = node.module
        print("module_name--->", module_name)
        if module_name == MDL_NAME:
            self.from_import_count += 1
