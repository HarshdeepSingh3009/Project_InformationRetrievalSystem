# -*- coding: utf-8 -*-
import re, string
import os, errno, sys
import random


class Tokenize:

    def __init__(self, source):
        self.dic = {}
        self.all_words = []
        self.source_dir = source
        self.corpus_dir = "tokenized_corpus"

    def process_data(self, body):
        list_words = []

        # do text manipulation now
        punc = string.punctuation
        # punc = punc.replace('.','')
        punc = punc.replace('-','')
        punc = punc.replace(',', ', ')
        punc = punc.replace(' ','')

        regex = re.compile('[%s]' % re.escape(punc))

        for l in body:
            flag = False
            l = l.strip("\n")
            l = l.strip(" ")
            if not (l.startswith('<') and l.endswith('>')):
                    l = regex.sub('', l)
                    l = l.replace('.', "")
                    if l.endswith("AM") or l.endswith("PM"):
                        flag = True
                    l = l.lower()
                    list_words.append(l.encode("UTF-8"))
            if flag:
                break

        return list_words

    def make_sure_path_exists(self, path):                 # checks if a directory exists and create it if not exists
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def write_data_to_file(self, txt, o_filename):
        self.make_sure_path_exists(self.corpus_dir)
        o_filename = o_filename[:o_filename.index(".html")]
        try:
            # if not os.path.isfile(self.corpus_dir + "/" + o_filename + ".txt"):
            #     with open(self.corpus_dir + "/" + o_filename + ".txt", "w") as f:
            #         f.write(" ".join(txt))
            # else:
            with open(self.corpus_dir + "/" + o_filename + ".txt", "w") as f:
                f.write(" ".join(txt))
        except:
            print(sys.exc_info())

    def start_processing(self):
        list_of_files = []
        i = 0
        for f in os.listdir(self.source_dir):
            print("getting file names")
            list_of_files.append(f)

        print("starting manipulation")

        for files in list_of_files:
            i += 1
            with open(self.source_dir + "/" + files, 'r') as f:
                o_filename = files
                body = f.readlines()
                self.write_data_to_file(self.process_data(body), o_filename)
                print("successfully tokenized file : " + str(i) + " " + o_filename)

        return self.corpus_dir, len(list_of_files)

