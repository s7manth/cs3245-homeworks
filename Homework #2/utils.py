import os
import pickle

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
            if token not in self.dictionary: return postings_list
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
        operators = {"AND", "OR", "NOT", "ANOT"}
        operator_precedence = {"NOT":2,"AND":1,"ANOT":1,"OR": 0}

        def top_operator_precedence(stack):
            if len(stack) == 0:
                return 0
            return operator_precedence[stack[-1]]

        tokens = query.split(" ")
        query_tokens = []
        for t in tokens:
            current = t
            while(current[0] == "("):
                query_tokens.append("(")
                current = current[1:]
            end_parenthese_cnt = 0
            while(current[-1] == ")"):
                end_parenthese_cnt += 1
                current = current[:-1]
            query_tokens.append(current)
            for _ in range(end_parenthese_cnt):
                query_tokens.append(")")
        output_queue = []
        operator_stack = []
        while query_tokens:
            current = query_tokens.pop(0)
            if query_tokens and current == "AND" and query_tokens[0] == "NOT":
                current = "ANOT"
                query_tokens.pop(0)
            if current not in operators and current != "(" and current != ")":
                output_queue.append(current)
            if current in operators:
                while len(operator_stack) != 0 and operator_stack[len(operator_stack)-1] != "(" and ((top_operator_precedence(operator_stack) > operator_precedence[current]) or (top_operator_precedence(operator_stack) == operator_precedence[current] and current != "NOT")):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(current)
            if current == "(":
                operator_stack.append(current)
            if current == ")":
                while operator_stack[len(operator_stack) -1] != "(":
                    output_queue.append(operator_stack.pop())
                operator_stack.pop()
        while operator_stack:
            output_queue.append(operator_stack.pop())
        return output_queue
