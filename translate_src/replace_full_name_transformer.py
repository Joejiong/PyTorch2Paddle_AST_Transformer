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
import copy


def get_attr_full_name(node):
    return astor.to_source(gast.gast_to_ast(node)).strip()


class ReplaceFullNameTransformer(gast.NodeTransformer):
    """replace api with full package name

    e.g:
        import paddle.dygraph.nn as nn
        Then when we call the function,
        the Linear function will be replace with it full name.
        nn.Linear(x) --> paddle.fluid.dygraph.nn.Linear(x)
    """
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.replace_dict = ""

    def replace(self, replace_dict):
        self.replace_dict = replace_dict
        self.visit(self.root)

    def visit_Attribute(self, node):
        self.generic_visit(node)
        attr_full_name = get_attr_full_name(node)
        name_lst = attr_full_name.split('.')
        if name_lst[0] in self.replace_dict:
            new_api_prefix = self.replace_dict[name_lst[0]]
            new_api_name_lst = [new_api_prefix] + [i for i in name_lst[1:]]
            new_api_name = '.'.join(i for i in new_api_name_lst)
            print("\033[3;32mRestore API full name(%s->%s)\033[0m"%
                  (attr_full_name, new_api_name))
            new_api_node = gast.parse(new_api_name).body[0].value
            return new_api_node
        return node


class PaddleReplaceFullNameTransformer(gast.NodeTransformer):
    """
    replace api with full package name
    paddle is a little bit different when it assign
    call object, it a node.func which is different from 
    pytorch, so here we change the code to node.func and 
    use visit_Call transformer when we want to get attr_name.

    e.g:
        Import paddle.dygraph.nn as nn
        Then when we call the function,
        the Linear function will be replace with it full name.
        nn.Linear(x) --> paddle.fluid.dygraph.nn.Linear(x)
    """
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.replace_dict = ""

    def replace(self, replace_dict):
        self.replace_dict = replace_dict
        self.visit(self.root)

    def visit_Call(self, node):
        self.generic_visit(node)
        attr_full_name = get_attr_full_name(node.func)
        new_node = copy.deepcopy(node)

        name_lst = attr_full_name.split('.')
        if name_lst[0] in self.replace_dict:
            new_api_prefix = self.replace_dict[name_lst[0]]
            new_api_name_lst = [new_api_prefix] + [i for i in name_lst[1:]]
            new_api_name = '.'.join(i for i in new_api_name_lst)
            print("\033[3;32mRestore API full name(%s->%s)\033[0m"%
                  (attr_full_name, new_api_name))
            new_node.func = gast.parse(new_api_name).body[0].value
            return new_node
        return node
