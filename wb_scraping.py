import grequests
import shutil
import requests
import os

from lxml import html
from urllib.parse import urlparse


class WebDownload:
    def __init__(self, urls, save_path):
        self.action(urls, save_path)

    def action(self, urls, save_path):

        for file in urls:
            self.filename_save_name = file[file.rfind("/") + 1:]
            self.response = requests.get(file, stream=True)

            if self.response.status_code == 200:
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                with open(save_path + self.filename_save_name, 'wb') as out_file:
                    shutil.copyfileobj(self.response.raw, out_file)
                del self.response


class WebScrapping:
    response_sites = []
    reqs = []
    status_code = None
    agent_win_os = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
    header = {'User-Agent': agent_win_os}
    url = None
    xpath_strings = None
    def __init__(self, urls, xpath_strings):
        self.xpath_strings = xpath_strings
        self.action(urls)

    def action(self, urls):
        for self.url in urls:
            self.reqs.append(grequests.get(self.url, proxies=None, headers=self.header,
                                           allow_redirects=False, hooks={'response': self.callback}))
            grequests.map(self.reqs, exception_handler=self.exception_handler, size=50, gtimeout=5, stream=False)

    def callback(self, response, **kwargs):
        self.status_code = response.status_code
        self.response_text = html.fromstring(response.text)
        #response.css('img').xpath('@src').extract()
        for url_file in self.response_text.xpath(self.xpath_strings):
            if url_file not in self.response_sites and str(url_file).startswith("htt"):
                self.response_sites.append(url_file)
            else:
                # TODO: example img=ocdn.eu/static/ucs/NDc7MDA_/b89eda87119432d976737840e84cf8b5/images/icons/cat_icn_more.png
                #      ne pripada domeni sa koje skida - nema http:// il https://
                #      tesko odrediti da li da se doda u listu
                #      example    img=./path/pic.jpg  -> ne znam da li uopste parsira.

                self.file_format_tocheck = ['.jpg', '.png']
                self.url_check = str(url_file)
                if self.url_check.endswith(tuple(self.file_format_tocheck)):
                    self.url_parse = urlparse(str(self.url))
                    self.http_domain = self.url_parse.scheme + "://" + self.url_parse.netloc + "/"
                    self.response_sites.append(self.http_domain + str(url_file))

    def exception_handler(self, request, exception):
        print('Grequests Exception on: ' + str(exception))

    def get_response_sites(self):
        return self.response_sites

    def get_response_code(self):
        return self.status_code


blog = WebScrapping(['https://www.vladimircicovic.com'] , '//img/@src')

result_list = None
if blog.get_response_code() == 200:
    result_list = blog.get_response_sites()

if not result_list == None:
    download_file = WebDownload(result_list, "/tmp/tt/")
