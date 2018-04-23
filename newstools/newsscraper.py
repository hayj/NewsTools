# coding: utf-8

from newspaper import Article
from datatools.json import *
from datatools.url import *
from datatools.csvreader import *
from systemtools.file import *
from systemtools.location import *
from systemtools.system import *
import random
from enum import Enum
from readability import Document
from boilerpipe.extract import Extractor
import html2text
from newsplease import NewsPlease


class NewsScraper():
    # goose doesn't work
    SCRAPLIB = Enum('SCRAPLIB', 'newspaper boilerpipe newsplease readability') # goose

    def __init__(self, logger=None, verbose=True): #
        self.logger = logger
        self.verbose = verbose

    def scrapAll\
    (
        self,
        *args,
        scrapLibs=\
        [
            SCRAPLIB.boilerpipe,
            SCRAPLIB.newspaper,
        ],
        **kwargs
    ):
        if scrapLibs is None:
            scrapLibs = NewsScraper.SCRAPLIB
        scrap = {}
        for current in scrapLibs:
            currentScrap = self.scrap(*args, scrapLib=current, **kwargs)
            if currentScrap is not None:
                scrap = {**scrap, **{current.name: currentScrap}}
        return scrap

    def scrap(self, html, scrapLib=SCRAPLIB.newspaper, reduce=True):
        if html is None or html == "":
            return None
        try:
            if scrapLib == NewsScraper.SCRAPLIB.newspaper:
                url = ''
                article = Article(url)
                article.download(input_html=html)
                article.parse()
                result = \
                {
                    "title": article.title,
                    "text": article.text,
                    "publish_date": article.publish_date,
                    "authors": article.authors,
                    "tags": article.tags,
                    "meta_description": article.meta_description,
                    "meta_lang": article.meta_lang,
                    "meta_favicon": article.meta_favicon,
                    "meta_data": article.meta_data,
                }
            elif scrapLib == NewsScraper.SCRAPLIB.boilerpipe:
                scraper = Extractor(extractor='ArticleExtractor', html=html)
                scrap = scraper.getText()
                result = {"text": scrap}
            elif scrapLib == NewsScraper.SCRAPLIB.newsplease:
                article = NewsPlease.from_html(html)
                result = \
                {
                    "authors": article.authors,
                    "download_date": article.date_download,
                    "modify_date": article.date_modify,
                    "publish_date": article.date_publish,
                    "description": article.description,
                    "image_url": article.image_url,
                    "language": article.language,
                    "localpath": article.localpath,
                    "source_domain": article.source_domain,
                    "text": article.text,
                    "title": article.title,
                    "title_page": article.title_page,
                    "title_rss": article.title_rss,
                }
            elif scrapLib == NewsScraper.SCRAPLIB.readability:
                doc = Document(html)
                result = \
                {
                    "title": doc.title(),
                    "text": html2text.html2text(doc.content()),
                }
            else:
                result = None
            if result is not None and reduce:
                newResult = {}
                newResult["text"] = result["text"]
                newResult["title"] = result["title"]
                result = newResult
            return result
        except Exception as e:
            logException(e, self, location="scrap(self, scrapLib=SCRAPLIB.newspaper)")
        return None

# https://github.com/grangier/python-goose/zipball/master#egg=python-goose

if __name__ == '__main__':
#     print({**None, **{"t": 1}})
    html = fileToStr(getExecDirectory() + "/data-test/bbc-cookie.html")
    ns = NewsScraper(html)
#     scrap = ns.scrap(scrapLib=NewsScraper.SCRAPLIB.readability)
    scrap = ns.scrapAll()
    print(listToStr(scrap))


