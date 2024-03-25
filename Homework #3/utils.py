import os
import pickle

#class to handle the loading of the posting and dictionary files
class LoadingUtil:
    def __init__(self, output_dictionary_path, output_postings_path):
        self.output_postings_path = output_postings_path
        self.output_dictionary_path = output_dictionary_path

        self.file_ids: list[str] = list()
        self.dictionary: dict[str, int] = {}
        self.document_frequency : dict[str, int] = {}
        self.document_length : dict[str, int] = {}

        self.__post_init__()

    #ensure the path provided is correct
    def __post_init__(self):
        if not os.path.exists(self.output_postings_path):
            raise RuntimeError("ERROR: output postings path doesnt exist")

        if not os.path.exists(self.output_dictionary_path):
            raise RuntimeError("ERROR: output dictionary path doesnt exist")

    #load the postings list for the token
    def load_postings_list(self, token):
        assert len(self.dictionary) > 0
        postings_list = str()
        with open(self.output_postings_path, "rb") as postings_file:
            if token not in self.dictionary:
                return postings_list
            postings_file.seek(self.dictionary[token])
            postings_list = pickle.load(postings_file)

        return postings_list

    #load the dictionary
    def load_dictionary(self):
        with open(self.output_dictionary_path, "rb") as dictionary_file:
            self.file_ids = pickle.load(dictionary_file)
            self.dictionary = pickle.load(dictionary_file)
            all_file_postings_list = pickle.load(dictionary_file)
            self.document_frequency = pickle.load(dictionary_file)
            self.document_length = pickle.load(dictionary_file)

        return self.file_ids, self.dictionary, all_file_postings_list, self.document_length, self.document_frequency
