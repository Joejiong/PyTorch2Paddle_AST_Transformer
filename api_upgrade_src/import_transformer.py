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


class ImportVisitor(gast.NodeVisitor):
    """
    ImportVisitor will analyze module's import & from statement,
    and create a mapping between the full name one and the origin.
    
    """
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.import_dict = dict()
        self.from_import_dict = dict()

    def visit_Import(self, node):
        self.generic_visit(node)
        print('ImportName--->:', type(node).__name__)
        print(astor.dump_tree(node.names))
        self.import_dict.update({node.names[0].asname: node.names[0].name})

    def visit_ImportFrom(self, node):
        self.generic_visit(node)
        print('NameFrom--->:', type(node).__name__)
        print(astor.dump_tree(node.names))
        print(astor.dump_tree(node))

        module_name = node.module
        print("module_name--->", module_name)

        for func_name in node.names:
            print(func_name.name)
            full_name = module_name + '.' + func_name.name
            self.from_import_dict.update({func_name.name: full_name})
