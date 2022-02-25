# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter


class YandreFilesPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        item_dict = ItemAdapter(item).asdict()
        return [Request(item_dict['file_url'])]

    def file_path(self, request, response=None, info=None, *, item=None):
        return os.path.join('Yandere', item.get_filename())


class CollectionFilePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        item_dict = ItemAdapter(item).asdict()
        referer = item_dict.get('referer')
        return (Request(url, headers={'referer': referer}) for url in item_dict.get('image_urls', ()))

    def file_path(self, request, response=None, info=None, *, item=None):
        return item.get_filepath(request.url)
