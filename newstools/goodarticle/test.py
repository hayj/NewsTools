# pew in st-venv python ~/Workspace/Python/Crawling/NewsTools/newstools/goodarticle/test.py

from newstools.goodarticle.utils import *
from systemtools.hayj import *
from systemtools.basics import *
from systemtools.file import *
from systemtools.printer import *
from systemtools.logger import *
from annotator.annot import *
from datatools.jsonutils import *
from nlptools.tokenizer import *
from datatools.htmltools import *

if __name__ == '__main__':
	data = []
	for file in sortedGlob(getExecDir(__file__) + "/goodarticle*.json"):
		data += fromJsonFile(file)
	for i in range(len(data)):
		data[i]["text"] = newsPreclean(data[i]["text"])
	wellClassified = 0
	for current in data:
		isGoodPrediction = isGoodArticle(current["text"])
		isGoodTrueLabel = current["relevance"] > 0.5
		if isGoodPrediction == isGoodTrueLabel:
			wellClassified += 1
	print("Well classified ratio: " + str(wellClassified / len(data)))