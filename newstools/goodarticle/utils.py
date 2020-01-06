from systemtools.hayj import *
from systemtools.basics import *
from systemtools.file import *
from systemtools.printer import *
from systemtools.logger import *
from annotator.annot import *
from datatools.jsonutils import *
from nlptools.tokenizer import *
from datatools.htmltools import *
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR, LinearSVC
from sklearn import linear_model
from sklearn.model_selection import StratifiedKFold
import re



startswithExcludesSingleton = None
def newsPreclean(text, logger=None, verbose=True):
    global startswithExcludesSingleton
    if startswithExcludesSingleton is None or len(startswithExcludesSingleton) == 0:
        startswithExcludesSingleton = set(fileToStrList(getExecDir(__file__) + "/startswith-excludes.txt"))
    text = reduceBlank(text, keepNewLines=True)
    lines = [e for e in text.split("\n") if e != '']
    newLines = []
    for line in lines:
        if hasLetter(line):
            tokens = line.split(" ")
            found = False
            token = None
            for index in range(len(tokens)):
                token = tokens[index]
                if hasLetter(token):
                    found = True
                    break
            if found and token is not None:
                truncatedLine = re.search(re.escape(token) + ".*$", line).group(0)
                found = False
                for exclude in startswithExcludesSingleton:
                    if truncatedLine.startswith(exclude):
                        found = True
                        break
                if not found:
                    newLines.append(line)
    return "\n".join(newLines)


goodArticleModelSingleton = None
stopwordsSingleton = None
startswithExcludesSingleton = None
def isGoodArticle(text, logger=None, verbose=True):
    global goodArticleModelSingleton
    global stopwordsSingleton
    if text is None or len(text) < 10:
        return False
    if goodArticleModelSingleton is None:
        goodArticleModelSingleton = deserialize(getExecDir(__file__) + "/best.pickle")
    if stopwordsSingleton is None:
        stopwordsSingleton = set(fileToStrList(getExecDir(__file__) + "/stopwords.txt"))
    features = basicFeatures(text, stopwords=stopwordsSingleton)
    prediction = goodArticleModelSingleton.predict(np.array([features]))[0]
    return prediction == 1


def basicFeatures\
(
    text,
    longLine=140,
    shortLine=20,
    tooLongDocument=60000,
    stopwords={},
    punct={',', ')', '...', "'", ';', '-', '!', ':', '?', '"', '.', '('},
    logger=None,
    verbose=True,
    asDict=False,
    asNpArray=True,
):
    # Checking vars:
    if stopwords is None or len(stopwords) == 0 or punct is None or len(punct) == 0:
        logWarning("Please give a stopwords list and a punct list", logger, verbose=verbose)
    features = OrderedDict()
    # Too long document ?
    features["tooLongDocument"] = len(text) >= tooLongDocument
    # Len of the text:
    features["length"] = len(text)
    # The count of non-blank lines:
    lines = [e for e in text.split("\n") if e != '']
    features["linesCount"] = len(lines)
    # The count of tokens:
    loweredText = text.lower()
    tokens = [e for e in text.split() if e != '']
    loweredTokens = [e for e in loweredText.split() if e != '']
    features["tokensCount"] = len(tokens)
    # Count of long lines, mean lines length, count of short lines:
    longLinesCount = 0
    shortLinesCount = 0
    meanLinesLength = 0
    for line in lines:
        if len(line) >= longLine:
            longLinesCount += 1
        if len(line) <= shortLine:
            shortLinesCount += 1
        meanLinesLength += len(line)
    meanLinesLength = meanLinesLength / len(lines)
    features["longLinesCount"] = longLinesCount
    features["shortLinesCount"] = shortLinesCount
    features["meanLinesLength"] = meanLinesLength
    features["longLinesRatio"] = longLinesCount / len(lines)
    features["shortLinesRatio"] = shortLinesCount / len(lines)
    # The ratio of stopwords / punct:
    stopwordsAndPunct = stopwords.union(punct)
    c = len([e for e in loweredTokens if e in stopwordsAndPunct])
    features["stopwordsPunctRatio"] = c / len(loweredTokens)
    # The mean overlap:
    nonSWPTokens = [e for e in loweredTokens if e not in stopwordsAndPunct]
    c = dict()
    for token in nonSWPTokens:
        if token not in c:
            c[token] = 0
        c[token] += 1
    theMean = 0
    for token, count in c.items():
        theMean += count
    if len(c) == 0:
        theMean = 0.0
    else:
        theMean = theMean / len(c)
    features["nonSWPMeanOverlap"] = theMean
    # Ratio of only uppercased words:
    upperWordCount = len([e for e in tokens if hasLetter(e) and not hasLowerLetter(e)])
    features["upperWordCount"] = upperWordCount
    features["upperWordRatio"] = upperWordCount / len(tokens)
    # Ratio of non words:
    nonWordCount = len([e for e in tokens if not hasLetter(e)])
    features["nonWordCount"] = nonWordCount
    features["nonWordRatio"] = nonWordCount / len(tokens)
    # Ratio of html:
    htmlCharCount = len(text) - len(html2Text(text))
    if htmlCharCount < 0:
        htmlCharCount = 0
    features["htmlCharCount"] = htmlCharCount
    features["htmlCharRatio"] = htmlCharCount / len(text)
    # Ratio of words that has at least on upper case:
    c = 0
    for token in tokens:
        if hasUpperLetter(token):
            c += 1
    features["hasUpperRatio"] = c / len(tokens)
    # Ratio of lines that start with a non word:
    c = 0
    for line in lines:
        line = line.split()
        if len(line) > 0:
            if not hasLetter(line[0]):
                c += 1
    features["lineStartWithNonWordRatio"] = c / len(lines)
    # Encoding prob count:
    encCount = 0
    encCount += text.count("â")
    encCount += text.count("ï")
    encCount += text.count("U+")
    encCount += text.count("Ï")
    encCount += text.count("À")
    encCount += text.count("Á")
    encCount += text.count("Ã")
    encCount += text.count("�")
    encCount += text.count("")
    features["encodingProbCount"] = encCount
    # Finally we return all features:
    if asDict:
        return features
    else:
        result = list(features.values())
        if asNpArray:
            return np.array(result)
        else:
            return result

def accuracy(predictions, y, thresholds=[0.25, 0.75]):
    assert len(predictions) == len(y)
    wellClassified = 0
    for i in range(len(y)):
        prediction = predictions[i]
        currentPredictedClass = continuous2discret(prediction, thresholds)
        currentY = y[i]
        currentClass = continuous2discret(currentY, thresholds)
        if currentPredictedClass == currentClass:
            wellClassified += 1
    return wellClassified / len(y)
def continuous2discret(y, thresholds):
    currentClass = 0
    for threshold in thresholds:
        if y <= threshold:
            return currentClass
        currentClass += 1
    return currentClass


