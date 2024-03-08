#!/usr/bin/python3
import re
import math
import nltk
import sys
import getopt

from enum import Enum
from nltk.stem.porter import PorterStemmer
from utils import LoadingUtil, ShuntingYard, BooleanOpertors

class Characters:
    SPACE = " "
    EMPTY = ""
    SKIP_POINTER = "+"


# represents a token/term that is associated with a postings list
# this class also takes care of the not operator requirement where we take a negation
# with the universe, the postings list in that case would have all the files
class Token:
    def __init__(self, lutil, token=Characters.EMPTY, result=[], all_files_postings_list=False):
        self.contains_results = False

        _, _, self.file_ids = lutil.load_dictionary()

        # token (stemmed) associated with the postings list
        self.token = PorterStemmer().stem(token.lower())
        self.start_pointer = 0
        # postings list in flattened string form from the pickle file
        self.postings_string = ""

        # number of unique documents the token appears in
        self.frequency = 0

        # variables that are related to character traversal on postings list string
        self.length = 0
        self.next_pointer = 0
        self.pointer_alive = 0

        self.final_results = []
        self.index_of_posting = 0

        if all_files_postings_list:
            self.next_pointer = self.start_pointer
            self.pointer_alive = self.next_pointer
            self.postings_string = (
                self.file_ids if all_files_postings_list else lutil.load_postings_list(self.token)
            )
            self.frequency = len(
                list(
                    filter(
                        lambda x: not x.startswith(Characters.SKIP_POINTER),
                        self.postings_string.strip().split(" "),
                    )
                )
            )
            self.length = len(self.postings_string)
            return

        if self.token != Characters.EMPTY:
            stemmer = PorterStemmer()
            self.token = stemmer.stem(token.lower())

            self.postings_string = (
                self.file_ids if all_files_postings_list else lutil.load_postings_list(self.token)
            )
            self.frequency = len(
                list(
                    filter(
                        lambda x: not x.startswith(Characters.SKIP_POINTER),
                        self.postings_string.strip().split(" "),
                    )
                )
            )
            self.length = len(self.postings_string)

            if len(self.postings_string.strip()) == 0:
                self.contains_results = True
                return
            else:
                self.next_pointer = self.start_pointer
                self.pointer_alive = self.next_pointer
                return

        self.contains_results = True
        self.final_results = result

    def skip_pointer(self):
        if self.contains_results:
            skip_interval = math.sqrt(len(self.final_results))

            if self.index_of_posting % skip_interval == 0:
                if self.index_of_posting + skip_interval < len(self.final_results):
                    result = (self.final_results[self.index_of_posting + int(skip_interval)], skip_interval)
                    return result

        result = (Characters.EMPTY, 0)

        self.pointer_alive = self.next_pointer
        current = (
            Characters.EMPTY
            if self.pointer_alive >= len(self.postings_string)
            else self.postings_string[self.pointer_alive]
        )
        self.pointer_alive += 1
        characters_to_skip = 0
        skip = Characters.EMPTY
        skipped = Characters.EMPTY

        if current == Characters.SKIP_POINTER:
            characters_to_skip += 2
            current = self.postings_string[self.pointer_alive]
            self.pointer_alive += 1
            characters_to_skip += 1

            while current != " ":
                skip += current
                current = self.postings_string[self.pointer_alive]
                self.pointer_alive += 1
                characters_to_skip += 1

            self.pointer_alive += int(skip) - 1
            characters_to_skip += int(skip) - 1
            current = self.postings_string[self.pointer_alive]
            self.pointer_alive += 1
            characters_to_skip += 1

            while current != " ":
                skipped += current
                current = self.postings_string[self.pointer_alive]
                self.pointer_alive += 1
                characters_to_skip += 1

            characters_to_skip -= 1

        result = (skipped, characters_to_skip)
        return result

    # get frequency of appearance of a particular term
    def get_frequency(self):
        return len(self.final_results) if self.contains_results else self.frequency

    # get the final results from the execution
    def get_results(self):
        if self.contains_results:
            return self.final_results

        _ = [self.final_results.append(self.next()) for _ in range(self.frequency)]
        self.contains_results = True
        return self.final_results

    # skips the lagging index pointer by interval
    def next_index_skip(self, interval):
        if self.contains_results:
            self.index_of_posting += interval

    # skips the lagging pointer by interval
    def next_pointer_skip(self, interval):
        if not self.contains_results:
            self.next_pointer += interval

    # points to the next file id in the postings list
    def next(self):
        value = Characters.EMPTY
        if self.contains_results and self.index_of_posting < len(self.final_results):
            value = self.final_results[self.index_of_posting]
            self.index_of_posting += 1

            return value

        if self.next_pointer < self.start_pointer + self.length:
            accumulated = Characters.EMPTY
            self.pointer_alive = self.next_pointer

            while value == Characters.EMPTY:
                self.pointer_alive += 1
                current = (
                    Characters.EMPTY
                    if self.pointer_alive >= len(self.postings_string)
                    else self.postings_string[self.pointer_alive]
                )
                self.pointer_alive += 1
                if current == Characters.EMPTY: return value

                is_skip = current == Characters.SKIP_POINTER
                while current != " " and current != Characters.EMPTY:
                    if not is_skip: value += current

                    current = (
                        Characters.EMPTY
                        if self.pointer_alive >= len(self.postings_string)
                        else self.postings_string[self.pointer_alive]
                    )
                    self.pointer_alive += 1
                self.pointer_alive -= 1

            self.next_pointer = self.pointer_alive

        return value

# orchestrator for evaluating the boolean queries
class Search:
    def __init__(self, dict_file, postings_file):
        self.dict_file = dict_file
        self.postings_file = postings_file

        self.lutil = LoadingUtil(dict_file, postings_file)
        (
            self.file_ids,
            self.dictionary,
            self.all_file_postings_list,
        ) = self.lutil.load_dictionary()

    def process_query(self, query):
        queue = ShuntingYard.parse(query)
        stack = []

        operators = {BooleanOpertors.operator_and, BooleanOpertors.operator_or, BooleanOpertors.operator_not, BooleanOpertors.operator_anot}

        for token in queue:
            if token not in operators:
                stack.append(Token(self.lutil, token=token))
                continue

            # means there are two operands to be considered, except not which is unary
            first_operand = stack.pop()
            if token == BooleanOpertors.operator_not:
                stack.append(self.not_eval(first_operand))
                continue

            second_operand = stack.pop()
            if token == BooleanOpertors.operator_or:
                stack.append(self.or_eval(first_operand, second_operand))
                continue

            if token == BooleanOpertors.operator_and:
                stack.append(self.and_eval(first_operand, second_operand))
                continue

            if token == BooleanOpertors.operator_anot:
                stack.append(self.anot_eval(first_operand, second_operand))
                continue

        results = stack.pop().get_results()
        return " ".join(results)

    # logic for the not clause execution
    def not_eval(self, operand):
        all_postings_list_operand = Token(self.lutil, all_files_postings_list=True)
        a = operand.next()
        b = all_postings_list_operand.next()

        result = list()

        while a != Characters.EMPTY and b != Characters.EMPTY:
            if int(a) == int(b):
                a = operand.next()
                b = all_postings_list_operand.next()
                continue

            if int(a) >= int(b):
                result.append(b)
                b = all_postings_list_operand.next()
                continue

            if int(a) < int(b):
                result.append(a)
                a = operand.next()

        while b != Characters.EMPTY:
            result.append(b)
            b = all_postings_list_operand.next()

        return Token(self.lutil, result=result)

    # logic for the and-not combined clause execution
    def anot_eval(self, right_operand, left_operand):
        a, b = left_operand.next(), right_operand.next()

        result = []

        while a != Characters.EMPTY and b != Characters.EMPTY:
            if int(a) == int(b):
                a, b = left_operand.next(), right_operand.next()
                continue

            if int(a) >= int(b):
                b = right_operand.next()
                continue

            if int(a) < int(b):
                result.append(a)
                a = left_operand.next()

        while a != Characters.EMPTY:
            result.append(a)
            a = left_operand.next()

        return Token(self.lutil, result=result)

    # logic for the and clause execution
    def and_eval(self, left_operand, right_operand):
        if left_operand.get_frequency() > right_operand.get_frequency():
            return self.and_eval(right_operand, left_operand)
        else:
            result = []
            a, b = left_operand.next(), right_operand.next()
            while a != Characters.EMPTY and b != Characters.EMPTY:
                if int(a) == int(b):
                    result.append(a)
                    a, b = left_operand.next(), right_operand.next()
                    continue

                if int(a) < int(b):
                    (a_skip, a_skip_interval) = left_operand.skip_pointer()
                    if a_skip != Characters.EMPTY:
                        if int(a_skip) <= int(b):
                            left_operand.next_pointer_skip(a_skip_interval)
                            left_operand.next_index_skip(a_skip_interval)

                    a = a_skip if a_skip != Characters.EMPTY and int(a_skip) <= int(b) else left_operand.next()
                    continue

                if int(a) >= int(b):
                    (b_skip, b_skip_interval) = right_operand.skip_pointer()
                    if b_skip != Characters.EMPTY and int(b_skip) <= int(a):
                        right_operand.next_pointer_skip(b_skip_interval)
                        right_operand.next_index_skip(b_skip_interval)

                    b = b_skip if b_skip != Characters.EMPTY and int(b_skip) <= int(a) else right_operand.next()

            return Token(self.lutil, result=result)

    # logic for the or clause execution
    def or_eval(self, left_operand, right_operand):
        result = []

        if left_operand.contains_results:
            if len(left_operand.final_results) == 0:
                result = right_operand.get_results()
                return Token(self.lutil, result=result)

        if right_operand.contains_results:
            if len(right_operand.final_results) == 0:
                result = left_operand.get_results()
                return Token(self.lutil, result=result)

        a, b = left_operand.next(), right_operand.next()
        while a != Characters.EMPTY and b != Characters.EMPTY:
            if int(a) == int(b):
                result.append(a)
                a = left_operand.next()
                b = right_operand.next()
                continue

            if int(a) >= int(b):
                result.append(b)
                b = right_operand.next()
                continue

            if int(a) < int(b):
                result.append(a)
                a = left_operand.next()

        while a != Characters.EMPTY:
            result.append(a)
            a = left_operand.next()

        while b != Characters.EMPTY:
            result.append(b)
            b = right_operand.next()

        return Token(self.lutil, result=result)


def usage():
    print(
        f"usage: {sys.argv[0]} -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


def run_search(dict_file, postings_file, queries_file, results_file):
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
