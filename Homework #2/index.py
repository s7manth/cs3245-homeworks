#!/usr/bin/python3
import getopt
import math
import numpy as np
import os
import pickle
import string
import sys

from dataclasses import dataclass
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize

from utils import LoadingUtil

class Index:
    def __init__(self, output_dictionary_path="dictionary.txt", output_postings_path="postings.txt"):
        self.output_dictionary_path: str = output_dictionary_path
        self.output_postings_path: str = output_postings_path

        self.files: dict[str, str] = dict() # file_name: file_path
        self.vocabulary: set[str] = set() # all individual, unique tokens
        self.postings: dict[str, set[str]] = {} # token: {all docs that it appears in}

        # all file ids
        self.file_ids: list[str] = list()

        # save postings in the form of { token: string form of the postings list }
        self.postings_serialized: dict[str, str] = {}

        # save dictionary in the form of { token: offset of the postings list in disk }
        self.dictionary: dict[str, int] = {}

    def sanity_check(self, input_directory_path):
        # sanity check if the input directory path exists
        if not os.path.exists(input_directory_path):
            raise RuntimeError("ERROR: input directory path doesnt exist")

        # sanity check if the input directory path is in fact a directory
        if not os.path.isdir(input_directory_path):
            raise RuntimeError("ERROR: specified input directory is not a directory")

    def process_documents(self, input_directory_path):
        is_file = lambda file: os.path.isfile(os.path.join(input_directory_path, file))
        self.files = { file: os.path.join(input_directory_path, file)
            for file in filter(is_file, os.listdir(input_directory_path)) }

        stemmer = PorterStemmer()
        sws = set(stopwords.words("english"))
        punct = set(string.punctuation)

        for file_id, file_path in self.files.items():
            self.file_ids.append(file_id)
            with open(file_path, "r+") as file:
                stopword_filter = lambda word: word not in sws
                punctuation_filer = lambda word: word not in punct

                tokens = [stemmer.stem(word).lower()
                        for line in file
                        for st in sent_tokenize(line)
                        for word in word_tokenize(st)]

                tokens = list(filter(stopword_filter, tokens))
                tokens = list(filter(punctuation_filer, tokens))

                for token in tokens:
                    if token in self.vocabulary:
                        self.postings[token].add(file_id)
                    else:
                        self.postings[token] = { file_id }
                        self.vocabulary.add(token)

        print('index built!')

    def serialize_with_skip_pointers(self, postings_list):
        length = len(postings_list)
        interval = int(math.sqrt(length))

        counter = 0
        result = str()

        while counter < length:
            result += f" {postings_list[counter]}"

            if counter % interval != 0 or interval <= 1:
                counter += 1
                continue

            boundary = counter + interval
            if boundary < length:
                documents_to_skip = postings_list[counter + 1:boundary]
                skip_s = " ".join(str(s) for s in documents_to_skip)

                result += f" +{len(skip_s) + 2} {skip_s}"
                counter += len(documents_to_skip) + 1
                continue

            counter += 1

        return result

    def save(self):
        self.postings_serialized = {
            token: self.serialize_with_skip_pointers(sorted(list(self.postings[token]), key=lambda x: int(x)))
            for token in self.vocabulary
        }

        with open(self.output_postings_path, "wb") as postings_file:
            position = 0
            for token, ps in self.postings_serialized.items():
                position = postings_file.tell()
                self.dictionary[token] = position
                pickle.dump(ps, postings_file)

        with open(self.output_dictionary_path, "wb") as dictionary_file:
            pickle.dump(self.file_ids, dictionary_file)
            pickle.dump(self.dictionary, dictionary_file)

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    index = Index(out_dict, out_postings)
    index.process_documents(in_dir)
    index.save()

    lutil = LoadingUtil(out_dict, out_postings)
    file_ids, dictionary = lutil.load_dictionary()
    pl = lutil.load_postings_list("inch")

    print(pl)


def usage():
    print(f"usage: {sys.argv[0]} -i directory-of-documents -d dictionary-file -p postings-file")

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
