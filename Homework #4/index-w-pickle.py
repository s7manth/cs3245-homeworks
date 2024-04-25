import sys
import getopt
import math
import csv
import string
import lzma
try: 
    import cPickle as pickle
except:
    import pickle

from time import perf_counter
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams
from nltk import sent_tokenize, word_tokenize
from tqdm import tqdm


# computes weights for words to calculate document length
def compute_weight(tf):
    tF = 1 + math.log(tf, 10)
    dF = 1
    return tF * dF

# writes indexing data into files
def write_into_file(out_postings, out_dict, postings, document_length, vocabulary, document_frequency):

    # token -> { postion, df }
    dictionary = dict()

    # start position for pointers
    position = 0

    # iterate through all postings

    with lzma.open(out_postings, "wb") as file:
        position = 0
        for token in tqdm(vocabulary):
            # calculate distance between skips
            skip_step = int(math.sqrt(len(postings[token])))

            # create entry for dictionary
            # dict.write(f"{position},{item['key']},{item['df']}\n")
            # dictionary[token] = (position, document_frequency[token])

            position = file.tell()

            dictionary[token] = (position, document_frequency[token]) # store dictionary

            pListStr = []

            docs = postings[token].keys()
            number_of_docs = len(docs)
            sorted_postings = sorted(docs)

            # sort postings according to docID
            for idx, c in enumerate(sorted_postings):
                if idx % skip_step == 0 and idx + skip_step < number_of_docs:
                    # if skip pointer add to end of entry
                    pListStr.append(f"({c},{postings[token][c]},{int(idx + skip_step)})")
                else:
                    # if no skip pointer use -1 instead
                    pListStr.append(f"({c},{postings[token][c]},-1)")

            # create entry for postings file
            # entry_postings = f"{token} : {}\n"

            pstring = " ".join(pListStr)

            pickle.dump(pstring, file, pickle.HIGHEST_PROTOCOL)

            # postings_for_pickling.append(entry_postings)

            # update pointer
            # position += len(entry_postings.encode("utf-8"))

    with lzma.open(out_dict, "wb") as file:
        # write document lengths into dictionary.txt seperated by empty line
        pickle.dump(dictionary, file, pickle.HIGHEST_PROTOCOL)
        pickle.dump(document_length, file, pickle.HIGHEST_PROTOCOL)

        # for k, v in dictionary.items():
        #     file.write(str.encode(f"{v[0]},{k},{v[1]}\n"))

        # file.write(str.encode("\n"))

        # for docID in document_length:
        #     file.write(str.encode(f"{docID} {document_length[docID]}\n"))


# creates dictionary and prepares postings
def create_dict(data_dir, out_dict, out_postings):
    print("creating dict...")

    start = perf_counter()

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

    end = perf_counter()
    print(f"Total time {end - start} seconds")


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
