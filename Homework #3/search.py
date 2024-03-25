#!/usr/bin/python3
import re
import nltk
import sys
import getopt

from utils import LoadingUtil

class Search:
    def __init__(self, dict_file, postings_file):
        self.dict_file = dict_file
        self.postings_file = postings_file

        self.lutil = LoadingUtil(dict_file, postings_file)
        (
            self.file_ids,
            self.dictionary,
            self.all_file_postings_list,
            self.document_frequency,
            self.document_length
        ) = self.lutil.load_dictionary()

    def process_query(self, query):
        return ""

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

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
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
