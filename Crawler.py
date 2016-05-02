#Author: Raymond Martin
import urllib2
from lxml import html
from urlparse import urljoin

#this class allows for the crawlling of any root directory
#and creates a primitive index of pages in said directory
class Crawler():
    def __init__(self, directory, limit):
        self.dir = directory
        self.limit = limit
        self.outOfDir = []
        self.errorPages = []
        self.pages = []
        self.pageData = {}
        self.readRobots()

    #read the robots.txt and create a forbidden directories list
    def readRobots(self):
        robotURL = urljoin(self.dir, "robots.txt")
        robotText = urllib2.urlopen(robotURL).read().split()
        for i, line in enumerate(robotText):
            if "Disallow" in line:
                robotText = robotText[i+1:]
                break
        self.forbidden = []
        for line in robotText:
            if line[0] == '/':
                line = line[1:]
            self.forbidden.append(urljoin(self.dir, line))
            #print self.forbidden

    #start a DFS crawl form the root page and on
    #with out crawling outside links
    def startCrawl(self):
        #breadth first search implementation of a page crawler
        self.docFP = [self.dir]
        links = [self.dir]
        while links and (len(self.docFP) < (self.limit + 1)):
            cur = links.pop(0)
            self.docFP.append(cur)
            newLinks = self.crawlPage(cur)
            for link in newLinks:
                if link[0] == '/':link = link[1:]
                link = urljoin(cur, link)
                if link not in self.docFP:
                    if self.dir in link:
                        links.append(link)
                    else:
                        self.outOfDir.append(link)

    #crawl the page and extract outside links
    def crawlPage(self, page):
        #check if page is forbidden
        for p in self.forbidden:
            if p in page:
                return []
        try:
            wp = urllib2.urlopen(page)
            rawText = wp.read()
            htmlTree = html.fromstring(rawText)
            #add to index
            if ".txt" in page or ".html" in page or ".htm" in page:
                self.pageData[page] = rawText
            #retreive all href links
            links = htmlTree.xpath('//@href')
            #print(page)
            #close and return all links
            wp.close
            self.pages.append(page)
            return links
        except urllib2.HTTPError as e:
            self.errorPages.append(page)
        except urllib2.URLError as e:
            self.errorPages.append(page)
        except Exception:
            self.errorPages.append(page)
        return []

    #returns raw HTML index
    def getRawHTMLIndex(self):
        return self.pageData

    #returns html tree sturcture index
    def getTreeIndex(self):
        self.treeIndex = {}
        for page, doc in self.pageData.items():
            self.treeIndex[page] =  html.fromstring(doc)
        return self.treeIndex

    #counts the occurences of jpgs in the raw HTML
    def countJPEG(self):
        count = 0
        for page, doc in self.pageData.items():
            count += doc.count(".jpg") + doc.count(".jpeg") + doc.count(".JPEG") + doc.count(".JPG")
        return count
