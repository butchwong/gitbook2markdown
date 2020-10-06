# gitbook2markdown
> 将gitbook网页格式 转换 为markdown 格式笔记

## 依赖
需要在环境中安装 PhantomJS
```
pip install html2text
pip install selenium
```

## 执行方式
```
python gitbook2md.py url路径 目标目录
```

如 `python gitbook2md.py  http://127.0.0.1:5500 md`

## 文本删除工具
> 自动查找`.md `文件，并删除前后的无用行
```
python separator.py 目录 待删除的前n行 待删除的后m行
```
如 `python separator.py md 80 3`