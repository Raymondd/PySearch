#Author: Raymond Martin
from porter_stemmer import PorterStemmer
import os.path, json, string, math

#this class does the reverse indexing, stemming, and stop word removal
class Query_Processor():
    #sets up direct index to words
    def __init__(self, index, digest):
        self.index = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, index), 'r') as fp:
            self.index = json.load(fp)

        with open(os.path.join(script_dir, digest), 'r') as fp:
            self.digests = json.load(fp)

    #traversing each document and sets up a reverse index for each word
    def submit_query(self, query):
        all_links = []
        keys = self.processString(query)
        for key in keys:
            if key in self.index:
                for page_name in self.index[key]:
                    all_links.append(page_name)

        return_links = []
        for page in list(set(all_links)):
            score = self.calculateScore(keys, page)
            digest = self.formatDigest(self.digests[page]["digest"], query)
            return_links.append((page, score, digest))

        ord_links = sorted(return_links, key=lambda x:float(x[1]),reverse=True)
        return ord_links

    def formatDigest(self, digest, query):
        for word in set(query.strip().split(' ')):
            if word != ' ' and word != '' and word in digest:
                digest = digest.replace(word, '<b>{}</b>'.format(word))
        formatted_digest = " ".join(digest.split()[:20])
        return formatted_digest[:500]


    def calculateScore(self, query, page_name):
        total_terms = self.digests[page_name]["term_number"]
        corpus_size = len(self.digests)

        query_TFIDF = {}
        for word in query:
            if word in query_TFIDF:query_TFIDF[word] += 1
            else:query_TFIDF[word] = 1

        doc_TFIDF = {}
        for word in query_TFIDF:
            if word in self.index:
                query_TFIDF[word] = self.calculateTFIDF(query_TFIDF[word], len(query), corpus_size, len(self.index[word]))
                if page_name in self.index[word]:
                    doc_TFIDF[word] = self.calculateTFIDF(self.index[word][page_name], total_terms, corpus_size, len(self.index[word]))
                else:
                    doc_TFIDF[word] = 0

        dot_product = 0.0
        _doc_ = 0.0
        _query_ = 0.0
        for word in doc_TFIDF:
            dot_product += doc_TFIDF[word]*query_TFIDF[word]
            _doc_ += doc_TFIDF[word]**2
            _query_ += query_TFIDF[word]**2


        denom = (_doc_**0.5) * (_query_**0.5)
        final_score = dot_product/denom

        #print dot_product,denom,final_score
        #print sum(p*q for p,q in zip(doc_TFIDF.values(), query_TFIDF.values()))
        return final_score

    def calculateTFIDF(self, in_doc, total_doc, total_corpus, in_corpus):
        TF = float(in_doc)/float(total_doc)
        IDF = math.log(float(total_corpus)/float(in_corpus))
        return TF*IDF

    def processString(self, words):

        output = []
        words = words.strip().split(' ')
        for word in words:
            word = word.replace('\r\n', '').lower()
            word = self.stemWord(word)
            if word != None and word != '':
                output.append(word)
        return output
    #stemmer function which stems and removes other characters and stop words
    def stemWord(self, word):
        for c in string.punctuation:
            word = word.replace(c,'')
        for i in range(10):
            word = word.replace(str(i),'')
        return PorterStemmer().stem(word, 0, len(word)-1)
