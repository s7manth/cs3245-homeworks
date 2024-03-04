This is the README file for A0226581A and A0226618B's submission
Email(s): e0638867@u.nus.edu, e0638904@u.nus.edu

== Python Version ==

We're using Python Version 3.11.1 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps
in your program, and discuss your experiments in general. A few paragraphs
are usually sufficient.

Our program mainly consists of three files that contain code that help us in indexing and searching. The indexing steps are handled by the file "index.py"
- In the indexing file, we are mainly handling the creation of index for the terms existing in the documents provided in the reuters collection of NLTK. 
- We start by doing a sanity check on the path of the documents provided, to ensure proper reading of documents. Next, we preprocess the documents by using the NLTK library, that helps us tokenise the documents into sentences, and sentences into words. 
- We next lowercase the tokens, and then perform stemming on the tokens with the help of Porter Stemmer. We also remove punctuations and stop words from the list of tokens to speed up indexing since these will not be of use while indexing. 
- Once this is done, we check if a perticular token already exists in the index vocabulary, and if it does we add the particular document in its posting list. If not, we add it to the vocabulary and initialise its posting list with te particular document. Once the posting lists are created for every token in all the documents, we proceed with initialising the skip pointers. 
- The serialize_with_skip_pointers function takes a postings list as input and serializes it with skip pointers. It calculates an interval based on the square root of the list length and iterates through the list, appending each element to the result string. This allows us to quickly iterates through huge posting lists while solving queries. 
- To save all the posting lists with their respective skip pointers, we use the "save" function. First, it serializes postings for each token in the vocabulary using serialize_with_skip_pointers method and stores them in postings_serialized. Then, it iterates through these serialized postings, writes them to a binary file (postings_file), and updates the dictionary with the corresponding positions in the file. This concludes the process of indexing in our assingment.

We have then written a file utils.py that help us read the pickled files for searching and parse the queries.
This file contains two classes: LoadingUtil and ShuntingYard.

LoadingUtil:

- This class provides functionality for loading data from files.
Upon initialization, it takes paths to the output postings and dictionary files.
The load_postings_list method loads a postings list for a given token by seeking its position in the postings file and unpickling the data.
The load_dictionary method loads file IDs, dictionary mappings, and a serialized postings list for all file IDs from the dictionary file.

ShuntingYard:

- This class implements the Shunting Yard algorithm for parsing boolean queries.
The parse static method takes a boolean query as input and parses it into a list of tokens.
It then converts the infix notation of the query into a postfix (RPN) notation using the Shunting Yard algorithm, considering operator precedence rules.
The resulting postfix expression facilitates the evaluation of boolean queries.

search.py is the file where the code and algorithms for executing the queries and searching the postings list for the answer to the queries happen.

- The main components in searching are Token and Search classes. 
- Token class takes care of the two terms/tokens with their individual postings lists retrieved from the disk to perform boolean mechanisms on it. 
- Search class acts like an orchestrator that evaluates a query converted to postfix form by passing the Tokens around to evaluate individual boolean clauses. This is taken care of by a stack which has these elements that are popped as they are evaluated.  
- The interesting thing about the retrieval of postings list is that 
the entire postings list is retrieved for a particular stemmed token. This postings list is a flattened version with skip pointer indicators (+). 
- A more efficient implementation can be one where the postings list too is frugally retrieved. This would consume less memory while execution. 
- A lot of the processing inside of Token is done using pointer variables which take care of the character addressing inside the postings list. 

== Files included with this submission ==

Directory structure of the files:
```
.
├── README.txt
├── index.py
├── search.py
└── utils.py
```

== Statement of individual work ==

[x] We, A0226618B and A0226581A, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, AXXXXXXXX, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

- https://mathcenter.oxford.emory.edu/site/cs171/shuntingYardAlgorithm/
- https://nlp.stanford.edu/IR-book/html/htmledition/faster-postings-list-intersection-via-skip-pointers-1.html
- https://github.com/drishabh/Info-Storage-and-Retrieval 
