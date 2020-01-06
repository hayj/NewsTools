
# Good Article Tool

This tool is a predictor to filter news dataset, it allow you to assess wether a text is a good article or not (according to he format...).

First import the tool:

	from newstools.goodarticle.utils import *

Then clean your document:

	text = newsPreclean(text)

Then predict if it is a good article or not:

	print(isGoodArticle(text))

See `test.py`.