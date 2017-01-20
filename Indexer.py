# -*- coding: utf-8 -*-
import os, errno, sys
from operator import itemgetter


class Indexing:

    def __init__(self, source, index_destination):
        self.index_dictionary = {}
        self.source = source
        self.dest = index_destination
        self.NoOfToken = {}
        self.hashmap_path = self.dest + "/" + "hashmap/hashmap.txt"
        self.NoOfToken_path = self.dest + "/" + "NoOfTokens.txt"

    def make_sure_path_exists(self, path):            # checks if a directory exists and create it if not exists
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def hashmap(self, lof):
        k = "/hashmap.txt"
        self.make_sure_path_exists(self.dest + "/hashmap")
        f = open(self.dest + "/hashmap" + k, "w")
        for name in lof:
            end = name.index(".txt")
            doc_id = name[:end]
            f.write(str(doc_id))
            f.write(" ")
            f.write(name)
            f.write("\n")
        f.close()

    def readHashMap(self, filename):
        f = open(filename, 'r')
        d = {}
        while True:
            k = f.readline()
            if k == '':
                break
            k = k.split()
            d[k[1]] = k[0]
        return d.copy()

    def getDocID(self, hashmap, filename):
        return hashmap[filename]

    def createIndex(self, d1, filename, hashmap, n):
        k = self.source
        k = k + "/"+filename
        d = d1.copy()
        f = open(k, "r")
        docId = self.getDocID(hashmap, filename)
        k = f.read()
        k = k.split()
        term_count = len(set(k))
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
        return d.copy(), term_count

    def ngram(self, n):
        uni = {}
        noOfToken = {}
        h = self.readHashMap(self.hashmap_path)
        for item in h.keys():
            new_doc_id = item[:len(item)-4]
            uni, noOfToken[str(new_doc_id)] = self.createIndex(uni, item, h, n)
        return uni.copy(), noOfToken

    def start_processing(self):
        list_of_files = []
        i = 0
        try:
            print("getting file names")
            for f in os.listdir(self.source):
                list_of_files.append(f)
            print("creating hash map")
            self.hashmap(list_of_files)
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
        self.writeTermFreqTable(self.generateTermFreqTable(self.index_dictionary), "Term_Frequency")
        print("writing df")
        self.writeDocFreqTable(self.index_dictionary, "Doc_Frequency")
        print("writing vocabulary count file")
        self.writeNoOfToken(self.NoOfToken_path)
        return self.index_dictionary, self.NoOfToken_path, self.hashmap_path

    def writeIndex(self, index):
        self.make_sure_path_exists(self.dest)
        f = open(self.dest + "/" + "index_file" + ".txt", "w")
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
