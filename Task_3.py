# -*- coding: utf-8 -*-
import re, string
import BM25
import sys, math, os, errno


class StoppingAndStemming:
    def __init__(self,source, index_destination):
        self.new_index = {}
        self.stemmed_index = {}
        self.index_dictionary = {}
        self.source = "cacm_stem.txt"
        self.dest = index_destination
        self.NoOfToken = {}
        self.hashmap_path = self.dest + "/" + "hashmap/hashmap_stemmed.txt"
        self.NoOfToken_path = self.dest + "/" + "NoOfTokens_Task_3.txt"
        self.stemmed_corpus = {}

    def make_sure_path_exists(self, path):            # checks if a directory exists and create it if not exists
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def read_stemmed_corpus(self, filename):
        d = {}
        f = open(filename, 'r')
        i = 0
        m = 0
        for line in f:
            l = []
            if line.startswith('#'):
                x = line.split()
                m = x[1]
                d[m] = l
            else:
                line = line.strip("\n")
                line = line.strip(" ")
                line = line.translate(None, string.digits)
                l = line.split()
                d[m].extend(l)
        self.stemmed_corpus = d

    def createIndex(self, n):
        d = {}
        noOfToken ={}
        for i in self.stemmed_corpus:
            docId = i
            k = self.stemmed_corpus[i]
            noOfToken[i] = len(set(k))
            for c in range(0, len(k) - n - 1):
                # item=k[c]
                # print d
                item = ""
                max = c + n
                for i in range(c, c + n):
                    item = item + k[i]
                    if (i + 1 < max):
                        item = item + " "
                    if item in d:
                        if docId in d[item]:
                            d[item][docId] = d[item][docId] + 1
                        else:
                            d[item][docId] = 1
                    else:
                        d[item] = {docId: 1}
        return d.copy(), noOfToken

    def ngram(self, n):
        uni = {}
        noOfToken = {}
        self.read_stemmed_corpus(self.source)
        uni, noOfToken = self.createIndex(n)
        return uni.copy(), noOfToken

    def start_processing(self):
        list_of_files = []
        i = 0
        try:
            print("creating index")
            self.index_dictionary, self.NoOfToken = self.ngram(1)

        except:
            print("error while  processing file")
            print(sys.exc_info())
            print(sys.exc_traceback)

        # write data into files
        print("writing index file")
        self.writeIndex(self.index_dictionary)
        print("generating and writing tf")
        self.writeTermFreqTable(self.generateTermFreqTable(self.index_dictionary), "Term_Frequency_Task_3")
        print("writing df")
        self.writeDocFreqTable(self.index_dictionary, "Doc_Frequency_Task_3")
        print("writing vocabulary count file")
        self.writeNoOfToken(self.NoOfToken_path)
        return self.index_dictionary, self.NoOfToken_path

    def writeIndex(self, index):
        self.make_sure_path_exists(self.dest)
        f = open(self.dest + "/" + "index_file_task_3" + ".txt", "w")
        for item in sorted(index.iterkeys()):
            f.write(item)
            f.write(" -> ")
            for k1 in sorted(index[item].iterkeys()):
                f.write('(')
                f.write(str(k1))
                f.write(",")
                f.write(str(index[item][k1]))
                f.write(')')
                f.write(" ")
            f.write('\n')
        f.close()

    def generateTermFreqTable(self, index):
        d = {}
        for k, v in index.items():
            tf = 0
            for k1, v1 in v.items():
                tf = tf + v1
            d[k] = tf
        return d.copy()

    def writeTermFreqTable(self, d, filename):
        k = self.dest + "/"
        f = open(k + filename + ".txt", "w")
        l = sorted(d, key=d.get, reverse=True)
        for item in l:
            f.write(str(item))
            f.write(" ")
            f.write(str(d[item]))
            f.write("\n")
        f.close()

    def writeNoOfToken(self, filename):
        f = open(filename, "w")
        for item in self.NoOfToken:
            f.write(str(item))
            f.write(" ")
            f.write(str(self.NoOfToken[item]))
            f.write("\n")
        f.close()

    def writeDocFreqTable(self, index, filename):
        d = index.copy()
        k = self.dest + "/"
        f = open(k + filename + ".txt", "w")
        l = sorted(d)
        for k in l:
            f.write(k)
            f.write(" ")
            count = 0
            for k1, v1 in d[k].items():
                f.write(str(k1))
                f.write(" ")
                count = count + 1
            f.write(str(count))
            f.write("\n")
        f.close()


class task_3_Ranking:
    def __init__(self, source, dest, N, queries, hashmap_source):
        self.N = N
        self.task_3 = StoppingAndStemming(source, dest)
        self.index, self.NoofTokenpath = self.task_3.start_processing()
        self.BM25 = BM25.BM25Ranking(self.index, hashmap_source, self.NoofTokenpath, self.N)
        self.queries = queries

    def start(self):
        ranking_per_query_top_100 = self.BM25.start_processing(self.queries)
        return ranking_per_query_top_100
