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

import unittest
import astor
import astor.code_gen
import ast
import codegen
import gast
import numpy as np
import inspect
import dygraph_lenet
import six
import astunparse
import pprint
from yapf.yapflib.yapf_api import FormatCode
from api_upgrade_src.import_transformer import ImportVisitor


def transfomer_import_test(root):
    """import transformer test

    Args:
        root (gast.node)

    Returns:
        dict, dict: import_dict, from_import_dict
    """
    import_visitor = ImportVisitor(root)
    import_visitor.visit(root)

    print(import_visitor.import_dict)
    print(import_visitor.from_import_dict)

    return import_visitor.import_dict, import_visitor.from_import_dict


def get_attr_full_name(node):
    return astor.to_source(gast.gast_to_ast(node)).strip()


class TestImportTransfomer(unittest.TestCase):
    """
    test for import_transformer which scan the code,
    and create dict for replace_full_name transformer
    """
    maxDiff = None

    def test_replace_full_name_transformer(self):
        # expected
        expected_dict = dict()
        # captured input
        captured_dict = dict()
        input_test = gast.parse(inspect.getsource(dygraph_lenet))
        print("*******original code*******")
        original_code = astor.to_source(gast.gast_to_ast(input_test))
        original_code_formated = FormatCode(original_code)
        print(original_code_formated[0])

        # get captured
        root = gast.parse(input_test)
        print("*******start_transfer*******")
        import_dict, from_import_dict = transfomer_import_test(root)

        print("*******code_for_captured_formated*******")
        for k, v in import_dict.items():
            print("k,v", k, v)
            if k and "paddle" in v:
                captured_dict.update({k: v})

        for k, v in from_import_dict.items():
            print("kv,from", k, v)
            if k and "paddle" in v:
                captured_dict.update({k: v})

        print("*******code_for_expected_formated*******")
        expected_dict = import_map = {
            "fluid": "paddle.fluid",
            "Conv2D": "paddle.fluid.dygraph.nn.Conv2D",
            "Pool2D": "paddle.fluid.dygraph.nn.Pool2D",
            "Linear": "paddle.fluid.dygraph.nn.Linear"
        }

        # testting
        print("ex", expected_dict)
        print("cp", captured_dict)
        self.assertEqual(expected_dict, captured_dict)


if __name__ == '__main__':
    root = gast.parse(inspect.getsource(dygraph_lenet))
    print(astunparse.unparse(root))
    import_dict, from_import_dict = transfomer_import_test(root=root)

    unittest.main()
