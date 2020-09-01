English | [简体中文](./README.md)

## Environment Dependence：
1. python >=3.6
2. Third library: gast >=0.3.3
3. Third library: ast >=0.8.1
4. Third library: eventlet >=0.25.2
5. Third library: astor <= 0.7.0 (gast cannot handle attribute storage)
6. shell tool: rsync replace commands for cp

## Project Design
1. with AST parsing, we manage to upgrade PaddlePaddle API, so while upgrading **firstly, we have to make sure the code is well working** , currently we support the following use operations.
	- replace api by name，e,g: paddle.fluid.data-->paddle.data;
	- modification api: API AST CRUD;
	- replace full name, e,g: self.q_fc = Linear-->self.q_fc = paddle.fluid.dygraph.Linear.


## Code Detail description:
```
1、paddle_api_upgrade/upgrade_models_api_run.py  # main function
2、paddle_api_upgrade/run.sh # entry shell
3、paddle_api_upgrade/api_upgrade_src/upgrade_models_api_utils.py # file operation utility function.
4、paddle_api_upgrade/api_upgrade_src/modify_transformer.py # API CRUD transformer.
5、paddle_api_upgrade/api_upgrade_src/import_transformer.py # scanning import module for creating full name api mapping.
6、paddle_api_upgrade/api_upgrade_src/replace_full_name_transformer.py # via api full name mapping replace api alias.
7、paddle_api_upgrade/api_upgrade_src/node_operation.py # AST node operation
8、paddle_api_upgrade/api_upgrade_src/script/restore_comments_spaces.py # script for restoring comments and space after upgrading the code.
9、paddle_api_upgrade/api_upgrade_src/script/convert_dict.py # Script for transfering excel data to dict data.
10、paddle_api_upgrade/api_upgrade_src/dict/data.json # json data from raw excel.
11、paddle_api_upgrade/api_upgrade_src/dict/modify.dict  # Modification dictionary.
12、paddle_api_upgrade/api_upgrade_src/conf/upgrade.conf  # Intermediate
 configuration file.
```
## How to Use：
caveats: if input is a directory, please make sure that files under the directory are well working;
```
cd paddle_api_upgrade
sh run.sh input output # for non-mac users
bash run_mac.sh input output # for mac users

#input: could be a single file or an entire project folder(the tool could recursively parse the whole project)
#output: could be a single file or an entire project folder
```

script description:
1. convert_dict.py will use the original json file (../dict/data.json) directly converted from excel to generate the following two files by default
```
../dict/modify.dict
../dict/delete.dict
```
2. restore_comments_spaces.py could restore comments and spaces in source model file to transfered model file and save it to ./temp1 folder.
```
python restore_comments_spaces.py [original model folder or file path] [transfered model file without comments]
```
3. check_api.py could automatically check whether an api could import into target environment or not and if not it will generate a summary report to record which api could not be included.
```
cd paddle_api_upgrade/paddle_api_src/script/
python check_api
```

test description: cd test run

	python test_api_crud.py

	# currently we have unitest for each key word in dict

	test_add_kwarg
	test_delete_kwarg
	test_rename_kwarg
	test_fusion_def

	# test for transformer
	test_replace_full_name
	test_import_visitor

	# test_project_folder:
	bash run_mac.sh api_upgrade_src/tests/dygraph_folder_test/transformer/ api_upgrade_src/tests/dygraph_folder_test/output_folder_transformer/

	# TODO:
	test_single_model_file：
	bash run.sh ../../../model/input/class_cnn.py ../../../output/class_cnn_transfered.py

## TODO and Problems:
- currently we support four AST node operations "name",  "add",  “delete“,  "rename"，but add operation has some problems, because paddle source code usually adds param with default value, so it is redundant to add parameter with default value. Therefore we consider eliminating this operation.
