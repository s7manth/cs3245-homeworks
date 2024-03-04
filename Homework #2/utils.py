import os
import pickle

class BooleanOpertors:
   operator_and = "AND"
   operator_or = "OR"
   operator_not = "NOT"
   operator_anot = "ANOT"

class Parentheses:
    left = "("
    right = ")"

class LoadingUtil:
    def __init__(self, output_dictionary_path, output_postings_path):
        self.output_postings_path = output_postings_path
        self.output_dictionary_path = output_dictionary_path

        self.file_ids: list[str] = list()
        self.dictionary: dict[str, int] = {}

        self.__post_init__()

    def __post_init__(self):
        if not os.path.exists(self.output_postings_path):
            raise RuntimeError("ERROR: output postings path doesnt exist")

        if not os.path.exists(self.output_dictionary_path):
            raise RuntimeError("ERROR: output dictionary path doesnt exist")

    def load_postings_list(self, token):
        assert len(self.dictionary) > 0
        postings_list = str()
        with open(self.output_postings_path, "rb") as postings_file:
            if token not in self.dictionary:
                return postings_list
            postings_file.seek(self.dictionary[token])
            postings_list = pickle.load(postings_file)

        return postings_list

    def load_dictionary(self):
        with open(self.output_dictionary_path, "rb") as dictionary_file:
            self.file_ids = pickle.load(dictionary_file)
            self.dictionary = pickle.load(dictionary_file)
            all_file_postings_list = pickle.load(dictionary_file)

        return self.file_ids, self.dictionary, all_file_postings_list


class ShuntingYard:
    @staticmethod
    def parse(query):
        operators = {
            BooleanOpertors.operator_and,
            BooleanOpertors.operator_or,
            BooleanOpertors.operator_not,
            BooleanOpertors.operator_anot
        }
        operator_precedence = {
            BooleanOpertors.operator_not: 2,
            BooleanOpertors.operator_and: 1,
            BooleanOpertors.operator_anot: 1,
            BooleanOpertors.operator_or: 0
        }

        tokens = query.split(" ")
        parsed_entities = []

        for t in tokens:
            t_copy = t
            while t_copy[0] == Parentheses.left:
                parsed_entities.append(Parentheses.left)
                t_copy = t_copy[1:]

            right_parentheses_count = 0
            while t_copy[-1] == Parentheses.right:
                right_parentheses_count += 1
                t_copy = t_copy[:-1]

            parsed_entities.append(t_copy)
            _ = [parsed_entities.append(Parentheses.right) for _ in range(right_parentheses_count)]

        output_queue = []
        operator_s = []

        while parsed_entities:
            current = parsed_entities.pop(0)
            if parsed_entities and current == BooleanOpertors.operator_and and parsed_entities[0] == BooleanOpertors.operator_not:
                current = BooleanOpertors.operator_anot
                parsed_entities.pop(0)

            if current not in operators and current != Parentheses.left and current != Parentheses.right:
                output_queue.append(current)

            if current in operators:
                while (
                    len(operator_s) != 0
                    and operator_s[len(operator_s) - 1] != Parentheses.left
                    and (
                        (
                            0 if len(operator_s) == 0 else operator_precedence[operator_s[-1]]
                            > operator_precedence[current]
                        )
                        or (
                            0 if len(operator_s) == 0 else operator_precedence[operator_s[-1]]
                            == operator_precedence[current]
                            and current != BooleanOpertors.operator_not
                        )
                    )
                ):
                    output_queue.append(operator_s.pop())
                operator_s.append(current)

            if current == Parentheses.left:
                operator_s.append(current)

            if current == Parentheses.right:
                while operator_s[len(operator_s) - 1] != Parentheses.left:
                    output_queue.append(operator_s.pop())
                operator_s.pop()

        while operator_s:
            output_queue.append(operator_s.pop())
        return output_queue
