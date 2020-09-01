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

import gast
import json
import astor

IMPROT_PADDLE_POS = 4  # We will insert "import paddle“ as fourth import node.


def get_attr_full_name(node):
    #assert isinstance(node, gast.Attribute)
    return astor.to_source(gast.gast_to_ast(node)).strip()


def delete_keywords_from(node, del_dict):
    assert isinstance(node, gast.Call)
    node.keywords = [k for k in node.keywords if k.arg not in del_dict]
    return


def add_keywords_to(node, add_dict):
    assert isinstance(node, gast.Call)
    for key in add_dict:
        value = gast.Constant(value=add_dict[key], kind=None)
        add_keyword = gast.keyword(arg=key, value=value)
        node.keywords.append(add_keyword)
    return


def rename_keywords_to(node, modify_dict):
    assert isinstance(node, gast.Call)
    for key in node.keywords:
        if key.arg in modify_dict:
            key.arg = modify_dict[key.arg]
    return


def modify_Attribute(node, modify_dict):
    assert isinstance(node, gast.Attribute)
    attr_full_name = get_attr_full_name(node)
    if attr_full_name in modify_dict:
        new_api_name = modify_dict[attr_full_name]["name"]
        new_api_node = gast.parse(new_api_name).body[0].value
        node = new_api_node
    return


def insert_import_module(node, mdl_name="paddle"):
    assert isinstance(node, gast.gast.Module)
    stat = -1
    for b in node.body:
        if not isinstance(b, gast.gast.Import):
            continue
        for name in b.names:
            if "paddle" != name.name:
                continue
            else:
                stat = 0
                break
    if stat != 0:
        def_alias = gast.alias(name=mdl_name, asname=None)
        new_import_node = gast.gast.Import(names=[def_alias])
        node.body.insert(IMPROT_PADDLE_POS, new_import_node)
    return node


def check_mdl_paddle(node, mdl_name="paddle"):
    assert isinstance(node, gast.gast.Module)
    stat = -1
    for b in node.body:
        if isinstance(b, gast.gast.Import):
            for name in b.names:
                if "paddle" not in name.name:
                    continue
                else:
                    stat = 0
                    return stat
        elif isinstance(b, gast.gast.ImportFrom):
            if "paddle" in b.module:
                stat = 0
                return stat
            for name in b.names:
                if "paddle" not in name.name:
                    continue
                else:
                    stat = 0
                    return stat
    return stat


def insert_import_module_with_postion(node,
                                      mdl_name="paddle",
                                      pos=IMPROT_PADDLE_POS):
    """insert import module with pos number

    Args:
        node (gast)
        mdl_name (str, optional): Defaults to "paddle"
        pos (int, optional): Defaults to IMPROT_PADDLE_POS.

    Returns:
        node (gast)
    """
    assert isinstance(node, gast.gast.Module)
    stat = -1
    for b in node.body:
        if not isinstance(b, gast.gast.Import):
            continue
        for name in b.names:
            if "paddle" != name.name:
                continue
            else:
                stat = 0
                break
    if stat != 0:
        def_alias = gast.alias(name=mdl_name, asname=None)
        new_import_node = gast.gast.Import(names=[def_alias])
        print("insert paddle with position: %s" % (pos + 1))
        node.body.insert(pos + 1, new_import_node)
    return node
