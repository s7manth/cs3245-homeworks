#!/usr/bin/python3
import os
import re
import string
import nltk
import sys
import getopt
from nltk.stem.porter import PorterStemmer
nltk.download('punkt')


nltk.download('reuters')
from nltk.corpus import reuters

stemmer = PorterStemmer()

def tokenise_sentence(sentence):
    tokens = []
    punct  =  nltk.word_tokenize(sentence)
    for token in punct:
        if tokens not in list(string.punctuation):
            tokens.append(token)
    return tokens

def tokenise_text(text):
    sentences = re.compile('[.!?] ').split(text)
    return sentences

def stemming(word):
    return stemmer.stem(word)

def preprocessing(file):
    tokens = []
    for line in file:
        for sentence in tokenise_text(line):
            for word in tokenise_sentence(sentence):
                word.lower()
                stemmed_word = stemming(word)
                tokens.append(stemmed_word)
    return tokens
    # files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]


    
            


def usage():
    print(f"usage: {sys.argv[0]} -i directory-of-documents -d dictionary-file -p postings-file")
    tokenise_sentence("hello hello")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    index_dict = {}
    postings_list = {}

    files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
    for file_name in files:
        with open(os.path.join(in_dir, file_name), "r") as file:
            # print(file)
            tokens = preprocessing(file)
            for token in tokens:
                if token not in index_dict:
                    index_dict[token] = 1
                    postings_list[token] = []
                    postings_list[token].append(int(file_name))
                else:
                    index_dict[token] += 1
                    postings_list[token].append(int(file_name))

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
