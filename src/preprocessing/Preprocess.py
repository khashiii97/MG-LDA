from hazm import *
from PersianStemmer import PersianStemmer
"""
this file is for preprocessing (e.g. stemming and stopwords)  the sentences and words obtained from The Sentence_Extractor file
"""
ps = PersianStemmer()
def clean_sentence(documents):#recieves a set of documents and CLEANS it's sentences (removing punctuations, stemming &...)
    for document in documents:
        for i in range(len(document)): # iterating the sentences
            ### deleting ، : ! ? .  () , - ها های هایی هاش باهاش
            document[i] = [x for x in document[i] if not (x == "،" or x == "." or x == ":"
                                                          or x == "!" or x == "?"
                                                          or x == "؟" or x == "."
                                                          or x == "(" or x == ")" or x == "-"
                                                            or x == "ها" or x == "های" or x ==  "هایی"
                                                          or x == "هاش" or x == "باهاش")]
            for j in range(len(document[i])):# iterating the words
                ### replacing ي with ی
                arabic_ys = [pos for pos, char in enumerate(document[i][j]) if
                             (char == 'ي' or char == 'ى')]  # the ي causes problems in stemming
                if len(arabic_ys)>0:
                    temporary_list = list(document[i][j])
                    for pos in arabic_ys:
                        temporary_list[pos] = 'ی'
                    document[i][j]="".join(temporary_list)
                #removing nim spaces!
                if '\u200c' in document[i][j]:
                    document[i][j] = document[i][j].replace('\u200c','')
                ###replacing the word with its stem
                document[i][j] = ps.run(document[i][j])
    return documents
def get_stopwords():# obtains the files in the StopWords Directory And cumulates them all in a list:
    stop_words_list = []
    import os
    for path in os.listdir('../StopWords/'):
        full_path = os.path.join('../StopWords/', path)
        if os.path.isfile(full_path) and full_path.endswith(".txt"):
            with open(full_path, 'r', encoding='utf-8') as in_file:
                words = in_file.read().split('\n')
                for word in words:
                    stop_words_list.append(word)
    with open('slang_verbs.txt','r', encoding='utf-8') as in_file:
        words = in_file.read().split('\n')
        for word in words:
            stop_words_list.append(word)
    return stop_words_list
def reduce_sentences(documents):# removes stopwords
    stop_words_list = get_stopwords()
    for d,document in enumerate(documents):
        for i in range(len(document)): # iterating the sentences
            document[i] = [x for x in document[i] if not (x in stop_words_list or x.isnumeric())]
        documents[d] = [x for x in documents[d] if not (x == [])]
    return documents
#preprocessing
documents = []
with open('sentipers_documents.txt', 'r', encoding='utf-8') as in_file:
    strings = in_file.read().split("@@@")
    for i in range(len(strings) - 1):
        documents.append(eval(strings[i]))
documents = clean_sentence(documents)
documents = reduce_sentences(documents)
documents = [doc for doc in documents if not (doc == [])]
# print(len(documents)) #1777 documents
# number_of_sentences= 0
# number_of_words = 0
# for doc in documents:
#     number_of_sentences += len(doc)
#     for sentence in doc:
#         number_of_words += len(sentence)
# print(number_of_sentences) #19655 sentences
# print(number_of_words)#166616 useful words
# print(number_of_words/number_of_sentences) #each sentence has an average of 8.5 useful words

#write  the  output documents in a file
with open('preprocessed_documents.txt', 'w',encoding='utf-8') as f:
    for document in documents:
        f.write(str(document))
        f.write("@@@")










