# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from string import ascii_uppercase
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import random
import requests

class StackoverflowSpider(scrapy.Spider):
    name = 'stackoverflow'
    allowed_domains = ['stackoverflow.com']
    start_urls = []

    proxy_file_name = 'proxy_http_ip.txt'
    PROXIES = []
    with open(proxy_file_name, 'rb') as text:
        PROXIES = ["http://" + x.decode("utf-8").strip() for x in text.readlines()]

    def __init__(self):
        self.total_cnt = 0

    def start_requests(self):
        pass

    def parse(self, response):
        pass

    def create_result_file(self, result_file_name):
        heading = [

        ]

        import codecs
        self.result_file = codecs.open(result_file_name, "w", "utf-8")
        self.result_file.write(u'\ufeff')
        self.insert_row(result_row=heading)

    def insert_row(self, result_row):
        self.result_file.write('"' + '","'.join(result_row) + '"' + "\n")
        self.result_file.flush()