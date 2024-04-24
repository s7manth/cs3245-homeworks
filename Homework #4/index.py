import sys
import getopt
import math
import csv
import string

from collections import Counter, defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams
from nltk import sent_tokenize, word_tokenize
from tqdm import tqdm

# restructure postings object
# def invert_postings(inverted_postings):
#     postings_list = []

#     # iterate through all docIDs and put them in list of dictionaries of all words they include
#     for docID in inverted_postings.keys():
#         for word in inverted_postings[docID]:
#             postings_list.append({"key": word, "doc": docID})

#     return postings_list


# computes weights for words to calculate document length
def compute_weight(tf):
    tF = 1 + math.log(tf, 10)
    dF = 1
    return tF * dF

# calculates document length for cosine normalization
# def calculate_doc_length(postingsList):
#     lengths = {}

#     for docID in postingsList.keys():
#         counts = Counter(postingsList[docID])
#         countsValues = sorted(counts.values())
#         countsValuesWeighted = [compute_weight(value) for value in countsValues]
#         summation = sum(countsValue * countsValue for countsValue in countsValuesWeighted)
#         lengths[docID] = math.sqrt(summation)

#     return lengths


# consolidate postings to postings list
def consolidate(postings_unsorted):
    postings = sorted(postings_unsorted, key=lambda d: d["key"])
    result = []

    curr_term = ""
    curr_value_list = {}

    for _, item in enumerate(postings, 0):
        # if first term assign values to variables
        if curr_term == "":
            curr_term = item["key"]
            curr_value_list[int(item["doc"])] = 1
            continue

        # else if still the same key consolidate
        if curr_term == item["key"]:
            # if doc already part of postings list for word increment
            if int(item["doc"]) in curr_value_list.keys():
                curr_value_list[int(item["doc"])] = (
                    curr_value_list[int(item["doc"])] + 1
                )
            # else append document to postings list
            else:
                curr_value_list[int(item["doc"])] = 1

        # if different key: turn postings list into string, and add to result
        else:
            # create postings list for item
            curr_item = {
                "key": curr_term,
                "df": len(curr_value_list.keys()),
                "postings_list": curr_value_list,
            }

            # add to result
            result.append(curr_item)

            # init new values
            curr_item = None
            curr_term = item["key"]
            curr_value_list = {}
            curr_value_list[int(item["doc"])] = 1

    # add last postings list to result
    curr_item = {
        "key": curr_term,
        "df": len(curr_value_list.keys()),
        "postings_list": curr_value_list,
    }
    result.append(curr_item)

    return result


# writes indexing data into files
def write_into_file(out_postings, out_dict, postings, document_length, vocabulary, document_frequency):
    # create postings lists
    # postings = invert_postings(postingsList)

    # compute document lengths
    # lengths = calculate_doc_length(postingsList)

    # consolidate postings list
    # result = consolidate(postings)

    # token -> { postion, df }
    dictionary = dict()

    # start position for pointers
    position = 0

    with open(out_postings, "w") as out:
        # iterate through all postings
        for token in vocabulary:
            # calculate distance between skips
            skip_step = int(math.sqrt(len(postings[token])))

            # create entry for dictionary
            # dict.write(f"{position},{item['key']},{item['df']}\n")
            dictionary[token] = (position, document_frequency[token])

            pListStr = []

            docs = postings[token].keys()
            number_of_docs = len(docs)
            sorted_postings = sorted(docs)

            # sort postings according to docID
            for idx, c in enumerate(sorted_postings):
                if idx % skip_step == 0 and idx + skip_step < number_of_docs:
                    # if skip pointer add to end of entry
                    pListStr.append(f"({c},{postings[token][c]},{int(idx+skip_step)})")
                else:
                    # if no skip pointer use -1 instead
                    pListStr.append(f"({c},{postings[token][c]},-1)")

            # create entry for postings file
            entry_postings = f"{token} : {' '.join(pListStr)}\n"

            # write into postings file
            out.write(entry_postings)

            # update pointer
            position += len(entry_postings.encode("utf-8"))


    with open(out_dict, "w") as file:
        # write document lengths into dictionary.txt seperated by empty line
        for k, v in dictionary.items():
            file.write(f"{v[0]},{k},{v[1]}\n")

        file.write("\n")

        for docID in document_length:
            file.write(f"{docID} {document_length[docID]}\n")


# creates dictionary and prepares postings
def create_dict(data_dir, out_dict, out_postings):
    print("creating dict...")

    # retrieve all entries
    csv.field_size_limit(1000000000)

    postings = defaultdict(lambda: defaultdict(int)) # token -> { doc -> how many times in it? }
    document_length = defaultdict(int) # doc -> length
    vocabulary = set() # unique tokens
    document_frequency = defaultdict(int) # token -> how many docs does it appear in? 

    stemmer = PorterStemmer()  # stemmer initialisation
    sws = set(stopwords.words("english"))  # stopwords
    punct = set(string.punctuation)  # punctuations

    stopword_filter = lambda word: word not in sws  # stopword removal
    punctuation_filer = lambda word: word not in punct # punctuation removal

    with open(data_dir, "r", encoding="utf-8", errors="ignore") as csvfile:
        datareader = csv.reader(csvfile)
        next(datareader)

        for entry in tqdm(datareader):
            # read out all structure elements of entry (possibly used at later stage)
            docID, _title, text, _date, _court = entry

            # tokenize text
            # positional indexing could be implemented here!
            tokens = [
                stemmer.stem(word).lower()  # stemming
                for st in sent_tokenize(text)  # document to lines tokenisation
                for word in word_tokenize(st)  # lines to words tokenisations
            ]

            tokens = list(filter(stopword_filter, tokens))
            tokens = list(filter(punctuation_filer, tokens))

            # bigrams and trigrams
            bigrams = ngrams(tokens, 2)
            trigrams = ngrams(tokens, 3)

            bigrams = list(map(lambda x: " ".join(x), bigrams))
            trigrams = list(map(lambda x: " ".join(x), trigrams))

            tokens += bigrams
            tokens += trigrams

            document_length[docID] = len(tokens)

            for token in tokens:
                if not token in vocabulary:
                    vocabulary.add(token) # add the token to a dictionary of all existing tokens

                if not docID in postings[token]:
                    document_frequency[token] += 1 # track the number of documents the token appears in

                postings[token][docID] += 1 # increasse the tf for the particlar token, doc pair


    write_into_file(out_postings, out_dict, postings, document_length, vocabulary, document_frequency)


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -i directory-of-documents -d dictionary-file -p postings-file"
    )


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory and
    store it in output dictionary and postings
    """
    print("indexing...")

    create_dict(in_dir, out_dict, out_postings)


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:d:p:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-i":  # input directory
        input_directory = a
    elif o == "-d":  # dictionary file
        output_file_dictionary = a
    elif o == "-p":  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if (
    input_directory == None
    or output_file_postings == None
    or output_file_dictionary == None
):
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
