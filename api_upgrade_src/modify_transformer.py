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

from api_upgrade_src.node_operation import get_attr_full_name, delete_keywords_from, rename_keywords_to, add_keywords_to
from api_upgrade_src.upgrade_models_api_utils import print_info
                                                                                                 

class AddParamTransformer(gast.NodeTransformer): 
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.modify_dict = ""

    def add(self, modify_dict):
        self.modify_dict = modify_dict
        self.visit(self.root)
   
    def visit_Call(self, node): 
        attribute_node = node.func
        attr_full_name = get_attr_full_name(attribute_node)
        if attr_full_name in self.modify_dict: 
            if "add" not in self.modify_dict[attr_full_name]:
                return node
            add_dict = self.modify_dict[attr_full_name]["add"]
            add_keywords_to(node, add_dict)
            for param in add_dict: 
                print_info("\033[1;33mAdd Params (%s) to API (%s)\033[0m" % (param, attr_full_name))
        return node


class DelParamTransformer(gast.NodeTransformer):
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.modify_dict = ""

    def delete(self, modify_dict):
        self.modify_dict = modify_dict
        self.visit(self.root)

    def visit_Call(self, node): 
        attribute_node = node.func
        attr_full_name = get_attr_full_name(attribute_node)
        if attr_full_name in self.modify_dict: 
            if "delete" not in self.modify_dict[attr_full_name]: 
                return node
            delete_dict = self.modify_dict[attr_full_name]["delete"]
            delete_keywords_from(node, delete_dict)
            for param in delete_dict: 
                print_info("\033[1;33mDelete Params (%s) from API (%s)\033[0m" % (param, attr_full_name))
        return node


class RenameParamTransformer(gast.NodeTransformer):
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.modify_dict = ""
    
    def replace(self, modify_dict): 
        self.modify_dict = modify_dict
        self.visit(self.root)

    def visit_Call(self, node): 
        attribute_node = node.func
        attr_full_name = get_attr_full_name(attribute_node)
        if attr_full_name in self.modify_dict: 
            if "rename" not in self.modify_dict[attr_full_name]: 
                return node
            modify_dict = self.modify_dict[attr_full_name]["rename"]
            rename_keywords_to(node, modify_dict)
            for param in modify_dict: 
                print_info("\033[1;33mRename Params (%s->%s) in API (%s)\033[0m" % (param, modify_dict[param], attr_full_name))
        return node


class RepAttributeTransformer(gast.NodeTransformer): 
    def __init__(self, node):
        assert isinstance(node, gast.AST)
        self.root = node
        self.modify_dict = ""

    def replace(self, modify_dict): 
        self.modify_dict = modify_dict
        self.visit(self.root)

    def visit_Attribute(self, node): 
        self.generic_visit(node)
        attr_full_name = get_attr_full_name(node)
        if attr_full_name in self.modify_dict:
            new_api_name = self.modify_dict[attr_full_name]['name']
            new_api_node = gast.parse(new_api_name).body[0].value
            print_info("\033[1;33mUpgrade API (%s->%s)\033[0m" % (attr_full_name, new_api_name))
            return new_api_node
        return node
