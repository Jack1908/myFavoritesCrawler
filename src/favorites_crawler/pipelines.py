# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from pathlib import Path

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter
from twisted.python.failure import Failure

from favorites_crawler.utils.files import create_comic_archive


logger = logging.getLogger(__name__)


class FavoritesFilePipeline(FilesPipeline):

    def __init__(self, store_uri, **kwargs):
        super().__init__(store_uri, **kwargs)
        self.files_path = Path(store_uri).resolve()
        self.comic_comments = {}

    def close_spider(self, spider):
        for title, comment in self.comic_comments.items():
            folder = self.files_path / title
            if not folder.exists():
                continue
            try:
                create_comic_archive(folder, comment=comment)
            except FileNotFoundError:
                pass

    def process_item(self, item, spider):
        if hasattr(item, 'get_comic_info'):
            title = item.get_folder_name(spider)
            if (self.files_path / f'{title}.cbz').exists():
                raise DropItem(f'Comic file of "{title}" already exist, stop download this comic.')
            comment = item.get_comic_info()
            self.comic_comments[title] = bytes(comment, encoding='utf-8')

        return super().process_item(item, spider)

    def get_media_requests(self, item, info):
        item_dict = ItemAdapter(item).asdict()
        referer = item_dict.get('referer')
        return (Request(url, headers={'referer': referer}) for url in item_dict.get(self.files_urls_field, ()))

    def file_path(self, request, response=None, info=None, *, item=None):
        return item.get_filepath(request.url, info.spider)

    def item_completed(self, results, item, info):
        for result in info.downloaded.values():
            if isinstance(result, Failure):
                logger.error('Error when downloading file: %s', result.value)
        return super().item_completed(results, item, info)
