# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
import os, re
from datetime import datetime
import pandas as pd
import time

from SO_scraper.items import SOScraperItem

'''
1. Title of article
2. Year of article
3. Author of article
4. Preview text of article

Ideally, the database will contain these fields as well:

1. Publication name of article
2. Abstract of article, located inside the link.
'''


class SOSpider(scrapy.Spider):
    name = 'SO'
    allowed_domains = ['stackoverflow.com']
    start_urls = []
    switch = True
    tag = None

    def __init__(self):
        self.create_result_file()

    def start_requests(self):
        # this_year = datetime.now().year
        tag_df = pd.read_csv('tags.csv')
        tags = list(tag_df['TagName'])
        urls = list(tag_df['url'])
        searches = [link for link in urls]

        self.switch = True
        for tag, search in zip(tags[1000:], searches[1000:]):
            page = 1
            start_url = search.format(page)
            request = FormRequest(
                url=start_url,
                method="GET",
                callback=self.parse,
                meta={
                    'page': page,
                    'search': search,
                    'tag': tag,
                    'switch': True
                }
            )

            yield request

    def parse(self, response):
        page = response.meta['page']
        search = response.meta['search']
        tag = response.meta['tag']
        switch = response.meta['switch']

        rows = response.xpath('//div[@class="question-summary"]')
        for row in rows:
            url = row.xpath('.//a[@class="question-hyperlink"]//text()').extract()
            votes = row.xpath('.//span[contains(@class, "vote-count-post ")]//strong//text()').extract()
            answers = row.xpath('.//div[contains(@class, "status")]//strong//text()').extract()
            date = row.xpath('.//span[@class="relativetime"]//text()').extract()

            print("You're scraping this url:\t", response.url)

            if re.search(r"'17", date[0]):
                switch = False
                break

            result_row = [
                tag, url[0], votes[0], answers[0], date[0]
            ]
            print(result_row)

            result_row = [elm if elm else '' for elm in result_row]
            self.insert_row(result_row=result_row)

            item = SOScraperItem()
            item['tag'] = tag
            item['url'] = url[0]
            item['votes'] = votes[0]
            item['answers'] = answers[0]
            item['date'] = date[0]
            print(response.url)
            print(item)
            yield item

        if switch and rows:
            page += 1
            start_url = search.format(page)
            request = FormRequest(
                url=start_url,
                method="GET",
                callback=self.parse,
                meta={
                    'page': page,
                    'search': search,
                    'tag': tag,
                    'switch': True
                }
            )

            yield request

    def create_result_file(self):
        heading = [
            "tag", "url", "votes", "answers", "date"

        ]

        import codecs
        python_file_name = os.path.basename(__file__)
        result_file_name = python_file_name.replace(".py", ".csv")
        self.result_file = codecs.open(result_file_name, "a", "utf-8")
        self.result_file.write(u'\ufeff')
        self.insert_row(heading)

    def insert_row(self, result_row):
        self.result_file.write('"' + '","'.join(result_row) + '"' + "\n")
        self.result_file.flush()


# scrapy crawl SO -s LOG_ENABLED=False


if __name__ == '__main__':
    from scrapy.utils.project import get_project_settings
    from scrapy.crawler import CrawlerProcess, CrawlerRunner

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(SOSpider)
    process.start()
