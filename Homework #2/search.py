#!/usr/bin/python3
import re
import math
import nltk
import sys
import getopt

from enum import Enum
from nltk.stem.porter import PorterStemmer
from utils import LoadingUtil, ShuntingYard

class Operator(Enum):
    NOT = 0
    AND = 1
    OR = 2
    AND_NOT = 3

class Characters(Enum):
    SPACE = " "
    EMPTY = ""
    SKIP_POINTER = "+"

class Operand:
    def __init__(self, lutil, token="", result=[], is_all=False):
        self.has_results = False

        _, _, self.file_ids = lutil.load_dictionary()

        self.token = token
        self.starting_fp = 0
        self.postings_string = self.file_ids if is_all else lutil.load_postings_list(token)

        self.frequency = len(list(filter(lambda x: not x.startswith("+"), self.postings_string.strip().split(" "))))
        self.length = len(self.postings_string)
        self.next_fp = 0
        self.next_fp_copy = 0

        self.evaluated_results = []
        self.next_idx = 0

        if is_all:
            self.next_fp = self.starting_fp
            self.next_fp_copy = self.next_fp
        elif token != "":
            stemmer = PorterStemmer()
            self.token = stemmer.stem(token.lower())

            if len(self.postings_string.strip()) == 0:
                self.has_results = True
            else:
                self.next_fp = self.starting_fp
                self.next_fp_copy = self.next_fp
        else:
            self.has_results = True
            self.evaluated_results = result

    def get_frequency(self):
        if self.has_results:
            return len(self.evaluated_results)
        return self.frequency

    def get_results(self):
        if not self.has_results:
            for _ in range(self.frequency):
                self.evaluated_results.append(self.next())
            self.has_results = True

        return self.evaluated_results

    def skip_pointer(self):
        value = ("", 0)
        if self.has_results:
            skip_interval = math.sqrt(len(self.evaluated_results))

            if self.next_idx % skip_interval == 0 and self.next_idx + skip_interval < len(self.evaluated_results):
                value = (self.evaluated_results[self.next_idx + int(skip_interval)], skip_interval)

            return value

        self.next_fp_copy = self.next_fp
        current = "" if self.next_fp_copy >= len(self.postings_string) else self.postings_string[self.next_fp_copy]
        self.next_fp_copy += 1
        skipped_bytes = 0
        skip = ""
        skipped_value = ""

        if current == "+":
            skipped_bytes += 2
            current = self.postings_string[self.next_fp_copy]
            self.next_fp_copy += 1
            skipped_bytes += 1

            while current != " ":
                skip += current
                current = self.postings_string[self.next_fp_copy]
                self.next_fp_copy += 1
                skipped_bytes += 1

            self.next_fp_copy += int(skip) - 1
            skipped_bytes += int(skip) - 1
            current = self.postings_string[self.next_fp_copy]
            self.next_fp_copy += 1
            skipped_bytes += 1

            while current != " ":
                skipped_value += current
                current = self.postings_string[self.next_fp_copy]
                self.next_fp_copy += 1
                skipped_bytes += 1

            skipped_bytes -= 1

        value = (skipped_value, skipped_bytes)
        return value

    def next_skip(self, interval):
        if self.has_results:
            self.next_idx += interval
        else:
            self.next_fp += interval

    def next(self):
        value = ""
        if self.has_results:
            if self.next_idx < len(self.evaluated_results):
                value = self.evaluated_results[self.next_idx]
                self.next_idx += 1

        elif self.next_fp < self.starting_fp + self.length:
            accumulated = ""
            self.next_fp_copy = self.next_fp

            while value == "":
                self.next_fp_copy += 1
                current = "" if self.next_fp_copy >= len(self.postings_string) else self.postings_string[self.next_fp_copy]
                self.next_fp_copy += 1
                is_end = current == ""
                is_skip = current == "+"

                if is_end: return value

                while current != " " and current != "":
                    if not is_skip:
                        value += current

                    current = "" if self.next_fp_copy >= len(self.postings_string) else self.postings_string[self.next_fp_copy]
                    self.next_fp_copy += 1

                self.next_fp_copy -= 1

            self.next_fp = self.next_fp_copy

        return value

class Search:
    def __init__(self, dict_file, postings_file):
        self.dict_file = dict_file
        self.postings_file = postings_file

        self.lutil = LoadingUtil(dict_file, postings_file)
        self.file_ids, self.dictionary, self.all_file_postings_list = self.lutil.load_dictionary()

    def process_query(self, query):
        queue = ShuntingYard.parse(query)
        print(queue)
        stack = []

        operators = { "AND", "OR", "NOT", "ANOT" }
        operator_precedence = { "NOT": 2, "AND": 1, "ANOT": 1, "OR": 0 }

        for token in queue:
            # print("STACK", stack)
            if token not in operators:
                # means the token is a term
                stack.append(Operand(self.lutil, token=token))
                continue

            if token == "OR":
                stack.append(self.or_query(stack.pop(), stack.pop()))
                continue

            if token == "AND":
                stack.append(self.and_query(stack.pop(), stack.pop()))
                continue

            if token == "NOT":
                stack.append(self.not_query(stack.pop()))
                continue

            if token == "ANOT":
                stack.append(self.and_not_query(stack.pop(), stack.pop()))
                continue

        return " ".join(stack.pop().get_results())


    def not_query(self, operand):
        all_operand = Operand(self.lutil, is_all=True)
        a = operand.next()
        b = all_operand.next()
        result = []
        while a != "" and b != "":
            if int(a) == int(b):
                a = operand.next()
                b = all_operand.next()
            elif int(a) < int(b):
                result.append(a)
                a = operand.next()
            else:
                result.append(b)
                b = all_operand.next()
        while b != "":
            result.append(b)
            b = all_operand.next()
        return Operand(self.lutil, result=result)

    def and_not_query(self, operand_b, operand_a):
        a = operand_a.next()
        b = operand_b.next()

        result = []

        while a != "" and b != "":
            if int(a) == int(b):
                a = operand_a.next()
                b = operand_b.next()
            elif int(a) < int(b):
                result.append(a)
                a = operand_a.next()
            else:
                b = operand_b.next()

        while a != "":
            result.append(a)
            a = operand_a.next()

        return Operand(self.lutil, result=result)

    def and_query(self, operand_a, operand_b):
        if operand_a.get_frequency() > operand_b.get_frequency():
            return self.and_query(operand_b, operand_a)
        else:
            result = []
            a = operand_a.next()
            b = operand_b.next()
            while a != "" and b != "":
                if int(a) == int(b):
                    result.append(a)
                    a = operand_a.next()
                    b = operand_b.next()
                elif int(a) < int(b):
                    (a_skip, a_skip_interval) = operand_a.skip_pointer()
                    if a_skip != "" and int(a_skip) <= int(b):
                        operand_a.next_skip(a_skip_interval)
                        a = a_skip
                    else:
                        a = operand_a.next()
                else:
                    (b_skip, b_skip_interval) = operand_b.skip_pointer()
                    if b_skip != "" and int(b_skip) <= int(a):
                        operand_b.next_skip(b_skip_interval)
                        b = b_skip
                    else:
                        b = operand_b.next()
            return Operand(self.lutil, result=result)

    def or_query(self, operand_a, operand_b):
        result = []
        if operand_a.has_results and len(operand_a.evaluated_results) == 0:
            result = operand_b.get_results()
        elif operand_b.has_results and len(operand_b.evaluated_results) == 0:
            result = operand_a.get_results()
        else:
            a = operand_a.next()
            b = operand_b.next()
            while a != "" and b != "":
                if int(a) == int(b):
                    result.append(a)
                    a = operand_a.next()
                    b = operand_b.next()
                elif int(a) < int(b):
                    result.append(a)
                    a = operand_a.next()
                else:
                    result.append(b)
                    b = operand_b.next()
            while a != "":
                result.append(a)
                a = operand_a.next()
            while b != "":
                result.append(b)
                b = operand_b.next()
        return Operand(self.lutil, result=result)


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
        for i, query in enumerate(file):
            query = query.strip()
            print(i)
            result = search.process_query(query)
            # result = " ".join(token for token in result.strip().split(" ") if not token.startswith("+"))
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
    elif o == "-p":
        postings_file = a
    elif o == "-q":
        file_of_queries = a
    elif o == "-o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
