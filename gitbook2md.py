import requests
from selenium import webdriver
import html2text
from lxml import etree
import re
import sys
import os
import json
from urllib.parse import urljoin

class Gitbook2Markdown(object):
    def __init__(self, path, dir_name):
        self.path = path
        self.index = path if path.endswith('/index.html') else path + '/index.html'
        # self.driver = webdriver.Chrome()
        self.dir_name = dir_name

        self.driver = webdriver.PhantomJS()
        self.h = html2text.HTML2Text()

        self.driver.get(self.index)
        index_html_str = self.driver.page_source
        index_html = etree.HTML(index_html_str)
        self.pre_li = index_html.xpath('//nav/ul[@class="summary"]/li[contains(@class, "chapter")]')

        self.p_dot = re.compile(r'(\.)?$')
        self.p_s = re.compile(r'\s+')


    def __del__(self):
        self.driver.quit()
        self.h.close()

    # 传入每个导航li标签，fileMapUrl_list 中存放目标md文件路径，url
    def parse_li(self, li, prepath_dir, fileMapUrl_list):
        seq = li.xpath('./a/b/text()')
        seq = seq[0] if len(seq) > 0 else '0'
        seq = self.p_dot.sub('_', seq)

        subject = li.xpath('./a/text()')
        subject = ''.join(subject)
        subject = self.p_s.sub('', subject)

        url = li.xpath('./a/@href')
        url = url[0] if len(url) > 0 else 'index.html'
        url = self.path.replace('/index.html', '') + url.replace('./', '/')

        # 判断是否存在子标题
        if len(li.xpath('./ul/li[contains(@class, "chapter")]')) != 0:
            sub_lis = li.xpath('./ul/li[contains(@class, "chapter")]')
            # 修改当前的路径
            prepath_dir += '/' + seq + subject
            # 修改当前的seq 若1_ 存在子标题，则改为1.0_
            # 当1_xx 存在子标题，路径由{prepath_dir}/1_xx.md改为{prepath_dir}/1_xx/1.0_xx.md
            seq = seq.replace('_', '.0_')
            for sub_li in sub_lis:
                self.parse_li(sub_li, prepath_dir, fileMapUrl_list)

        file_name = prepath_dir + '/' + seq + subject + '.md'
        html_str = requests.get(url).content.decode()
        html = etree.HTML(html_str)
        img_urls = html.xpath('//img/@src')
        imgs = [{'img_file': prepath_dir + '/' + i, 'img_url': urljoin(url,i)} for i in img_urls]
        fileMapUrl_list.append({'file_name': file_name, 'url': url, 'prepath_dir': prepath_dir, 'imgs': imgs})

        md_str = self.trans_html_to_md(html_str)
        self.save_md_content(md_str, file_name)

    def check_pre_path(self, path):
        dir_name = os.path.dirname(path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name, exist_ok=True)

    def save_img(self, img_url, img_path):
        self.check_pre_path(img_path)
        img = requests.get(img_url).content
        with open(img_path, 'wb') as f:
            f.write(img)

    def trans_html_to_md(self, html_str):
        return self.h.handle(html_str)

    def save_md_content(self, md_str, file_name):
        self.check_pre_path(file_name)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(md_str)

    def run(self):
        fileMapUrl_list = []
        for li in self.pre_li:
            self.parse_li(li, self.dir_name, fileMapUrl_list)

        with open('./files.json', 'w', encoding='utf-8') as f:
            json.dump(fileMapUrl_list, f, ensure_ascii=False, indent=2)

        img_list = [img for chapter in fileMapUrl_list for img in chapter['imgs']]
        with open('./imgs.json', 'w', encoding='utf-8') as f:
            json.dump(img_list, f, ensure_ascii=False, indent=2)

        for img in img_list:
            self.save_img(img['img_url'], img['img_file'])

        print('执行完毕')

if __name__ == "__main__":
    # path = 'http://127.0.0.1:5500'

    if len(sys.argv) < 3:
        print('请输入路径和目标目录')
        exit()

    index_url = sys.argv[1]
    dir_name = sys.argv[2]
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        print('目标目录不存在，自动创建目录：', dir_name)

    md = Gitbook2Markdown(index_url, dir_name)
    md.run()