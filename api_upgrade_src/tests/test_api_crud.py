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

import inspect
import gast
import astor
import codegen
import argparse
import sys
import paddle
from api_upgrade_src.modify_transformer import AddParamTransformer, DelParamTransformer, RenameParamTransformer, RepAttributeTransformer
from api_upgrade_src.replace_transformer import ReplaceTransformer
from api_upgrade_src.upgrade_models_api_utils import load_replace_dict, load_modify_dict
from yapf.yapflib.yapf_api import FormatCode


def transformer(root, modify_dict):
    """
    API ast CRUD transformer

    Args:
        root (gast node)
        modify_dict (json)

    Returns:
        root (gast node)
    """
    AddParamTransformer(root).add(modify_dict)
    DelParamTransformer(root).delete(modify_dict)
    RenameParamTransformer(root).replace(modify_dict)
    RepAttributeTransformer(root).replace(modify_dict)
    return root


class TestApiCRUD(unittest.TestCase):
    """
    test_add_kwarg
    test_delete_kwarg
    test_rename_kwarg
    test_fusion_def
    test_single_model_file
    test_project_folders
    """
    maxDiff = None

    def test_add_kwarg(self):
        # expected
        expected = '''
def test1():
    data4 = paddle.tensor.zeros(x=x, shape=[3, 2], dtype='float32', device=None, out=None)
        '''
        # captured input
        input_test = '''
def test1():
    data4 = paddle.fluid.layers.zeros(x=x, shape=[3, 2], dtype='float32', force_cpu=True)
        '''

        # get captured
        # root = gast.parse(inspect.getsource(input_test))
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******test_1_source_code*******")
        # print(inspect.getsource(test1))
        root = transformer(root, modify_dict)
        print("*******test_add_kwarg*******")
        print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        expected = astor.to_source(gast.gast_to_ast(root_expected))

        # testting
        self.assertEqual(expected, captured)

    def test_delete_kwarg(self):

        # expected
        expected = '''
def test2(x, y):
    data4 = paddle.tensor.add(x, y, name=None, alpha=1, out=None)
        '''
        # captured input
        input_test = '''
def test2(x, y):
    data4 = paddle.fluid.layers.elementwise_add(x, y, axis=-1, act=None, name=None)
        '''

        # get captured
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******test_2_source_code*******")
        # print(inspect.getsource(test1))
        root = transformer(root, modify_dict)
        print("*******test_delete_kwarg*******")
        print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        expected = astor.to_source(gast.gast_to_ast(root_expected))

        # testting
        self.assertEqual(expected, captured)

    def test_rename_kwarg(self):
        # expected
        expected = '''
def test3(x, y):
    data4 = paddle.tensor.argmax(input=x, axis=2, dtype=None, keepdims=False, name=None, out=None)
        '''
        # captured input
        input_test = '''
def test3(x, y):
    data4 = paddle.fluid.layers.argmax(x=x, axis=2)
        '''

        # get captured
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******test_3_source_code*******")
        # print(inspect.getsource(test1))
        root = transformer(root, modify_dict)
        print("*******test_rename_kwarg*******")
        print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        expected = astor.to_source(gast.gast_to_ast(root_expected))

        # testting
        self.assertEqual(expected, captured)

    def test_fusion_defDes(self):

        # expected
        expected = '''
def test1(x):
    data1 = paddle.nn.data(x=x)
    data2 = paddle.reshape(x=data1, shape=[1, 2, 3])
    data3 = paddle.tensor.zeros(shape=[3, 2], dtype='float32', device=None, out=None)
    return abc
def test2(x): 
    data1 = paddle.tensor.tanh(input=x, out=None)
    data2 = paddle.tensor.zeros(shape=[3, 2], dtype='float32', device=None, out=None)
def test3(x): 
    data1 = paddle.nn.Sigmoid(input=x, inplace=False)
    data2 = paddle.tensor.sum(x, axis=0)
def test4(x): 
    data1 = paddle.tensor.max(x=x, out=None)
    data2 = paddle.tensor.stack(x, dim=0, out=None)
    
        '''
        # captured input
        input_test = '''
def test1(x):
    data1 = paddle.fluid.data(x=x)
    data2 = paddle.fluid.layers.reshape(x=data1, shape=[1, 2, 3])
    data3 = paddle.fluid.layers.zeros(shape=[3, 2], dtype='float32')

    return abc
def test2(x): 
    data1 = paddle.fluid.layers.tanh(x=x)
    data2 = paddle.fluid.layers.zeros(shape=[3, 2], dtype='float32')
def test3(x): 
    data1 = paddle.fluid.layers.sigmoid(x=x)
    data2 = paddle.fluid.layers.reduce_sum(x, dim=0)
def test4(x): 
    data1 = paddle.fluid.layers.reduce_max(x=x)
    data2 = fluid.layers.stack(x, dim=0)
        '''

        # get captured
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******test_4_source_code*******")
        # print(inspect.getsource(test1))
        root = transformer(root, modify_dict)
        print("*******test_fusion_function_kwarg*******")
        print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        expected = astor.to_source(gast.gast_to_ast(root_expected))

        # testting
        self.assertEqual(expected, captured)

    # TODO: fix the these unitest for nice print comparison
    def test_single_model_file(self):

        parser = argparse.ArgumentParser("Paddle API upgrade")
        parser.add_argument("--modify_dict",
                            type=str,
                            default="../dict/modify.dict")
        parser.add_argument("--input", type=str, default='class_cnn.py')
        parser.add_argument("--output",
                            type=str,
                            default='class_cnn_update.py')
        args = parser.parse_args()

        # read captured

        with open('class_cnn.py', 'r') as fp:
            data_captured = fp.read()

        with open('class_cnn_expected.py', 'r') as fp:
            data_expected = fp.read()

        # expected
        expected = data_expected
        # captured input
        input_test = data_captured

        # # get captured
        root = gast.parse(input_test)
        root_expected = gast.parse(expected)
        print("*******test_5_source_code*******")
        root = transformer(root, modify_dict)
        print("*******test_model_single_file*******")
        print(astor.to_source(gast.gast_to_ast(root)))
        captured = astor.to_source(gast.gast_to_ast(root))
        captured_formated = FormatCode(captured)

        with open('class_cnn_update.py', 'w') as fp:
            fp.write(captured_formated[0])

        expected = astor.to_source(gast.gast_to_ast(root_expected))
        data_expected_formated = FormatCode(captured)

        # read captured
        with open('class_cnn_update.py', 'r') as fp:
            data_captured = fp.read()

        captured = astor.to_source(gast.gast_to_ast(root))
        data_captured_formated = FormatCode(captured)

        # testting
        self.assertEqual(data_expected_formated, data_captured_formated)

    def test_project_folder(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    modify_dict = load_modify_dict('../dict/modify.dict')
    unittest.main()
