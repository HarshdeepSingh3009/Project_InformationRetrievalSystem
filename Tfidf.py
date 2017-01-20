import sys, os, errno
import math
from collections import Counter
import operator

class TDIDF:
    def __init__(self, index, N):
        self.index = index
        self.tf_idf_doc = {}
        self.corpus_size = N
        self.idf = self.calculate_idf()
        self.queries = {}

    def calculate_idf(self):
        local_idf = {}
        for item in self.index:
            doc_freq = len(self.index[item])
            local_idf[item] = math.log10((self.corpus_size * 1)/doc_freq)
        return local_idf

    def find_tfidf_in_doc(self, term):
        if term not in self.tf_idf_doc:
            if term in self.index:
                    for k in self.index[term]:
                        if term in self.tf_idf_doc:
                            self.tf_idf_doc[term].append((k, (self.index[term][k] * self.idf[term])))
                        else:
                            self.tf_idf_doc[term] = [(k, (self.index[term][k] * self.idf[term]))]

    def find_tfidf_in_query(self, query):
        lot_query = query.split(" ")
        tf_idf_query = {}
        lot_query = Counter(lot_query)
        for t in lot_query:
            if t in self.idf:
                tf_idf_query[t] = (lot_query[t] * self.idf[t])
            else:
                tf_idf_query[t] = (lot_query[t] * math.log10((self.corpus_size * 1)/1))
        return tf_idf_query

    def calculate_ranking(self, tf_idf_q):
        ranking = {}
        for term in tf_idf_q:
            if term in self.tf_idf_doc:
                for x in self.tf_idf_doc[term]:
                    if x[0] in ranking:
                        ranking[x[0]] = ranking[x[0]] + (x[1] * tf_idf_q[term])
                    else:
                        ranking[x[0]] = (x[1] * tf_idf_q[term])
        return ranking

    def start_processing(self, list_queries):
        ranking_per_query = {}
        ranking_per_query_top_100 = {}
        i = 0
        for q in list_queries:
            i += 1
            tfidf = self.find_tfidf_in_query(q)
            for term in q.split():
                self.find_tfidf_in_doc(term)
            ranking_per_query[i] = self.calculate_ranking(tfidf)
            ranking_per_query[i] = sorted(ranking_per_query[i].items(), key=operator.itemgetter(1), reverse=True)
            ranking_per_query_top_100[i] = ranking_per_query[i][:100]
        del ranking_per_query
        return ranking_per_query_top_100, self.idf

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
