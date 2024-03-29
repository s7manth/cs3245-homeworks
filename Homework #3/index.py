#!/usr/bin/python3
import getopt
import math
import numpy as np
import os
import pickle
import string
import sys

from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize
from pprint import pprint as print

from utils import LoadingUtil


# index class to represent the postings and the indexing of the terms
class Index:
    def __init__(
        self,
        output_dictionary_path="dictionary.txt",
        output_postings_path="postings.txt",
    ):
        # path of the output dictionary and postings files
        self.output_dictionary_path: str = output_dictionary_path
        self.output_postings_path: str = output_postings_path

        self.files: dict[str, str] = dict()  # file_name: file_path
        self.vocabulary: set[str] = set()  # all individual, unique tokens

        self.postings: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))  # { token: { document: frequency, ... }... }
        self.document_frequency: dict[str, int] = defaultdict(int)  # token: how_many_docs_is_the_token_in
        self.document_length: dict[str, int] = defaultdict(int)  # document_id: number_of_tokens
        self.file_ids: list[str] = list() # all file ids

        # save dictionary in the form of { token: offset of the postings list in disk }
        self.dictionary: dict[str, int] = defaultdict(int)

    def sanity_check(self, input_directory_path):
        # sanity check if the input directory path exists
        if not os.path.exists(input_directory_path):
            raise RuntimeError("ERROR: input directory path doesnt exist")

        # sanity check if the input directory path is in fact a directory
        if not os.path.isdir(input_directory_path):
            raise RuntimeError("ERROR: specified input directory is not a directory")

    # function to preprocess the documents
    def process_documents(self, input_directory_path):
        is_file = lambda file: os.path.isfile(os.path.join(input_directory_path, file))
        self.files = {
            file: os.path.join(input_directory_path, file)
            for file in filter(is_file, os.listdir(input_directory_path))
        }

        stemmer = PorterStemmer()  # stemmer initialisation
        sws = set(stopwords.words("english"))  # stopwords
        punct = set(string.punctuation)  # punctuations

        # use numpy nd array to imitate the structure from tutorial
        #         document1   document2   document3 ...
        # token1  w_{t1, d1}
        # token2
        # token3
        # ...

        for file_id, file_path in list(self.files.items()):
            self.file_ids.append(file_id)
            with open(file_path, "r+") as file:
                stopword_filter = lambda word: word not in sws  # stopword removal
                punctuation_filer = lambda word: word not in punct # punctuation removal

                tokens = [
                    stemmer.stem(word).lower()  # stemming
                    for line in file
                    for st in sent_tokenize(line)  # document to lines tokenisation
                    for word in word_tokenize(st)  # lines to words tokenisations
                ]

                # tokens = list(filter(stopword_filter, tokens))
                tokens = list(filter(punctuation_filer, tokens))
                self.document_length[file_id] = len(tokens)

                for token in tokens:
                    if not token in self.vocabulary:
                        self.vocabulary.add(token)

                    if not file_id in self.postings[token]:
                        self.document_frequency[token] += 1

                    self.postings[token][file_id] += 1

        print("index built!")

    # function to save the postings list with skip pointers
    def save(self):
        with open(self.output_postings_path, "wb") as postings_file:
            position = 0
            for token, t_dict in self.postings.items():
                position = postings_file.tell()
                self.dictionary[token] = position # store dictionary
                pickle.dump(t_dict, postings_file)

        with open(self.output_dictionary_path, "wb") as dictionary_file:
            pickle.dump(self.file_ids, dictionary_file)
            pickle.dump(self.dictionary, dictionary_file)
            pickle.dump(self.document_frequency, dictionary_file)
            pickle.dump(self.document_length, dictionary_file)


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...")

    # the three lines are to index the documents and store the index
    # index = Index(out_dict, out_postings)
    # index.process_documents(in_dir)
    # index.save()

    lutil = LoadingUtil(out_dict, out_postings)
    (
        file_ids,
        dictionary,
        document_frequency,
        document_length,
    ) = lutil.load_dictionary()

    print(lutil.load_document_data(PorterStemmer().stem("Chu".lower())))
    print("-" * 50)
    print(lutil.load_document_data(PorterStemmer().stem("housing,".lower())))


def usage():
    print(f"usage: {sys.argv[0]} -i directory-of-documents -d dictionary-file -p postings-file")


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:d:p:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-i":  # input directory
        input_directory = a
    elif o == "-d":  # dictionary file
        output_file_dictionary = a
    elif o == "-p":  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if (
    input_directory == None
    or output_file_postings == None
    or output_file_dictionary == None
):
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
