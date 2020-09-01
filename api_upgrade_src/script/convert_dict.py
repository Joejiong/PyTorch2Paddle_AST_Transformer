#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2020 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: convert_dict.py
Author: root(root@baidu.com)
Date: 2020/05/15 16:30:57
"""
import sys
import json


def _num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def _string2bool(string):
    d = {'True': True, 'False': False}
    return d.get(string, string)

def load_src_json(f): 
    try: 
        with open(f, 'r') as fr: 
            json_dict = json.load(fr)
    except: 
        json_dict = dict()
    return json_dict

def get_key_value(term): 
    value = term.strip("\"").strip("\'").split("|")
    key_value = {}
    for v in value:
        prek,prev = v.split('=')
        if prev == 'None':
            prev = None
        elif prev == 'False' or prev == 'True':
            prev = _string2bool(prev)
        elif prev.isnumeric():
            prev = _num(prev)

        key_value[prek] = prev

    return key_value

def get_key(term): 
    value = term.strip("\"").strip("\'").split("|")
    key_value = {v: None for v in value}
    return key_value

def check_conflict(add_dict, rename_dict): 
    rename_list = rename_dict.values()
    add_list = add_dict.keys()
    inter = list(set(rename_list).intersection(set(add_list)))
    if not inter: 
        return add_dict, rename_dict
    else: 
        for c in inter: 
            add_dict.pop(c)
    return add_dict, rename_dict

def convert_dict(f): 
    json_dict = load_src_json(f)
    upgrade_api = dict()
    if not json_dict: 
        print("parser json dict error")
        exit(1)
    json_dict_src = json_dict["Sheet1"]
    for term in json_dict_src: 
        name = term.get("paddle.17", None)
        upgrade_name = term.get("paddle2.0", None)
        
        assert name, "old version doesn't exist"
        assert upgrade_name, "new version doesn't exist"
        add_dict = dict()
        if "add" in term: 
            add_dict = get_key_value(term["add"])

        rename_dict = dict()
        if "rename" in term: 
            rename_dict = get_key_value(term["rename"])
        
        delete_dict = dict()
        if "delete" in term: 
            delete_dict = get_key(term["delete"])

        if rename_dict and add_dict: 
            add_dict, rename_dict = check_conflict(add_dict, rename_dict)

        upgrade_api[name] = dict()
        upgrade_api[name]["name"] = upgrade_name
        if delete_dict: 
            upgrade_api[name]["delete"] = delete_dict
        if add_dict: 
            upgrade_api[name]["add"] = add_dict
        if rename_dict: 
            upgrade_api[name]["rename"] = rename_dict
    res = json.dumps(upgrade_api, sort_keys=True, indent=4)
    return res

if __name__ == "__main__": 
    # ../dict/data.json
    json_file = convert_dict(sys.argv[1])
    with open("../dict/modify.dict", "w") as outfile: 
        outfile.write(json_file) 
