This is the README file for A0290035MX's submission
Email(s): e1324528@u.nus.edu

== Python Version ==

I'm (We're) using Python Version 3.9.6 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Overview of your system

    Our system is compromissed out of two modules.
    A indexing scipt and a search script

System architectur
    Indexing (index.py):

        Formats:

            - dictionary:
                {position of term},{term},{document frequency}
                {linebreak}
                {docID} {document length}

            - postings:
                {term} : {postings}

            Formatting and tokenization:
                - stopword removal
                - removal of punctuation
                - stemming
                - lowering
                - tokenization with nltk word_tokenize and sent_tokenize

            Methods:

                create_dict(data_dir, out_dict, out_postings): reads all cases from the csv file and applies formating/tokenization and creates postings, document lengths and dictionary
                write_into_file(out_postings, out_dict, postings, document_length, vocabulary, document_frequency): adds skip pointers with a step size of sqrt_length_postings_list and use pickle do write into  postings and dictionary


    Search (search.py):

        Our search consists out of boolean retrieval and free text search

        Boolean retrieval:

            LinkedList:

                Classes:
                    - Node: node of LinkedList with data, a pointer to the next element, and a pointer to skip node
                    - LinkedList: a class that implements add_node and has a pointer to the head and tail of LinkedList


            Computation of queries:

                Description:
                    - query gets split with the creation of Terms recursively when operators are found
                    - operation with lower priority gets split first (OR -> AND -> NOT -> ())
                    - if the lowest level is reached, a BasicTerm gets created to retrieve the postings list
                    - Terms compute the intermediary result of an operation with a postings list and operators
                    - because the priority operation gets split first, the high-priority operations get computed first

                Classes:
                    - BasicTerm
                        Methods:
                            def retrieve_list(self): returns postings list of token as stored in postings.txt
    
                    - Term
                        Methods:
                            def evaluate(self): returns result of query after converting it into a term
                            def evaluateQuery(self, query): splits term into subterms
                            def OR(self): returns non-empty term
                            def AND(self): merges two postings lists

                Methods:
                    run_search(self, dict_file, postings_file, query, results_file): runs boolean retrieval search


        Free text search:

            LinkedList:

                We have implemented a LinkedList for boolean retrieval and one for free text search

                Boolean Retrieval
                Classes:
                    - Node: node of LinkedList with data, a pointer to the next element, and a pointer to skip node
                    - LinkedList: a class that implements add_node, has a pointer to the head of LinkedList and pointer to tail of LinkedList


            Computation of queries:

                Methods:
                    read_postings_list(word, dictionary, postings_file): reads postings list from file into memory for a single word
                    read_dictionary(dict_file): reads dictinary into memory including pointer to postings file, word and document frequency and document lengths
                    compute_weight(N, df, tf, t, d): computes weights of word with tf and idf
                    calculate_score_for_word(dictionary, df, tf_q, word, postings_file,N, scores): calculates weights for word in query
                    compute_similarities(dictionary, query, postings_file, docs): iterates through all tokens of query and calculates score for all relevant documents (documents including at least one token of the query)
                    create_ranking(scores): retrieves documents with top K scores
                    read_queries(queries_file): reads sanity-queries

Techniques used to improve the retrieval performance

Allocation of work to each of the individual members of the project team


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py: Reads documents and writes into postings and dictionaries. Files
search.py: implements search algorithm. Reads queries and computes results with the help of an index
README.txt: this file describes project components
dictionary.txt: file containing dictionary and document lengths
postings.txt: file containing postings lists

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I/We, A0290035M, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0290035M, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

https://www.nltk.org/
https://www.python.org/doc/
