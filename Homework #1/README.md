This is the README file for A0226581A's submission
Email: e0638867@u.nus.edu

== Python Version ==

I'm using Python Version 3.11.1 for this assignment.

== General Notes about this assignment ==

> General working flow: 
- Assignment tasks one to construct a simple n-gram language model for the purpose of language detection 
- Training file contains linewise language and sentence pairs separated by a whitespace which needs to be parsed properly 
- The language forms the label for training data 
- The testing file contains just the sentences for which the language needs to be predicted using the n-gram model 
- The final output is to be written to a separate file in a similar format to that of training data (linewise language and sentence pairs)
- `input.correct.txt` is provided to check the prediction capability of the model 

> About the model itself: 
- Model used in this assignment is the character-level 4-gram language model 
- Each language is profiled on the basis of raw counts as to how many times a particular n-gram has occured in the training data given 
- There were two hyperparameters that I played around with. `THRESHOLD` was to determine whether the given sentence belongs to any of the language learnt. This `THRESHOLD` is a percentage of how many n-grams in the given sentence are absolutely new. If the minimum for all the three languages is crossing 70%, then the sentence is marked as "other". The other hyperparameter is `K` which is the value used to smooth the language model ratios upon encountering a new n-gram that doesn't exist in a language but is a part of the training data. The value chosen for `K` is 1, which in other words is Laplacian Add One Smoothing.

== Files included with this submission ==
```
.
├── build_test_LM.py
├── out.txt
└── README.txt
```

- `build_test_LM.py` houses the code to build the n-gram language model on training data and running the same on test data to get the language detection predictions. 
- `out.txt` is the file where the output is written to after running `build_test_LM.py`. 
- `README.txt` is this file. 

== Statement of individual work ==

[x] I, A0226581A, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

None. 

