class PseudoRelevance:

    def __init__(self, path, stoplist):
        self.path = path
        self.stoplist = stoplist

    def createIndex(self, dic, filename):
        d=dic.copy()
        docId = filename
        f=open(self.path + "/" + filename, 'r')
        k = f.read()
        k = k.split()
        for c in range(0, len(k)- 1):
            item = k[c]
            if item in d:
                if docId in d[item]:
                    d[item][docId] = d[item][docId] + 1
                else:
                    d[item][docId] = 1
            else:
                d[item] = {docId: 1}
        return d.copy()

    def generateTermFreqTable(self, index):
        d = {}
        for k, v in index.items():
            tf = 0
            for k1, v1 in v.items():
                tf = tf + v1
                d[k] = tf
        return d.copy()

    def removeStopWords(self, l):
        new_list=[]
        for word in l:
            if word not in self.stoplist:
                new_list.append(word)
        return new_list

    # REturns : expanded query for all queries
    def PseudoRelevance(self, old_results, hashmap, queries):
        new_query = []
        for j in range(0, len(queries)):
            cacmTopk = []
            topk = 25
            for i in range(0, topk):
                cacmTopk.append(old_results[j+1][i][0])
            filenames = []
            for docid in cacmTopk:
                filenames.append(hashmap[str(docid)])

            dic={}
            for name in filenames:
                dic = self.createIndex(dic.copy(), name)
            index = dic

            TermFreq = self.generateTermFreqTable(index)
            l = sorted(TermFreq, key=TermFreq.get, reverse=True)
            l = self.removeStopWords(l)
            new_query.append(queries[j])
            count = 0
            for i in range(0, len(l)):
                if l[i] not in new_query:
                    new_query[j]=new_query[j]+" "+l[i]
                    count += 1
                if count >= 5:
                    break
        return new_query

    