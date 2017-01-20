import sys, math, os, errno
import Indexer
from collections import Counter
import operator

class BM25Ranking:
    def __init__(self, index, hashmap_source, noOfToken_source, N):
        self.index = index
        self.R = 0.00
        self.r = 0.00
        self.avgdl = 0.00
        self.n = 0.00
        self.N = N
        self.f_query = 0.00
        self.f_doc = 0.00
        self.h_source = hashmap_source
        self.n_source = noOfToken_source
        self.k1 = 1.2
        self.k2 = 800.00
        self.b = 0.75
        self.dl = self.Compute_dl()
        self.relevant_docs_query = self.get_relevant_docs()

    def get_relevant_docs(self):
        list_of_docs_per_query = {}
        filename = "cacm.rel"
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            x = line.split()
            if x[0] in list_of_docs_per_query:
                list_of_docs_per_query[x[0]].append(x[2])
            else:
                list_of_docs_per_query[x[0]] = [x[2]]
        return list_of_docs_per_query

    def readnoOfTokenTxt(self, filename):
        f = open(filename, 'r')
        nooftoken = {}
        while True:
            k = f.readline()
            if k == '':
                break
            k = k.split()
            nooftoken[k[0]] = int(k[1])
        return nooftoken.copy()

    def Compute_k(self, dl):
        return self.k1 * ((1 - self.b) + self.b * (dl / self.avgdl))

    def readHashMap(self, filename):
        f = open(filename, 'r')
        d = {}
        while True:
            k = f.readline()
            if k == '':
                break
            k = k.split()
            d[k[0]] = k[1]
        return d.copy()

    def Compute_dl(self):
        noOftoken = {}
        # hashmap = self.readHashMap(self.h_source)
        noOftoken = self.readnoOfTokenTxt(self.n_source)
        self.avgdl = sum(noOftoken.values())/self.N
        return noOftoken

    def BM25Score(self, dl):
        K = self.Compute_k(dl)
        start = float(math.log(((self.r + 0.5) / (self.R - self.r + 0.5)) / ((self.n - self.r + 0.5) /
                                                                       (self.N - self.n - self.R + self.r + 0.5))))
        middle = float((self.k1 + 1)*self.f_doc)/(K + self.f_doc)
        last = float((self.k2 + 1) * self.f_query) / (self.k2 + self.f_query)
        return start * middle * last

    def calculate_ranking(self, query, x):
        ranking ={}
        query_terms = query.split()
        temp = Counter(query_terms)
        for term in temp:
            self.r = 0
            self.R = len(x)
            self.f_query = temp[term]
            if term in self.index:
                doc_list = self.index[term]
                for y in x:
                    if y in doc_list:
                        self.r += 1
                self.n = len(doc_list)
                for doc in doc_list:
                    self.f_doc = doc_list[doc]
                    score = self.BM25Score(self.dl[str(doc)])
                    if doc in ranking:
                        ranking[doc] += score
                    else:
                        ranking[doc] = score
        return ranking

    def start_processing(self, queries):
        ranking_per_query = {}
        i = 0
        ranking_per_query_top_100 = {}
        for query in queries:
            i += 1
            x = []
            if i in self.relevant_docs_query:
                x = self.relevant_docs_query[i]
            ranking_per_query[i] = self.calculate_ranking(query, x)
            ranking_per_query[i] = sorted(ranking_per_query[i].items(), key=operator.itemgetter(1), reverse=True)
            ranking_per_query_top_100[i] = ranking_per_query[i][:100]
        del ranking_per_query
        return ranking_per_query_top_100

    def calculate_average(self, rankings):
        rankings_with_doc_keys = {}
        for i in rankings:
            for j in rankings[i]:
                if j[0] in rankings_with_doc_keys:
                    rankings_with_doc_keys[j[0]] += float(j[1])
                else:
                    rankings_with_doc_keys[j[0]] = float(j[1])

        rankings_with_doc_keys = {k: v / 64 for k, v in rankings_with_doc_keys.items()}
        rankings_with_doc_keys = sorted(rankings_with_doc_keys.items(), key=operator.itemgetter(1), reverse = True)
        rankings_with_doc_keys = rankings_with_doc_keys[:100]
        return rankings_with_doc_keys


