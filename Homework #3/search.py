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

        self.tf_score_query: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(int)) # maintain the tf-idf score for the query
        self.idf_score_query: dict[str, float] = {} # calculate the idk for all the tokens

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

        self.__post_init__()

    def __post_init__(self):
        self.calc_idf()

    # calculate and store the idf scores for all the terms in the document
    def calc_idf(self):
        for token in self.dictionary:
            df = self.document_frequency[token]
            idf = math.log(len(self.file_ids) / df, 10) if df != 0 else 0
            self.idf_score_query[token] = idf

    # function to process each query that comes in
    def process_query(self, query):
        # tokenize query
        tokens = [
            self.stemmer.stem(word).lower()  # stemming
            for word in word_tokenize(query)  # query to words tokenisations
        ]

        # tokens = list(filter(stopword_filter, tokens))
        tokens = set(filter(self.punctuation_filer, tokens))

        # calculate the tf for the query terms
        for token in tokens:
            if token in self.dictionary:
                self.tf_score_query[query][token] += 1

        # calculate the tf-idf for the query terms by multiplying the tf scores with idf scores
        for token in tokens:
            idf = self.idf_score_query[token] if token in self.idf_score_query else 0
            tf = self.tf_score_query[query][token]
            tf_idf = tf * idf
            self.tf_score_query[query][token] = tf_idf

        scores: dict[str, float] = defaultdict(float)
        # calculate the log tf score for the document
        for token in tokens:
            ps = self.lutil.load_document_data(token)
            for file in ps:
                tf_doc = 1 + math.log(ps[file], 10)

                # calculate the scores for the particular doc
                scores[file] += self.tf_score_query[query][token] * tf_doc

        # normalise the score by dividing by the doc length.
        for file in scores:
            scores[file] /= self.document_length[file]

        # return the top 10 documents for a particular query
        # these documents are sorted in a reverse manner with respect to the score
        tls = scores.items()
        scores_sorted = list(sorted(tls, key=lambda x: -x[1]))
        scores_sorted = scores_sorted[:10]
        result = " ".join(map(lambda pair: pair[0], scores_sorted))
        return result

def usage():
    print(f"usage: {sys.argv[0]} -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


# method to facilitate the searching process,
# by reading in the queries and the postings and dictionary file
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
