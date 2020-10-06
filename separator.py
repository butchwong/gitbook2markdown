#!/usr/bin/env python3
# coding=utf-8
"""
Author: butchwong
Date: 2020-10-06 16:39:57
LastEditors: butchwong
LastEditTime: 2020-10-06 18:10:04
"""
import os
import sys
import re
import json


def recursive_find_helper(path, target, res):
    items = [path + "/" + item for item in os.listdir(path)]
    p = re.compile(target)
    for item in items:
        if p.search(item):
            res.append(item)
        if os.path.isdir(item):
            recursive_find_helper(item, target, res)


def recursive_find():
    res = []
    recursive_find_helper(path, r'.*\.md', res)
    return res


def separator(file, n, m):
    with open(file, "r+", encoding="utf-8") as f:
        content_list = f.readlines()
        l = len(content_list)
        new_content = "".join(content_list[n : l - m])
        # 读取完文件之后，指针移动到文件尾部，重新移动指针到头部，以便重头写入数据
        f.seek(0)
        # 清空文件
        f.truncate()
        f.write(new_content)


if __name__ == "__main__":
    if (
        len(sys.argv) < 4
        or not os.path.isdir(sys.argv[1])
        or not re.match(r"^\d+$", sys.argv[2])
        or not re.match(r"^\d+$", sys.argv[3])
    ):
        print("请输入目录 待删除的前n行 待删除的后m行")
        exit()

    path = sys.argv[1]
    n = int(sys.argv[2])
    m = int(sys.argv[3])

    res = recursive_find()
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("文件个数", len(res))

    for item in res:
        print(item)
        separator(item, n, m)

    print("执行完成")
