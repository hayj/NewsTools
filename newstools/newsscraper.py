# coding: utf-8

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
from newspaper import Article
from datatools.jsonreader import *
from datatools.url import *
from datatools.csvreader import *
from systemtools.file import *
from systemtools.location import *
from systemtools.system import *
from nlptools.basics import *
import random
from enum import Enum
from boilerpipe.extract import Extractor
import html2text
from datatools.htmltools import *
# from newsplease import NewsPlease # To delete
# from readability import Document # To delete
from datastructuretools.processing import *

# def normalizeTextScraper(text):
#     if text is None or len(text) == 0:
#         return None
#     if text.count('<') > 5 and text.count('>') > 5:
#         text = html2Text(text)
#     text = reduceBlank(text, keepNewLines=True)
#     return text

def meanLinesLength(text):
    lines = text.split("\n")
    theSum = 0
    count = 0
    for line in lines:
        theSum += len(line)
        count += 1
    return theSum / count

def isGoodNews(data, minTextLength=100, minMeanLineLength=8, logger=None, verbose=True):
    try:
        if data is None:
            return False
        if dictContains(data, "status") and data["status"] not in \
        [
            "timeoutWithContent",
            "success",
        ]:
            return False
        scrap = data
        if dictContains(scrap, "scrap"):
            scrap = scrap["scrap"]
        if dictContains(scrap, "boilerpipe"):
            # logWarning("Old scrap")
            return False
            scrap = scrap["boilerpipe"]
        if not dictContains(scrap, "text") or not dictContains(scrap, "title"):
            return False
        if len(scrap["text"]) < minTextLength:
            return False
        if meanLinesLength(scrap["text"]) < minMeanLineLength:
            return False
        if len(scrap["title"]) == 0:
            return False
        loweredTitle = scrap["title"].lower()
        for exclude in \
        [
            "subscribe to read",
        ]:
            if exclude in loweredTitle:
                return False
    except Exception as e:
        logException(e, logger, verbose=verbose)
        return False
    return True



class NewsScraper():
    # goose doesn't work
    SCRAPLIB = Enum('SCRAPLIB', 'newspaper boilerpipe newsplease readability') # goose

    def __init__(self, logger=None, verbose=True):
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
            # SCRAPLIB.readability,
            # SCRAPLIB.newsplease,
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

    def smartScrap(self, html, winnerMinRatio=0.69, reduce=False, sentenceMinLength=30):
        try:
            scrap = self.scrapAll\
            (
                html,
                scrapLibs=\
                [
                    NewsScraper.SCRAPLIB.boilerpipe,
                    NewsScraper.SCRAPLIB.newspaper,
                    # SCRAPLIB.readability,
                    # SCRAPLIB.newsplease,
                ],
                reduce=reduce,
            )
            data = dict()
            data["title"] = None
            try:
                data["title"] = scrap["newspaper"]["title"]
            except: pass
            nText = None
            bText = None
            try:
                nText = scrap["newspaper"]["text"]
                del scrap["newspaper"]["text"]
            except: pass
            try:
                bText = scrap["boilerpipe"]["text"]
                del scrap["boilerpipe"]["text"]
            except: pass
            if nText is None or len(nText) == 0:
                nText = None
            if bText is None or len(bText) == 0:
                bText = None
            if nText is None and bText is None:
                data["text"] = None
            elif nText is None:
                data["text"] = bText
            elif bText is None:
                data["text"] = nText
            else:
                nText = nText
                bText = bText
                nTextOnlySentence = []
                for line in nText.split("\n"):
                    if len(line) > sentenceMinLength:
                        nTextOnlySentence.append(line)
                nTextOnlySentence = "\n".join(nTextOnlySentence)
                bTextOnlySentence = []
                for line in bText.split("\n"):
                    if len(line) > sentenceMinLength:
                        bTextOnlySentence.append(line)
                bTextOnlySentence = "\n".join(bTextOnlySentence)
                if len(nTextOnlySentence) + len(bTextOnlySentence) == 0:
                    nTextRatio = 0.5
                    bTextRatio = 0.5
                else:
                    nTextRatio = len(nTextOnlySentence) / (len(nTextOnlySentence) + len(bTextOnlySentence))
                    bTextRatio = len(bTextOnlySentence) / (len(nTextOnlySentence) + len(bTextOnlySentence))
                if nTextRatio > winnerMinRatio:
                    data["text"] = nText
                elif bTextRatio > winnerMinRatio:
                    data["text"] = bText
                else:
                    if meanLinesLength(bTextOnlySentence) > meanLinesLength(nTextOnlySentence):
                        data["text"] = bText
                    else:
                        data["text"] = nText
            data = mergeDicts(data, scrap["newspaper"], scrap["boilerpipe"])
            return data
        except Exception as e:
            logException(e, self)
            return None


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
                result["text"] = magicNormalizeText(result["text"])
            elif scrapLib == NewsScraper.SCRAPLIB.boilerpipe:
                scraper = Extractor(extractor='ArticleExtractor', html=html) # Or ArticleSentencesExtractor
                text = scraper.getText()
                text = magicNormalizeText(text)
                result = {"text": text} # "images": scraper.getImages()
                print("TODO TODO TODO TODO TODO TODO TODO TODO ")
                
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
                if dictContains(result, "text"):
                    newResult["text"] = result["text"]
                if dictContains(result, "title"):
                    newResult["title"] = result["title"]
                result = newResult
            return result
        except Exception as e:
            logException(e, self, location="scrap(self, scrapLib=SCRAPLIB.newspaper)")
        return None

# https://github.com/grangier/python-goose/zipball/master#egg=python-goose


# newsScraper = NewsScraper()

# def smartScrapAll(htmls):
#     global newsScraperSingleton
#     scraps = []
#     for html in htmls:
#         scraps.append(newsScraper.smartScrap(html))
#     return scraps

# def multiProcessingSmartScrap(htmls, parallelProcesses=cpuCount()):
#     htmlss = split(htmls, parallelProcesses)
#     pool = Pool(parallelProcesses, mapType=MAP_TYPE.multiprocessing)
#     scrapps = pool.map(smartScrapAll, htmlss)
#     scraps = []
#     for currentScraps in scrapps:
#         scraps += currentScraps
#     return scraps

if __name__ == '__main__':
    from hjwebbrowser.httpbrowser import *
    b = HTTPBrowser(pageLoadTimeout=20)
    html = b.get("https://fr.wikipedia.org/wiki/Grand_veneur_de_France")["html"]
    # print({**None, **{"t": 1}})
    # html = fileToStr(getExecDirectory() + "/data-test/bbc-cookie.html")
    ns = NewsScraper()
    # scrap = ns.scrap(scrapLib=NewsScraper.SCRAPLIB.readability)
    scrap = ns.scrapAll(html)
    print(listToStr(scrap))


