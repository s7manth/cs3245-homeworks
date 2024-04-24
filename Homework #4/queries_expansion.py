# Import necessary modules from NLTK library
from nltk import word_tokenize, pos_tag, PorterStemmer
from nltk.corpus import wordnet

# Initialize Porter Stemmer for stemming words
stemmer = PorterStemmer()


# Function to map NLTK POS tags to WordNet POS tags
def wordnet_tag(tag):
    if tag[0] == "N":
        return wordnet.NOUN
    elif tag[0] == "J":
        return wordnet.ADJ
    elif tag[0] == "V":
        return wordnet.VERB
    elif tag[0] == "R":
        return wordnet.ADV
    return None


# Function to get unique synonyms for a word
def unique_synonyms(synonyms):
    words = []
    unique_synonyms = []

    for synonym in synonyms:
        word_name = synonym.lemma_names()[0]  # Get the name of the synonym
        
        if word_name not in words:
            words.append(word_name)
            unique_synonyms.append(synonym)

    return unique_synonyms


# Function to get synonyms for each word in a list of tokens
def get_synonyms(tokens):
    tagged_tokens = pos_tag(tokens) # Get POS tags for tokens
    synonyms = list()

    for pair in tagged_tokens:
        token, tag = pair
        wnet_tag = wordnet_tag(tag) # Map POS tag to WordNet tag

        if wnet_tag is not None:
            ss = wordnet.synsets(token, pos=wnet_tag)
            us = unique_synonyms(ss)
            synonyms.append(us)

    return synonyms


# Function to get top k similar synonyms
def get_k_synonyms(synonyms, k):
    if synonyms == []:
        return synonyms

    # Calculate similarity score between each synonym and the first one
    similarity = list(sorted([
        (synonyms[i], synonyms[0].wup_similarity(synonyms[i]))
        for i in range(len(synonyms))
    ], key=lambda syn: syn[1] if syn[1] != None else 0, reverse=True))

    # Return top k synonyms
    return list(map(lambda x: x[0], similarity[:k]))


# Function to expand a query using synonyms
def query_expansion(query):
    tokens = word_tokenize(query)  # Tokenize the query
    synonyms = get_synonyms(tokens)  # Get synonyms for tokens

    expanded_tokens = []
    for i in range(len(synonyms)):
        synonyms_k = get_k_synonyms(synonyms[i], 2)  # Get top  synonyms for each token

        # If the original token is not in the synonym list, include it
        synonym_words = [synonym.lemma_names()[0].lower() for synonym in synonyms_k]
        if tokens[i] not in synonym_words:
            synonym_words.insert(0, tokens[i]) # Add original token at the beginning
            synonym_words = [stemmer.stem(token.lower()) for token in synonym_words]  # Stem the synonym words

        expanded_token = " ".join(synonym_words) # Join synonym words into a string
        expanded_tokens.append(expanded_token)

    return " ".join(expanded_tokens) # Join expanded tokens into a single string


# Main function
if __name__ == "__main__":
    print(query_expansion("bar drink ball bat elephant room fish"))
