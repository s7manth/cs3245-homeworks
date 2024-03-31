This is the README file for A0226581A and A0226618B's submission
Email(s): e0638867@u.nus.edu, e0638904@u.nus.edu

== Python Version ==

We're using Python Version 3.11.1 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps
in your program, and discuss your experiments in general.  A few paragraphs
are usually sufficient.

Our program mainly consists of three files that contain code that help us in indexing and searching. The indexing steps are handled by the file "index.py"
- In the indexing file, we are mainly handling the creation of index for the terms existing in the documents provided in the reuters collection of NLTK.
- We start by doing a sanity check on the path of the documents provided, to ensure proper reading of documents. Next, we preprocess the documents by using the NLTK library, that helps us tokenise the documents into sentences, and sentences into words.
- We next lowercase the tokens, and then perform stemming on the tokens with the help of Porter Stemmer. We also remove punctuations and stop words from the list of tokens to speed up indexing since these will not be of use while indexing.
- Once this is done, we check if a perticular token already exists in the index vocabulary, and if it does we add the particular document in its posting list. If not, we add it to the vocabulary and initialise its posting list with te particular document. For the posting list, we store the token with the corresponding documents it occurs in, with the number of times it appears in the document.
- We also store the number of documents this token appears in, later to be used in idf calculation.
- After all this indexing for every token in every document, we save it in the memory using `pickle.dump`

We have then written a file utils.py that help us read the pickled files for searching and parse the queries.
This file contains a LoadingUtil class:

LoadingUtil:

- This class provides functionality for loading data from files.
Upon initialization, it takes paths to the output postings and dictionary files.
The load_document_data method loads a postings list for a given token by seeking its position in the postings file and unpickling the data. This return a tokens term frequency for every document it occurs in.
The load_dictionary method loads file IDs, document frequencies, document length and the dictionary file to be used later for searching.

search.py is the file where the code and algorithms for executing the queries and searching the postings list for the answer to the queries happen.
The `Search` class contains all the fields and the methods necessary for us to perform the searching. We are maintaining two dictionaries `tf_score_query` and `idf_score_query` to maintain the tf-idf score of a query and the idf score for every token present in the vocab.

The `calc_idf` function calculates the idf score for every token in the dictionary, corresponding to the number of documents it occurs in.
The `process_query` function takes in a query, preprocesses it just like the documents and then calculates the tf_idf for every query term. It then calculates the score for every document by using the Cosine Formula given in the book, which also uses normalisation using the length of the document.
We then return the top documents (limit 10), for a particular query dependant on the score.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0000000X, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

- Python documentation (https://docs.python.org)
- Introduction to Information Retrieval book (https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf)
