#Author: Raymond Martin
from Crawler import Crawler
from Indexer import Indexer
from Query_Processor import Query_Processor
import json, os.path

class DataModel():
    def reindex():
        #defines our indexing limit (N)
        limit = 100
        root = "http://lyle.smu.edu/~fmoore/"
        myCrawl = Crawler(root, limit)
        myCrawl.startCrawl()

        #creating our reverse index
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stopWords = './assets/stopwords.txt'
        stopWords = open(os.path.join(script_dir, stopWords)).read().splitlines()
        myIndex = Indexer(myCrawl.getTreeIndex(), stopWords).createReverseIndex().saveIndex('assets/reverse_index.json').savePageDigests('assets/page_digests.json')
        return True

    def search(query):
        #return [(u'http://lyle.smu.edu/~fmoore/misc/levenshtein.html', 2, u'levenshtein distance calculator string 1: string 2: distance = for example: fast to cats = 3 cats to dogs = 3')]
        processor = Query_Processor('assets/reverse_index.json', 'assets/page_digests.json')
        results = processor.submit_query(query)
        #print results
        return results

    search = staticmethod(search)
    reindex = staticmethod(reindex)


if __name__ == "__main__":
    DataModel.reindex()
    print(DataModel.search("cats"))
