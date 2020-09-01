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

from api_upgrade_src.node_operation import get_attr_full_name
from api_upgrade_src.upgrade_models_api_utils import print_info


class ReplaceTransformer(gast.NodeTransformer): 
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
        if attr_full_name in self.replace_dict: 
            new_api_name = self.replace_dict[attr_full_name]
            new_api_node = gast.parse(new_api_name).body[0].value
            print_info("\033[1;31mUpgrade API (%s->%s)\033[0m" % (attr_full_name, new_api_name))
            return new_api_node
        return node


