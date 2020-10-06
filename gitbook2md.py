import requests
from selenium import webdriver
import html2text
from lxml import etree
import re
import sys
import os


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
        self.li_nodes = index_html.xpath('//nav/ul[@class="summary"]//li')

        self.p_dot = re.compile(r'(\.)?$')
        self.p_s = re.compile(r'\s+')

    def __del__(self):
        self.driver.quit()
        self.h.close()

    # 传入每个导航li标签，返回序号，标题，url
    def parse_li(self, li):
        seq = li.xpath('./a/b/text()')
        seq = seq[0] if len(seq) > 0 else '0'
        seq = self.p_dot.sub('_', seq)

        subject = li.xpath('./a/text()')
        subject = ''.join(subject)
        subject = self.p_s.sub('', subject)

        url = li.xpath('./a/@href')
        url = url[0] if len(url) > 0 else 'index.html'
        url = self.path.replace('/index.html', '') + url.replace('./', '/')
        return (seq, subject, url)

    def trans_html_to_md(self, html_str):
        return self.h.handle(html_str)

    def saveContent(self, file_name, md_str):
        with open(self.dir_name + '/' + file_name, 'w', encoding='utf-8') as f:
            f.write(md_str)
            print(md_str)

    def run(self):
        for li in self.li_nodes:
            seq, subject, url = self.parse_li(li)
            if subject == 'PublishedwithGitBook' or subject == '':
                continue
            file_name = seq + subject + '.md'
            html_str = requests.get(url).content.decode()
            md_str = self.trans_html_to_md(html_str)
            self.saveContent(file_name, md_str)

            print('file_name', file_name)
            print('url', url)

        print('执行完毕')

if __name__ == "__main__":
    # path = 'http://127.0.0.1:5500'

    if len(sys.argv) < 3:
        print('请输入路径和目标目录')
        exit()

    index_url = sys.argv[1]
    dir_name = sys.argv[2]
    if not os.path.isdir(dir_name):
        print('目标目录不存在')
        exit()

    md = Gitbook2Markdown(index_url, dir_name)
    md.run()