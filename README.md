# NewsScraper

This tool is useful to detect news URLs. It also aggregates several libraries which scrap news web pages (title, content...).

## Install

	git clone https://github.com/hayj/NewsTools.git
	pip install ./NewsTools/wm-dist/*.tar.gz

newspaper3k and news-please doesn't work in requirements.txt, produce `bad marshall data`
So you need to install it manually:

	pip install https://github.com/misja/python-boilerpipe/zipball/master#egg=python-boilerpipe
	pip install newspaper3k
	pip install news-please

Then you need to get data in the data dir.

## Usage

### NewsScraper

You can easily use different news scraper this way:

	from newstools.newsscraper import *
	ns = NewsScraper()
	newspaperData = ns.scrap(html, html, scrapLib=SCRAPLIB.newspaper)
	boilerpipeData = ns.scrap(html, html, scrapLib=SCRAPLIB.boilerpipe)
	allScraps = ns.scrapAll()

### NewsURLFilter

This tool allow you to check if an url is a news url according to known domains. You have to get the data dir. You can give a [Unshortener](https://github.com/hayj/Unshortener) from unshortener.unshortener to also check if a shortened url (bit.ly, tinyurl.com...) are news. It use PublicSuffixList to know domains.

Import it

	from newstools.newsurlfilter import *

Init a NewsURLFilter instance:

	nuf = NewsURLFilter\
	(
		dataLocation="../../data", # get the data from the data dir on github
		unshortener=None, # You can give an Unshortener or it will try to auto init one instance of Unshortener
		useUnshortener=True, # or you can set this param as False if you don't want to use an Unshortener
	)

Then you can use `isNews` method:

	>>> nuf.isNews("https://www.nytimes.com/XXXX")
	True
	>>> nuf.isNews("https://www.nytimes.com/X")
	False
	>>> nuf.isNews("https://www.google.com/XXXXX")
	False
	>>> nuf.isNews("https://www.nytimes.com/XXXXX.jpg")
	False
	>>> nuf.isNews("https://www.huffingtonpost.fr/XXXX")
	True

You can get all news domains using:

	nuf.newsDomains

