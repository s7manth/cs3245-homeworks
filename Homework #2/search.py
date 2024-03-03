#!/usr/bin/python3
import re
import nltk
import sys
import getopt

from enum import Enum
from utils import LoadingUtil, ShuntingYard

class Operator(Enum):
    NOT = 0
    AND = 1
    OR = 2
    AND_NOT = 3
    OR_NOT = 4

class Operand:
    pass

class Search:
    def __init__(self, dict_file, postings_file):
        self.dict_file = dict_file
        self.postings_file = postings_file

        self.lutil = LoadingUtil(dict_file, postings_file)
        self.file_ids, self.dictionary = self.lutil.load_dictionary()

    def process_query(self, query):
        terms, tokens = ShuntingYard.parse(query)
        postings_lists = [self.lutil.load_postings_list(term) for term in terms]

        stack = []

        #####
        # for rpn_token in rpn_query:
        #     if rpn_token not in operators:
        #         rpn_stack.append(Operand(index[0], postings_file, token=rpn_token))
        #     elif rpn_token == "OR":
        #         rpn_stack.append(or_query(rpn_stack.pop(), rpn_stack.pop(), index[0], postings_file))
        #     elif rpn_token == "AND":
        #         rpn_stack.append(and_query(rpn_stack.pop(), rpn_stack.pop(), index[0], postings_file))
        #     elif rpn_token == "NOT":
        #         rpn_stack.append(not_query(rpn_stack.pop(), index[0], index[1], postings_file))
        #     elif rpn_token == "ANOT":
        #         rpn_stack.append(and_not_query(rpn_stack.pop(), rpn_stack.pop(), index[0], postings_file))
        # return " ".join(rpn_stack.pop().get_results())
        #####

        pass



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
        for query in file:
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
    if o == "-d":
        dictionary_file  = a
    elif o == "p":
        postings_file = a
    elif o == "q":
        file_of_queries = a
    elif o == "o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
