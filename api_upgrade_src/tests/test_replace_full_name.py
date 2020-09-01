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
from api_upgrade_src.replace_full_name_transformer import PaddleReplaceFullNameTransformer


def transfomer_replace_test(root, import_map):
    """
    if we want to print the code definition for debugging purpose.

    from paddle.fluid.dygraph.nn import Conv2D, Pool2D, Linear
    import_map = {
         "fluid": "paddle.fluid",
         "Conv2D": "paddle.fluid.dygraph.nn.Conv2D",
         "Pool2D": "paddle.fluid.dygraph.nn.Pool2D",
         "Linear": "paddle.fluid.dygraph.nn.Linear"
    }

    root = gast.parse(inspect.getsource(dygraph_lenet))
    print(astunparse.unparse(root))
    transfomer_replace_test(root=root, import_map=import_map)
    print(astunparse.unparse(gast.gast_to_ast(root)))
    TestReplaceTransfomer.test_replace_full_name_transformer(import_map)

    """
    replace_transformer = PaddleReplaceFullNameTransformer(root)
    replace_transformer.replace(import_map)
    return root


def get_attr_full_name(node):
    return astor.to_source(gast.gast_to_ast(node)).strip()


class TestReplaceTransfomer(unittest.TestCase):
    """
    test for paddle's replace_full_name_transformer 
    """
    maxDiff = None
    import_dict = import_map = {
        "fluid": "paddle.fluid",
        "Conv2D": "paddle.fluid.dygraph.nn.Conv2D",
        "Pool2D": "paddle.fluid.dygraph.nn.Pool2D",
        "Linear": "paddle.fluid.dygraph.nn.Linear"
    }

    def test_replace_full_name_transformer(self, import_map=import_dict):
        # expected
        expected = '''
import paddle
import paddle.fluid as fluid
import numpy as np
from paddle.fluid.dygraph.nn import Conv2D, Pool2D, Linear

class LeNet(fluid.dygraph.Layer):

    def __init__(self, name_scope, num_classes=1):
        super(LeNet, self).__init__(name_scope)
        self.conv1 = paddle.fluid.dygraph.nn.Conv2D(num_channels=1, num_filters=6, filter_size=5, act='sigmoid')
        self.pool1 = paddle.fluid.dygraph.nn.Pool2D(pool_size=2, pool_stride=2, pool_type='max')
        self.conv2 = paddle.fluid.dygraph.nn.Conv2D(num_channels=6, num_filters=16, filter_size=5, act='sigmoid')
        self.pool2 = paddle.fluid.dygraph.nn.Pool2D(pool_size=2, pool_stride=2, pool_type='max')
        self.conv3 = paddle.fluid.dygraph.nn.Conv2D(num_channels=16, num_filters=120, filter_size=4, act='sigmoid')
        self.fc1 = paddle.fluid.dygraph.nn.Linear(input_dim=120, output_dim=64, act='sigmoid')
        self.fc2 = paddle.fluid.dygraph.nn.Linear(input_dim=64, output_dim=num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.conv3(x)
        x = paddle.fluid.layers.reshape(x, [x.shape[0], -1])
        x = self.fc1(x)
        x = self.fc2(x)
        return x
        '''
        # captured input
        input_test = gast.parse(inspect.getsource(dygraph_lenet))
        print("*******original code*******")
        original_code = astor.to_source(gast.gast_to_ast(input_test))
        original_code_formated = FormatCode(original_code)
        print(original_code_formated[0])

        # get captured
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******start_transfer*******")
        root = transfomer_replace_test(root, import_map)

        print("*******code_for_captured_formated*******")
        # print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        captured_formated = FormatCode(captured)
        print(captured_formated[0])

        expected = astor.to_source(gast.gast_to_ast(root_expected))
        expected_formated = FormatCode(expected)
        print("*******code_for_expected_formated*******")
        print(expected_formated[0])

        # testting
        self.assertEqual(expected_formated, captured_formated)


if __name__ == '__main__':

    unittest.main()
