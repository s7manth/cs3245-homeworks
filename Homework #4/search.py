import sys
import getopt
import math
import string
import heapq

from time import perf_counter
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams
from nltk import sent_tokenize, word_tokenize

# help function to format tokens
# def format_tokens(token):
#     stemmer = PorterStemmer()

#     result = stemmer.stem(token)
#     result = result.lower()

#     return result


# # function used to tokenize text
# def tokenize(text):
#     new_tokens = []
#     # text = text.lower()
#     # iterate thorugh lines and add tokens to token set
#     new_sentences = nltk.tokenize.sent_tokenize(text)
#     for sentence in new_sentences:
#         new_tokens = new_tokens + nltk.tokenize.word_tokenize(sentence)

#     return new_tokens

#opens dictionary file and creates object mapping word to position in postingsfile
def read_dictionary(dict_file):

    dictionary  = {}
    docs  = {}

    in_dictionary = True

    with open(dict_file, "rb") as file:
        lines = file.readlines()

        for _,line in enumerate(lines,0):

            line = line.decode('utf-8')

            if line == "\n":
                in_dictionary = False
                continue
            
            if in_dictionary:
                
                pointer = line.split(",")[0]
                word = line.split(",")[1]
                df = line.split(",")[2].replace("\n","")

                dictionary[word] = {"pointer": pointer, "df": df}
            else:
                docID = int(line.split(" ")[0])
                docLength = float(line.split(" ")[1].replace("\n",""))

                docs[docID] = docLength
    
    return dictionary, docs
#class Node for LinkedList (Boolean retrieval)
class Node_Boolean_Retrieval:
    def __init__(self, data):
        data = data[1:-1]

        data = data.split(",")

        # docID of this node
        self.data = int(data[0])

        # pointer to next node
        self.next = None

        # idx of skip node to identify possible skip
        self.skip_idx = data[2]

        # pointer to skip node
        self.skip = None

    def __repr__(self):
        return f"{self.data}"

    # directly add node to tail; only used when skip pointer not needed
    def add_node(self, data):
        node = Node_Boolean_Retrieval(data)

        self.next = node

        return node


# class LinkedList
class LinkedList_Boolean_Retrieval:
    def __init__(self):
        self.head = None
        self.tail = None

    def __repr__(self):
        if self.head == None:
            return ""

        resString = ""

        currNode = self.head

        while currNode:
            resString = resString + str(currNode) + " "
            currNode = currNode.next

        return resString.rstrip(" ")

    def add_node_quick(self, data):

        #create node to add
        node = Node_Boolean_Retrieval(data)

        if self.head == None:
            self.head = node
            self.tail = node
        else:

            self.tail.next = node

            self.tail = self.tail.next

        return node
    
    def add_node(self, data, idx):
        # create node to add
        node = Node_Boolean_Retrieval(data)

        # if linkedlist is empty add new node as head
        if self.head == None:
            self.head = node
            self.tail = node
        else:
            currNode = self.head

            # traverse through list until tail is found
            while currNode.next:
                currNode = currNode.next

                # if current node was assigned skip pointer to new node add skip pointer
                if currNode.skip_idx == idx:
                    currNode.skip = node

            # add node to list
            currNode.next = node
            self.tail = node

        return node

    # link other list to this list
    def add_list(self, node):
        
        #if list empty set start of new list as head
        if self.head == None:
            self.head = node

            #assign tail of list
            while node.next:
                node = node.next
            self.tail = node

        else:
            #add new list to tail
            self.tail.next = node

        #assign tail of list
        while node.next:
            node = node.next
            self.tail = node


# class Node for LinkedList (Vector Space)
class Node_Vector_Space:
    def __init__(self, data):
        # pointer to next node
        self.next = None

        data = data[1:-1]
        data = data.split(",")

        self.id = int(data[0])

        self.tf = int(data[1])

    def __repr__(self):
        return f"{self.id}"


# class LinkedList
class LinkedList_Vector_Space:
    def __init__(self):
        self.head = None
        self.tail = None

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def __repr__(self):
        if self.head == None:
            return ""

        resString = ""

        currNode = self.head

        while currNode:
            resString = resString + str(currNode) + " "
            currNode = currNode.next

        return resString.rstrip(" ")

    def add_node(self, data):
        # create node to add
        node = Node_Vector_Space(data)

        # if linkedlist is empty add new node as head
        if self.head == None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node

            self.tail = self.tail.next

        return node



# Class to retrieve postings list of single token
class BasicTerm:
    def __init__(self, word, dictionary, postings_file):
        stemmer = PorterStemmer()

        if word.startswith('"') and word.endswith('"'):
            word = word[1:-1]

        words = []
        for token in word_tokenize(word):
            result = word.lower()
            result = stemmer.stem(token)
            words.append(result)

        


        self.word = " ".join(words)
        self.dictionary = dictionary
        self.postings_file = postings_file

        print(self.word)

    def retrieve_list(self):
        if self.word not in self.dictionary.keys():
            return LinkedList_Boolean_Retrieval()

        with open(postings_file, "r") as file:
            file.seek(int(self.dictionary[self.word]["pointer"]))

            line = file.readline().replace(" \n", "").rstrip(" ").split(" : ")[1]

        linkedList = LinkedList_Boolean_Retrieval()

        values = line.split(" ")

        for idx, v in enumerate(values, 0):
            data = v

            linkedList.add_node(data, idx)

        print(linkedList)
        print(self.word)

        return linkedList

    def evaluate(self):

       

        return self.retrieve_list()
    
class Term:

    def __init__(self, queryL, queryR, operation, dictionary, postings_file):
        
        #left side of term
        self.queryL = queryL

        # right side of term
        self.queryR = queryR

        # operation (OR, AND, NOT)
        self.operation = operation

        self.postings_file = postings_file
        self.dictionary = dictionary
       
    #creates Term object from raw query
    def evaluateQuery(self, query):

        
        #return empty list of empty queries
        if query == "":
            return LinkedList_Boolean_Retrieval()

        # split query in tokens
        elements = query.split(" ")

        # if query just a single token create BasicTerm to return postings list
        if "AND" not in query:
            term = BasicTerm(query, self.dictionary, self.postings_file)
            return term.evaluate()

        # tokens of left side of term
        l_list = []

        # tokens of right side of term
        r_list = []

        # left side of term
        queryL = ""

        # right side of term
        queryR = ""

        # operation of term
        operation = None
                
        #iterate through all elements to find AND-operator (second lowest precedence)
        for idx, element in enumerate(elements,0):

            
            #if NOT-operator found create AND-Term
            if element in ["AND"]:
                # assign left and right side
                l_list = elements[:idx]
                r_list = elements[idx + 1 :]

                # assign operator
                operation = element

                # transfer lists into strings for term
                queryL = " ".join(l_list)
                queryR = " ".join(r_list)

                
                term = Term(queryL, queryR, operation, self.dictionary, self.postings_file)

                # return evaluated term as LinkedList
                return term.evaluate()
            
        return LinkedList_Boolean_Retrieval()

    def AND(self):
        result = LinkedList_Boolean_Retrieval()
        resultTail = None

        self.left = self.evaluateQuery(self.queryL)
        self.right = self.evaluateQuery(self.queryR)
        
        left = self.left.head
        right = self.right.head

        if right == None or left == None:
            return result

        idx = 0
        while left != None and right != None:
            if left.data == right.data:
                if resultTail == None:
                    resultTail = result.add_node(f"({left.data},-1,-1)", idx)
                else:
                    resultTail = resultTail.add_node(f"({left.data},-1,-1)")
                idx = idx + 1
                right = right.next
                left = left.next
                continue

            if left.data > right.data:
                while right.skip != None and right.skip.data <= left.data:
                    right = right.skip
                while right != None and right.data < left.data:
                    right = right.next
                continue

            if left.data < right.data:
                while left.skip != None and left.skip.data <= right.data:
                    left = left.skip
                while left != None and left.data < right.data:
                    left = left.next
                continue

        return result 
    #not relevant
    def OR(self):
        
        self.left = self.evaluateQuery(self.queryL)

        self.right = self.evaluateQuery(self.queryR)
        
        right = self.right.head

        if right == None:
            return self.left
        else:
            return self.right


    def evaluate(self):
        if self.operation == "AND":
            return self.AND()

        if self.operation == "OR":
            return self.OR()
        


class Boolean_Retrieval_Searcher:

    def run_search(self, dict_file, postings_file, query, results_file):
        dictionary, _ = read_dictionary(dict_file)

        dictionary,_ = read_dictionary(dict_file)
            
        #pre compute LinkedList of all elements for 
        start = perf_counter()

        out = open(results_file, "w")

        query = query.rstrip("\n")
        
        term = Term(query, "", "OR", dictionary, postings_file)
        out.write(f"{str(term.evaluate())}\n")

        end = perf_counter()

        print(f"Total time for boolean retrieval {end-start} seconds")


class Free_Text_Searcher:
    
   

    # reads postings list from file into memory for a single word
    def read_postings_list(self, word, dictionary, postings_file):
        if word not in dictionary.keys():
            return LinkedList_Vector_Space()

        with open(postings_file, 'rb') as file:
                file.seek(int(dictionary[word]["pointer"]))
                
                line = file.readline()

        linkedList = LinkedList_Vector_Space()

        values = line.split(" ")

        for _, v in enumerate(values, 0):
            data = v

            linkedList.add_node(data)

        return linkedList

    # computes weights of word with tf and idf
    def compute_weight(self, N, df, tf, t, d):
        # for natural tf
        if t == "n":
            tF = tf

        # for logarithmic tf
        else:
            tF = 1 + math.log(tf, 10)

        # for no df
        if d == "n":
            dF = 1

        # for idf
        else:
            dF = math.log(N / df, 10)

        return dF * tF

    # calculates weights for word in query
    def calculate_score_for_word(
        self, dictionary, df, tf_q, word, postings_file, N, scores
    ):
        # read postings list of word
        postings_list = self.read_postings_list(word, dictionary, postings_file)

        # compute query weight for word
        w_q = self.compute_weight(N, df, tf_q, "l", "t")

        # iterate through all nodes in postings list
        for curr_node in postings_list:
            # read docID for each posting
            docID = curr_node.id

            # add document to scores if it hasn't appeared yet for query
            if docID not in scores.keys():
                scores[docID] = 0

            # get tf from posting
            tf = curr_node.tf

            # computes document weight for word
            w_d = self.compute_weight(N, df, tf, "l", "n")

            # add to scores for respective document
            scores[docID] = scores[docID] + w_q * w_d

    # iterates through all tokens of query and calculates score for all relevant documents (documents including at least one token of the query)
    def compute_similarities(self, dictionary, query, postings_file, docs):
        # assign total number of documents to variable N
        N = len(docs)

        # init scores
        scores = {}

        stemmer = PorterStemmer()  # stemmer initialisation
        sws = set(stopwords.words("english"))  # stopwords
        punct = set(string.punctuation)  # punctuations

        stopword_filter = lambda word: word not in sws  # stopword removal
        punctuation_filer = lambda word: word not in punct # punctuation removal

        # format query and get tokens
        query_tokens = [
            stemmer.stem(word).lower()  # stemming
            for st in sent_tokenize(query)  # document to lines tokenisation
            for word in word_tokenize(st)  # lines to words tokenisations
        ]

        query_tokens = list(filter(stopword_filter, query_tokens))
        query_tokens = list(filter(punctuation_filer, query_tokens))

        # go through every unique word in query
        for word in set(query_tokens):
            # skip if word is unknown
            if word not in dictionary.keys():
                continue

            # get df of word from dictionary
            df = int(dictionary[word]["df"])

            # update scores dictionary for this word
            self.calculate_score_for_word(
                dictionary, df, query_tokens.count(word), word, postings_file, N, scores
            )

        # iterate through all scores apply cosine normalization (scores do not get divided by query length because it has the same effect on all docs)
        for d in scores.keys():
            scores[d] = scores[d] / docs[d]

        return scores

    # retrieves documents with top K scores
    def create_ranking(self, scores, K):
        ranking_items = scores.items()

        top_lK = heapq.nlargest(10 * K, ranking_items, key=lambda d: d[1])
        ranking = sorted(top_lK, key=lambda d: (-d[1], d[0]))

        if len(ranking) < K:
            return ranking
        return ranking[:K]

    def run_search(self, dict_file, postings_file, query, results_file):

        #read from files
        dictionary, docs = read_dictionary(dict_file)

        start = perf_counter()

        # open output document
        output = open(results_file, "w")

        # compute scores
        scores = self.compute_similarities(dictionary, query, postings_file, docs)

        # retrieve top 10 scores
        rankings = self.create_ranking(scores, 10)

        # filter out score values and only keep docIDs
        docIDs = [str(item[0]) for item in rankings]

        # write into output file
        output.write(f'{" ".join(docIDs)}\n')

        output.close()

        end = perf_counter()
        print(f"Total time {end-start} seconds")


def check_boolean_search(query):
    operators = ["AND", "NOT", "OR"]

    for operator in operators:
        if operator in query:
            return True

    return False


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print("running search on the queries...")

    with open(queries_file, "r", encoding="utf8", errors="ignore") as file:
        query = file.readline()

    if check_boolean_search(query):
        searcher = Boolean_Retrieval_Searcher()

    else:
        searcher = Free_Text_Searcher()

    searcher.run_search(dict_file, postings_file, query, results_file)
    # This is an empty method
    # Pls implement your code in below


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


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
