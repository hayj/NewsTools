
# pew in st-venv python ~/Workspace/Python/Datasets/Annotator/annotation/goodarticle.py


from systemtools.hayj import *
from systemtools.basics import *
from systemtools.file import *
from systemtools.printer import *
from systemtools.logger import *
from annotator.annot import *
from datatools.jsonutils import *
from nlptools.tokenizer import *



"""
	Règles de filtrage
	On supprime toutes les lignes qui contiennent ce qu'il y a dans generalmanual filter
	On supprime les lignes qui n'ont que 2 tokens
	Les lignes qui n'ont pas beaucoup de mots

	les docs qui n'ont pas beaucoup de phrase longure


	les phrase qui contiennent des email
	les phrases qui contiennent dezs urls
	qui ont un overlap de 2 grams et  1 gram enorme
	les phrases qui contiennent des mots uniquement en maj (sauf si c'est des acronyme genre N.C.A.A. ou USA)
	les phrase qui contiennt bcp de non word
	les phrase qui contiennent des fail d'encodage "the nationâs capital in 2014, one of 2,178"


	on filtre les docs, il faut au moins 3 sentences, et une longueur de sentence moyenne entre 6 et 40
	Les docs qui ont beaucoup de Advertisements
	
	
"""

# To handle test:
TEST = False
if TEST:
	dbname = "goodarticle-test"
else:
	dbname = "goodarticle"

# Misc vars:
skipRatio = 0.98

# Data dir:
files = sortedGlob(dataDir() + "/News/*newsan*" + "/*.bz2")

def dataGenerator():
	global files
	global skipRatio
	for file in files:
		for row in NDJson(file):
			if getRandomFloat() > skipRatio:
				o = {"id": None, "content": {"title": row["domain"]}}
				o["content"]["text"] = str(row["title"]) + "\n" * 3 + str(row["text"])
				o["meta"] = dict()
				for key in ["dataset", "domain", "authors", "url", "title", "text"]:
					o["meta"][key] = None
					if dictContains(row, key):
						o["meta"][key] = row[key]
				yield o



def test():
	i = 0
	for row in dataGenerator():
		bp(row, 5)
		if i == 10:
			break
		i += 1


def launch():
	# Labels:
	labels = \
	{
		"relevance": {"title": "Set the relevance for a style analysis. 1.0 means these docments are very relevant to be included in our style study. The text must be article about a subject, well formated...", "type": LABEL_TYPE.scale},
	}

	# We set the logger:
	logger = Logger("goodarticle.log")

	# We launch the Annotator:
	an = Annotator(dbname, labels, useMongodb=True, logger=logger)
	if TEST:
		an.reset()
	# an.start(dataGenerator())

	if True:
		data = an.getData()
		rows = []
		for key, value in data.items():
			row = value["meta"]
			row["relevance"] = value["relevance"]
			rows.append(row)
		toJsonFile(rows, homeDir() + "/goodarticle2.json")

if __name__ == "__main__":
	launch()