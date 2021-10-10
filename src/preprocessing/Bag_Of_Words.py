"""
In this file, we'll create a 2d matrix named bag_of_words, indicating the number of times a word has been used in a document.
In order to do that, first we'll create a set comprising all distinct words in the documents
"""
import numpy as np
def get_bag_of_words():
    set_of_words = set()  # all distinct words in the documents
    documents = []
    with open('preprocessed_documents.txt', 'r', encoding='utf-8') as in_file:
        strings = in_file.read().split("@@@")
        for i in range(len(strings) - 1):
            documents.append(eval(strings[i]))
    for document in documents:
        for sentence in document:
            for word in sentence:
                set_of_words.add(word)
    set_of_words = sorted(set_of_words)
    list_of_words = list(set_of_words)
    index_of = dict(
        [(word, index) for index, word in enumerate(list_of_words)])  # a mapping between each word and it's index
    # creating 2d matrix named bag_of_words, indicating the number of times a word has been used in a document.
    bag_of_words = np.zeros([len(documents), len(set_of_words)], dtype=int)
    for i in range(len(documents)):
        for sentence in documents[i]:
            for word in sentence:
                bag_of_words[i][index_of[word]] += 1
    # saving each document as sentences only this time sentences comprise of indexes instead of words
    indiced_documents = []
    for document in documents:
        indiced_documents.append([])
        for i in range(len(document)):
            indiced_documents[-1].append([])
            for j in range(len(document[i])):
                indiced_documents[-1][i].append(index_of[document[i][j]])
    return bag_of_words,indiced_documents,index_of,list_of_words






