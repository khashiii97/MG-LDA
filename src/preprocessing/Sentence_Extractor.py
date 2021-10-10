import os
import sys
import csv
import re
from hazm import *
# adding classes folder to system path
# sys.path.insert(0, os.path.abspath('..') + '/src')

from src import sentipers
"""
As stated in the research paper, "We represent a document as a set of sliding windows, each covering T adjacent sentences within
a document". One of the factors that may lead to poor results is the low number of sentences used in a document.
For this purpose, in this implementation we consider the following set of sentences as a document:
1.every 10 sentences in the Review body part (with the tag rev in the xml file) will be collectively considered as a document.
2.Each  "General" or "Critical" review comprises of a number of sentences. Those set of sentences will be considered as a document.
3.The files in the extra folder weren't  structured as xml files, so like the first case all of their sentences will be considered as one document.
so the list "documents" will encompass lists(each embodying a document)  that contain a set of sentences integrated out of the same
review files.
"""
def correct_measures(sentence): #it was viewed that measures like سانتی متر were counted as two words. two correct that i wrote this function
    if 'سانتی ' in sentence:
        sentence = sentence.replace('سانتی ', 'سانتی')

    if 'میلی ' in sentence:
        sentence = sentence.replace('سانتی ', 'میلی')

    if 'کیلو ' in sentence:
        sentence = sentence.replace('سانتی ', 'کیلو')

    if 'مگا ' in sentence:
        sentence = sentence.replace('سانتی ', 'مگا')
    return sentence


documents = []
# the set of sentences will be stored in this list
# we will make use of this data in the preprocessing section
sentences_of_a_document = []
#reading all sentences in a product review and putting them into an array named sentences_of_a_document.



# ****************************************
""""
1: the data in the main folder of sentipers:
the data in this part was well structured in xml format, so the sentipers build in functions
were enough for fetching the data
"""

senti = sentipers.SentiPers()
df = senti.read_sentences_main()
file_of_current_review = ''
rev = 0 # counter of rev tags. it will be set back to 0 every 10 revs
gr = 0 # number of the current gr
cr = 0 # number of the current gr
for index, row in df.iterrows():
    if file_of_current_review != row.file :# new file is being analyzed
        file_of_current_review = row.file
        documents.append(sentences_of_a_document)
        sentences_of_a_document = []
        rev = 0
        gr = 0
        cr = 0
    if row.sid.startswith("rev"):
        if(rev < 10):
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))  # the 0:-1 part is for omitting the extra space at the end of each array
            rev += 1
        else:
            rev = 1
            documents.append(sentences_of_a_document)
            sentences_of_a_document = []
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))
                                            # the 0:-1 part is for omitting the extra space at the end of each array
    elif row.sid.startswith("gr"):
        rev = 0
        splited = row.sid.split("-") #splited[1] will be the gr number
        if gr == int(splited[1]):# this sentence belongs to the current gr
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))  # the 0:-1 part is for omitting the extra space at the end of each array
        else:
            gr = int(splited[1])
            documents.append(sentences_of_a_document)
            sentences_of_a_document = []
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))
    elif row.sid.startswith("cr"):
        gr = 0
        splited = row.sid.split("-") #splited[1] will be the gr number
        if cr == int(splited[1]):
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))  # the 0:-1 part is for omitting the extra space at the end of each array
        else:
            cr = int(splited[1])
            documents.append(sentences_of_a_document)
            sentences_of_a_document = []
            sentences_of_a_document.append(word_tokenize(correct_measures(row.text)))



# ****************************************
"""
2: the data in the extra sentipers:
unfortunately,the data in this part had just the xml extension nominally, and the
content of the files were'nt structured in xml format. so we had to convert them to txt and read each line
manually and finally add them to our documents.
"""

# changing each file in extra_edited to txt and then eliciting the sentences from it.
# this part is only needed to be run once and can be commented after that
sentences_of_a_document = []
extra_path = "../data/extra_edited/"
for path in os.listdir(extra_path):
    full_path = os.path.join(extra_path, path)
    if os.path.isfile(full_path) and full_path.endswith(".xml"):
        pre, ext = os.path.splitext(full_path)
        os.rename(full_path, pre + ".txt")
for path in os.listdir(extra_path):
    full_path = os.path.join(extra_path, path)
    if os.path.isfile(full_path) and full_path.endswith(".txt"):
        with open(full_path,encoding="utf8") as file:
            temp_sentence = []
            for line in file:
                splited_sentence = re.split("[\t\n\.،():?!]+", line)[0:-1]
                if len(splited_sentence) == 1:
                    if splited_sentence[0] == "[@@@]":
                        if len(temp_sentence) > 1 and temp_sentence[0] !=   'تاکنون' and temp_sentence[1] != 'نقدی':
                            sentences_of_a_document.append(temp_sentence)
                        temp_sentence = []
                else:
                    temp_sentence.append(splited_sentence[1])
    if sentences_of_a_document != []:
        documents.append(sentences_of_a_document)
    sentences_of_a_document = []
# print(len(documents)) # number of documents == 1811
# sum_document = 0
# for document in documents:
#     sum_document += len(document)
# print(sum_document/len(documents)) #each document has an average of 11.01 sentences


# #************************
#write  the  output documents in a file

with open('sentipers_documents.txt', 'w',encoding='utf-8') as f:
    for document in documents:
        f.write(str(document))
        f.write("@@@")








