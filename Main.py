# -*- coding: utf-8 -*-
import Indexer
import Tokenizer
import Tfidf
import CosineVectorModel
import BM25
import Task_3
import Evaluation
from bs4 import BeautifulSoup
import PseudoRelevance
import re, string, errno, os

class Main:
    def __init__(self):
        self.source_path = raw_input("Enter path of corpus source: ")
        self.source_path = self.source_path.replace("\\", "/")
        self.dest_path = raw_input("Enter path for index creation: ")
        self.dest_path = self.dest_path.replace("\\", "/")
        self.index = {}
        self.new_source_path = ""
        self.N = 3204
        self.n_path = ""
        self.h_path = ""
        self.modified_queries = []
        self.modified_queries_1 = []
        self.stoplist = self.read_stoplistfile()
        self.idf = []
        self.old_result = {}
        self.old_tfidf_result = {}
        self.hashmap = {}

    def Execute(self):
        self.start_tokenizing()
        self.start_indexing()
        self.get_queries()

        # RANKING STARTS HERE
        self.tfidf_ranking()
        self.cos_ranking()
        self.bm25_ranking()
        self.Task_3_with_Stopping()
        self.Task_3_Stemming()
        self.Task_2_Pseudo_Relevance()
        self.Task_3_Seventh_Run()
        #EVALUATION
        self.Evaluation_task()

        print("Project END !!")

    def start_tokenizing(self):
        tokenize = Tokenizer.Tokenize(self.source_path)  # self.source_path
        self.new_source_path, self.N = tokenize.start_processing()  # "tokenized_corpus", 3204

    # INDEXING
    def start_indexing(self):
        index = Indexer.Indexing(self.new_source_path, self.dest_path)
        print("starting index creation")
        self.index, self.n_path, self.h_path = index.start_processing()

    def get_queries(self):
        queries, queries_1 = self.read_queries()
        tokenize = Tokenizer.Tokenize(" ")
        self.modified_queries = tokenize.process_data(queries)
        self.modified_queries_1 = queries_1
        f = open("queries for lucene.txt", 'w')
        i = 0
        for q in self.modified_queries:
            q = q.strip("\n")
            q = q.replace("\n",' ')
            f.write(str(q))
            f.write("\n")


    def read_queries(self):
        path = "cacm.query"
        path = path.replace("\\", "/")
        path_1 = "cacm_stem.query.txt"
        list_of_queries = []
        list_of_queries_1 = []
        f = open(path, 'r')
        body = f.read()
        soup = BeautifulSoup(body, "html.parser")
        for e in soup.find_all("docno"):
            e.decompose()
        for e in soup.find_all("doc"):
            list_of_queries.append(e.text)

        f1 = open(path_1, 'r')
        while True:
            k = f1.readline()
            if k == '':
                break
            list_of_queries_1.append(k)
        return list_of_queries, list_of_queries_1

    def read_stoplistfile(self):
            stoplist = []
            filename = "common_words"
            f = open(filename, 'r')
            for line in f:
                line = line.strip()
                if line not in stoplist:
                    stoplist.append(line)
            return stoplist

    def tfidf_ranking(self):
        # RANKING ALGO TF.IDF
        print("starting TFIDF ranking")
        tfidf = Tfidf.TDIDF(self.index, self.N)
        ranking_per_query_top_100, self.idf = tfidf.start_processing(self.modified_queries)
        self.old_tfidf_result = ranking_per_query_top_100
        write_top_100_result_query(ranking_per_query_top_100, "TFIDF", "0")
        del ranking_per_query_top_100

    def cos_ranking(self):
        print("starting COS ranking")
        cos = CosineVectorModel.CosineVector(self.index, self.idf, self.N)
        ranking_per_query_top_100 = cos.start_processing(self.modified_queries)
        write_top_100_result_query(ranking_per_query_top_100, "COS", "0")
        del ranking_per_query_top_100

    def bm25_ranking(self):
        print("starting BM25 ranking")
        bm25 = BM25.BM25Ranking(self.index, self.h_path, self.n_path, self.N)
        ranking_per_query_top_100 = bm25.start_processing(self.modified_queries)
        self.old_result = ranking_per_query_top_100
        write_top_100_result_query(ranking_per_query_top_100, "BM25", "0")
        del ranking_per_query_top_100

    def Task_3_with_Stopping(self):
        print("starting COS ranking for task 3")
        updated_index = self.index
        updated_queries = []
        # removing stop words from index and queries
        for x in self.stoplist:
            if x in updated_index:
                del updated_index[x]

        for query in self.modified_queries:
            querywords = query.split()
            resultwords = [word for word in querywords if word.lower() not in self.stoplist]
            result = ' '.join(resultwords)
            updated_queries.append(result)

        bm = BM25.BM25Ranking(updated_index, self.h_path, self.n_path, self.N)
        ranking_per_query_top_100 = bm.start_processing(updated_queries)
        write_top_100_result_query(ranking_per_query_top_100, "BM25_Task_3_Stopping", "0")
        del ranking_per_query_top_100

    def Task_3_Stemming(self):  # using COS system
        task_3 = Task_3.task_3_Ranking(" ", self.dest_path, self.N, self.modified_queries_1, self.h_path)
        ranking_per_query_top_100 = task_3.start()
        write_top_100_result_query(ranking_per_query_top_100, "BM25_Task_3_Stemmed", "1")

    def Evaluation_task(self):
        # Evaluation Code
        evaluate = Evaluation.Evaluation()
        evaluate.create_files()

    def Task_2_Pseudo_Relevance(self):
        print("starting Pseudo ranking")
        psr = PseudoRelevance.PseudoRelevance(self.new_source_path, self.stoplist)
        expanded_queries = psr.PseudoRelevance(self.old_result,self.readHashMap(self.h_path), self.modified_queries)
        bm25 = BM25.BM25Ranking(self.index, self.h_path, self.n_path, self.N)
        ranking_per_query_top_100 = bm25.start_processing(expanded_queries)
        write_top_100_result_query(ranking_per_query_top_100, "Task_2_Psuedo_REL", "0")
        del ranking_per_query_top_100

    def Task_3_Seventh_Run(self):
        print("starting TFIDF with Pseudo ranking")
        updated_index = self.index
        updated_queries = []
        # removing stop words from index and queries
        for x in self.stoplist:
            if x in updated_index:
                del updated_index[x]

        for query in self.modified_queries:
            querywords = query.split()
            resultwords = [word for word in querywords if word.lower() not in self.stoplist]
            result = ' '.join(resultwords)
            updated_queries.append(result)

        psr = PseudoRelevance.PseudoRelevance(self.new_source_path, self.stoplist)
        expanded_queries = psr.PseudoRelevance(self.old_tfidf_result, self.readHashMap(self.h_path), self.modified_queries)

        tfidf1 = Tfidf.TDIDF(updated_index, self.N)
        ranking_per_query_top_100, idf = tfidf1.start_processing(expanded_queries)
        write_top_100_result_query(ranking_per_query_top_100, "Run_7_Tfidf_Pseudo", "0")
        del idf
        del ranking_per_query_top_100

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


def make_sure_path_exists(path):            # checks if a directory exists and create it if not exists
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def write_top_100_result_query(ranking_per_query, model_name, value):
    if value == "0":
        path = "Final_Top_100results_per_query"
        make_sure_path_exists(path)
        f = open(path + "/" + "Top_100_per_query_" + model_name+ ".txt", 'w')
        f.write("QueryID" + "   " + "Rank" + "    " + "DOCID" + "    " + "     Score" + "    " + "  System")
        f.write("\n")
        for i in ranking_per_query:
            rank = 0
            for k in ranking_per_query[i]:
                rank += 1
                f.write("{0:" ">9}".format(i) + "    " + "{0:" ">4}".format(rank) + "    " + "{0:" ">6}".format(k[0]) +
                        "   " + str(k[1])[:5] + "    " + "{0:" ">5}".format(model_name))
                f.write("\n")
        f.close()
    else:
        f = open("Top_100_per_query_" + model_name + ".txt", 'w')
        f.write("QueryID" + "   " + "Rank" + "    " + "DOCID" + "    " + "     Score" + "    " + "  System")
        f.write("\n")
        for i in ranking_per_query:
            rank = 0
            for k in ranking_per_query[i]:
                rank += 1
                f.write("{0:" ">9}".format(i) + "    " + "{0:" ">4}".format(rank) + "    " + "{0:" ">6}".format(k[0]) +
                        "   " + str(k[1])[:5] + "    " + "{0:" ">5}".format(model_name))
                f.write("\n")
        f.close()


def main():
    m = Main()
    m.Execute()

if __name__ == "__main__":
    main()

