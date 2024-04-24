from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

stemmer = nltk.stem.PorterStemmer()


def wordnet_tag(tag):
  if tag[0] == 'N':
        return wordnet.NOUN
  elif tag[0] == 'J':
        return wordnet.ADJ
  elif tag[0]== 'V':
        return wordnet.VERB
  elif tag[0] == 'R':
        return wordnet.ADV
  
  return None

def get_synonyms(tokens):
  tagged_tokens = pos_tag(tokens)
  # print(tagged_tokens)
  synonyms = list()

  for pair in tagged_tokens:
    token, tag = pair
    wnet_tag = wordnet_tag(tag)
    # print(wnet_tag)
    if wnet_tag is not None:
        # print(token)
        synonyms.append(unique_synonyms(wordnet.synsets(token, pos=wnet_tag)))
    
    # print(synonyms)

  return synonyms


def unique_synonyms(synonyms):
    words = []
    unique_synonyms = []

    for synonym in synonyms:
        # print(synonym)
        word_name = synonym.lemma_names()[0]
        if word_name not in words:
            words.append(word_name)
            unique_synonyms.append(synonym)
            # print(synonyms)
        
    return unique_synonyms

def get_k_synonyms(synonyms, k):
    if synonyms == []:
        return synonyms
    
    similarity = [(synonyms[i], synonyms[0].wup_similarity(synonyms[i])) for i in range(len(synonyms))]
    
    # print(similarity)
    sorted(similarity, key=lambda syn: syn[1] if syn[1] != None else 0, reverse=True)
    
    # Return top k synonyms
    return list(map(lambda x: x[0], similarity[:k]))

def query_expansion(query):
    tokens = word_tokenize(query)
    # print(tokens)
    synonyms = get_synonyms(tokens)   
    # print(synonyms)
    # print(query)
    expanded_tokens = []
    for i in range (len(synonyms)):
        synonyms_k = get_k_synonyms(synonyms[i], 2)
        # print(synonyms_k)

        synonym_words = [synonym.lemma_names()[0].lower() for synonym in synonyms_k]
        if (tokens[i] not in synonym_words):
            synonym_words.insert(0, tokens[i]) 
            print(synonym_words)
            synonym_words = [stemmer.stem(token.lower()) for token in synonym_words]
            print(synonym_words)

        expanded_token = ' '.join(synonym_words)
        expanded_tokens.append(expanded_token)
    print('-------')
    # print(' '.join(expanded_tokens))
    
    return ' '.join(expanded_tokens)



if __name__ == '__main__':
    print(query_expansion("bar drink ball bat elephant room"))
    
