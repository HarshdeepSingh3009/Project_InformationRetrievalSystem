import sys, os, errno
import math
from collections import Counter
import operator


class CosineVector:
    def __init__(self, index, idf, N):
            self.index = index
            self.tf_idf_doc = {}
            self.idf = idf
            self.corpus_size = N

    # calculate tf.idf at document level using scheme "lnc" where we find log of tf in doc and assume idf to be 1

    def find_tfidf_in_doc(self, term):
            if term in self.index:
                    for k in self.index[term]:
                        if term in self.tf_idf_doc:
                            self.tf_idf_doc[term].append((k, (1 + float(math.log10(self.index[term][k])) * self.idf[term])))
                        else:
                            self.tf_idf_doc[term] = [(k, (1 + float(math.log10(self.index[term][k])) * self.idf[term]))]

    # calculate tf.idf at query level using scheme "ltc" where we find log of tf in query and assume idf to be log N/df

    def find_tfidf_in_query(self, query):
        lot_query = query.split(" ")
        tf_idf_query = {}
        lot_query = Counter(lot_query)
        for t in lot_query:
            if t in self.idf:
                tf_idf_query[t] = float((1 + math.log10(lot_query[t]))) * self.idf[t]
            else:
                tf_idf_query[t] = (1 + math.log10(lot_query[t])) * math.log10((self.corpus_size * 1)/1)
        return tf_idf_query

    # here we calculate product of weight of term j in document di and query q and store it in temp, also we calculate
    # length of documents(normalization factor) and length of query(normalization factor)
    def calculate_ranking(self, tf_idf_query):
        temp = {}
        length_of_doc ={}
        z = 0.00
        # calcualte tf-idf ranking
        for term in tf_idf_query:
            z += float(math.pow(tf_idf_query[term], 2))
            if term in self.tf_idf_doc:
                for x in self.tf_idf_doc[term]:
                    if x[0] in temp:
                        temp[x[0]] = temp[x[0]] + (x[1] * tf_idf_query[term])
                    else:
                        temp[x[0]] = x[1] * tf_idf_query[term]
        # normalization at query level
        length_of_query = 1/math.sqrt(z)

        # normalization at doc level

        for term in self.tf_idf_doc:
            for n in self.tf_idf_doc[term]:
                if not n[0] in length_of_doc:
                    length_of_doc[n[0]] = float(n[1] * n[1])
                else:
                    length_of_doc[n[0]] += float(n[1] * n[1])

        for doc in length_of_doc:
            if length_of_doc[doc] != float(0):
                length_of_doc[doc] = 1 / float(math.sqrt(length_of_doc[doc]))
            else:
                length_of_doc[doc] = 0

        ranking = self.cosine_score(length_of_doc, length_of_query, temp)
        return ranking

    # we get final ranking by using cosine vector model here
    def cosine_score(self, list_doc_length, query_length, temporary_rank):
        ranking = {}
        for doc in temporary_rank:
            if doc not in ranking:
                ranking[doc] = temporary_rank[doc] * list_doc_length[doc] * query_length
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
            ranking_per_query[i] = sorted(ranking_per_query[i].items(), key=operator.itemgetter(1), reverse = True)
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


