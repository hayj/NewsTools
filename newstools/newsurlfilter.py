# coding: utf-8

from systemtools.basics import *
from datatools.jsonreader import *
from datatools.url import *
from datatools.csvreader import *
from systemtools.file import *
from systemtools.location import *
from systemtools.system import *
try:
    from unshortener.unshortener import *
except: pass
import random
from newstools import config as ntConf


def langContains(text, filter, useOr=True):
    if filter is None or len(filter) == 0:
        return False
    if not useOr:
        raise Exception("Not yet implemented!")
    for current in filter:
        if current in text:
            return True
    return False

class NewsURLFilter():
    def __init__(self,
                 dataLocation=None,
                 verbose=True,
                 logger=None,
                 unshortener=None,
                 useUnshortener=True,
                 unshortenerReadOnly=False,
                 langFilter=None,
                 websitesPattern="/*.csv",
                 excludePattern="/exclude*.txt",
                 startswithExclude="/startswith-exclude.txt"):
        """
            This function init all known news and blog website (smart domains, see URLParser with public prefix)
            which are in english
            and which are not aggregator
            and which are not in exclude*.txt
        """
        self.langFilter = langFilter
        if self.langFilter is None:
            self.langFilter = ntConf.langFilter
        self.logger = logger
        self.verbose = verbose
        self.unshortener = unshortener
        self.unshortenerReadOnly = unshortenerReadOnly
        if self.unshortener is None and useUnshortener:
            try:
                self.unshortener = Unshortener(logger=self.logger, verbose=self.verbose,
                                               readOnly=self.unshortenerReadOnly)
            except Exception as e:
                logException(e, self, location="Unshortener init in NewsURLFilter __init__")
        if dataLocation is None:
            dataLocation = dataDir() + "/Misc/news-website-list/data"
        # We handle paths:
        websitesPattern = dataLocation + websitesPattern
        excludePattern = dataLocation + excludePattern
        allDataPaths = sortedGlob(websitesPattern)
        allExcludePaths = sortedGlob(excludePattern)
        self.newsDomains = []
        self.urlParser = URLParser(logger=self.logger, verbose=self.verbose)
        # We get all web sites (en and not an aggregator):
        for filePath in allDataPaths:
            cr = CSVReader(filePath)
            for row in cr:
                if  "lang" in row and langContains(row["lang"], self.langFilter) and ("website_type" not in row or row["website_type"] != "aggregator"):
                    currentSmartDomain = self.urlParser.getDomain(row["url"], urlLevel=URLLEVEL.SMART)
                    if currentSmartDomain is not None and currentSmartDomain != "":
                        self.newsDomains.append(currentSmartDomain)
        self.newsDomains = set(self.newsDomains) # set is a hastable, so key access in O(1)
        # Then we exlude all in exclude.txt:
        for currentExcludePath in allExcludePaths:
            excludeList = fileToStrList(currentExcludePath)
            for currentExclude in excludeList:
                currentExclude = currentExclude.strip()
                if currentExclude != "":
                    currentExclude = self.urlParser.getDomain(currentExclude, urlLevel=URLLEVEL.SMART)
                    if currentExclude in self.newsDomains:
                        self.newsDomains.remove(currentExclude)
#         strToFile(list(self.newsDomains), "/home/hayj/test.txt")
#         exit()
        startswithExcludeTmp = fileToStrList(dataLocation + startswithExclude)
        self.startswithExclude = []
        for current in startswithExcludeTmp:
            current = current.strip()
            if current != "":
                self.startswithExclude.append(current)



    def isNews(self, url, minRightPartSize=4):
        """
            This function exclude all link which are None or ""
            and which starts with a string in startswith-exclude.txt
            and which have a len right part of the url lower than 3
            and which are not in all newsDomains
            and which are image
            This function also check if there is a unshorted url of the current url
            if self.unshortener is not None
        """
        url = self.urlParser.normalize(url)
        smartDomain = self.urlParser.getDomain(url, urlLevel=URLLEVEL.SMART)
        if url is None or url == "":
            return False
        if self.unshortener is not None:
            if smartDomain not in self.newsDomains:
                if self.unshortener.isShortener(url):
                    lastUrl = self.unshortener.unshort(url)
                    if lastUrl is not None:
                        url = lastUrl
        parsedUrl = self.urlParser.parse(url)
        for currentStartswithExclude in self.startswithExclude:
            if parsedUrl.netloc.startswith(currentStartswithExclude):
                return False
        right = parsedUrl.path + parsedUrl.params + parsedUrl.query + parsedUrl.fragment
        if len(right) <= minRightPartSize:
            return False
        if self.urlParser.isImage(url) or self.urlParser.isDocument(url):
            return False
        smartDomain = self.urlParser.getDomain(url, urlLevel=URLLEVEL.SMART)
        return smartDomain in self.newsDomains



if __name__ == '__main__':
    nuf = NewsURLFilter(langFilter="fr")
    strListToTmpFile(list(nuf.newsDomains), "newsdomains.txt")
    print(nuf.isNews("http://www.businessinsider.fr/classement-salaires-nets-moyens-dans-40-pays/"))








