[English](./README.en.md) | 简体中文

## 环境依赖：
1. python >=3.6
2. 第三方库 gast >=0.3.3
3. 第三方库 ast >=0.8.1
4. 第三方库 eventlet >=0.25.2
5. 第三方库 astor <= 0.7.0 (gast处理不了attribut storage)
6. shell 辅助工具 rsync 用于替换 cp

## 设计方案
1. 采用AST解析的方式，对接口进行了升级，所以升级过程中，**首先要保证需要升级的文件是可执行的**，目前支持  
	- 对接口的替换，如paddle.fluid.data替换成paddle.data；
	- 对接口参数的增加、删除和修改；
	- 对接口名字补全，如self.q_fc = Linear替换成self.q_fc = paddle.fluid.dygraph.Linear


## 代码说明如下：
```
1、paddle_api_upgrade/upgrade_models_api_run.py  #入口，执行解析流程脚本
2、paddle_api_upgrade/run.sh #运行脚本
3、paddle_api_upgrade/api_upgrade_src/upgrade_models_api_utils.py #文件处理操作
4、paddle_api_upgrade/api_upgrade_src/modify_transformer.py # 接口参数的增，删，改，以及接口替换操作
5、paddle_api_upgrade/api_upgrade_src/import_transformer.py # 扫描 import 建立 api 全面映射
6、paddle_api_upgrade/api_upgrade_src/replace_full_name_transformer.py # 通过 api 全面映射 替换api别名
7、paddle_api_upgrade/api_upgrade_src/node_operation.py # AST内属性和节点的具体操作
8、paddle_api_upgrade/api_upgrade_src/script/restore_comments_spaces.py #转换后的脚本通过这个脚本恢复注释和空格
9、paddle_api_upgrade/api_upgrade_src/script/convert_dict.py #excel表格的数据通过这个脚本解析成json文件
10、paddle_api_upgrade/api_upgrade_src/dict/data.json #excel导出的原始数据
11、paddle_api_upgrade/api_upgrade_src/dict/modify.dict  #转换需要的json词表
12、paddle_api_upgrade/api_upgrade_src/conf/upgrade.conf  #接口自动化升级配置文件
```
## 使用方法：
注意：input如果为模型目录，请保证模型目录下的运行脚本可以正常运行，所需要的依赖都正常安装；
```
cd paddle_api_upgrade
sh run.sh input output # 对非mac用户
bash run_mac.sh input output # 对mac用户

#input: 输入为需要升级的python脚本文件名，或者需要升级的模块目录(工具会递归解析，并在output目录下生成新文件)
#output: 输出为升级后的文件，或者目录
```

script 说明：
1. convert_dict.py 可以从最原始的excel 文件转换出后续程序需要的 json 文件 (../dict/data.json)
```
../dict/modify.dict
../dict/delete.dict
```
2. restore_comments_spaces.py 可以恢复转换后的文件的空格和注释，并且把它存到 ./temp1 文件夹下面.
```
python restore_comments_spaces.py [原始文件] [被转换后的文件]
```
3. check_api.py 可以检测映射词表里面的api是否可以在目标环境（alpha2.0上面工作）。
```
cd paddle_api_upgrade/paddle_api_src/script/
python check_api
```

test 说明： cd test run

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

## 方案遗留问题
- 词表目前支持"name",  "add",  “delete“,  "rename"这四种，对应代码中会有这四种操作，目前add一般是一些默认值属性，所以对于接口升级来说这些有默认值参数可以加可以不加，未来可以根据接口演变，考虑是否需要删除这个操作；
