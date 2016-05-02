#Author: Raymond Martin
from porter_stemmer import PorterStemmer
#from lxml import html
import string, os.path, json

#this class does the reverse indexing, stemming, and stop word removal
class Indexer():
    #sets up direct index to words
    def __init__(self, index, stopWords):
        self.wordIndex = {}
        self.stopWords = [word.lower() for word in stopWords]
        for page, doc in index.items():
            content = ""
            for line in doc.xpath("//body/descendant::*/text()") + doc.xpath("//body/text()"):
                content += ' ' + line
            self.wordIndex[page] =  {"digest" : " ".join(self.flattenString(content)), "term_number" : 0}

    #traversing each document and sets up a reverse index for each word
    def createReverseIndex(self):
        self.reverseIndex = {}
        for page, data in self.wordIndex.items():
            index = self.pageReverseIndex(page, data["digest"])
            self.wordIndex[page]["term_number"] = len(index.items())
            for key, val in index.items():
                if key in self.reverseIndex:
                    self.reverseIndex[key][val[0]] = val[1]
                else:
                    self.reverseIndex[key] = {val[0]:val[1]}
        return self

    def pageReverseIndex(self, page, words):
        words = words.split(' ')
        words = self.processString(words)
        pageIndex = {}
        for word in words:
            if word in pageIndex:
                pageIndex[word] = (page, pageIndex[word][1]+1)
            else:
                pageIndex[word] = (page, 1)
        return pageIndex

    #orders and returns words by frequency
    def getTopWords(self):
        popList = list(self.reverseIndex.items())
        return sorted(popList, key=lambda i: i[1], reverse=True)

    def flattenString(self, digest):
        words = digest.lower().replace('\r\n', '').replace('\t', ' ').replace('\n', ' ').replace('\\u00a0', ' ').split(' ')
        words = [word for word in words if word != '']
        return words

    def processString(self, words):
        output = []
        for word in words:
            word = self.stemWord(word)
            if word != None and word != '' and word not in self.stopWords:
                output.append(word)
        return output

    #stemmer function which stems and removes other characters and stop words
    def stemWord(self, word):
        for c in string.punctuation:
            word = word.replace(c,'')
        for i in range(10):
            word = word.replace(str(i),'')
        return PorterStemmer().stem(word, 0, len(word) -1)

    def saveIndex(self, loc):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, loc), 'w') as fp:
            json.dump(self.reverseIndex, fp, sort_keys=True, indent=4)
        return self

    def savePageDigests(self, loc):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, loc), 'w') as fp:
            json.dump(self.wordIndex, fp, sort_keys=True, indent=4)
        return self
