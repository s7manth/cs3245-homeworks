#!/usr/bin/python3
import re
import getopt
import math
import string
import sys

from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize
from pprint import pprint as print

from utils import LoadingUtil


class Search:
    def __init__(self, dict_file, postings_file):
        self.dict_file = dict_file
        self.postings_file = postings_file

        self.tf_score: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(int))
        self.normalised_tf: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(int))
        self.q_score: dict[str, dict[str, float]] = {}

        self.lutil = LoadingUtil(dict_file, postings_file)
        (
            self.file_ids,
            self.dictionary,
            self.document_frequency,
            self.document_length,
        ) = self.lutil.load_dictionary()

        self.stemmer = PorterStemmer()  # stemmer initialisation
        self.sws = set(stopwords.words("english"))  # stopwords
        self.punct = set(string.punctuation)  # punctuations

        self.stopword_filter = lambda word: word not in self.sws  # stopword removal
        self.punctuation_filer = lambda word: word not in self.punct # punctuation removal

    # def __post_init__(self):
    #     self.score_document()

    # ltc
    def score_document(self, token):
        if token not in self.dictionary:
            return None

        if token in self.tf_score:
            return self.normalised_tf[token]

        document_data = self.lutil.load_document_data(token)

        magnitude = 0
        for doc in document_data:
            self.tf_score[token][doc] = 1 + math.log(document_data[doc], 10)
            magnitude += pow(1 + math.log(document_data[doc], 10), 2)

        magnitude = pow(magnitude, 0.5)
        for doc in document_data:
            self.normalised_tf[token][doc] = self.tf_score[token][doc] / magnitude

        return self.normalised_tf[token]

    # # lnc
    # def score_query(self, query_tokens):
    #     for token in query_tokens:
    #         pass

    #     return 0, 0

    def process_query(self, query):
        # tokenize query
        tokens = [
            self.stemmer.stem(word).lower()  # stemming
            for word in word_tokenize(query)  # query to words tokenisations
        ]

        # tokens = list(filter(stopword_filter, tokens))
        tokens = list(filter(self.punctuation_filer, tokens))

        for t in tokens:
            output = self.score_document(t)
            print(f"normalized doc vector for {t} is {output}")

        # create query vector and get the list of documents
        # score, document = self.score_query(tokens)
        # return document


def usage():
    print(f"usage: {sys.argv[0]} -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print("running search on the queries...")

    search = Search(dict_file, postings_file)
    answers = list()

    with open(queries_file, "r") as file:
        for _i, query in enumerate(file):
            query = query.strip()
            result = search.process_query(query)
            answers.append(result)

    with open(results_file, "w") as file:
        _ = [file.write(f"{a}\r\n") for a in answers]


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:p:q:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        dictionary_file = a
    elif o == "-p":
        postings_file = a
    elif o == "-q":
        file_of_queries = a
    elif o == "-o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if (
    dictionary_file == None
    or postings_file == None
    or file_of_queries == None
    or file_of_output == None
):
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
