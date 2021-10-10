from src.Bag_Of_Words import *
import numpy as np
import time
class MGLDA():
    def __init__(self,beta_gl,gamma,T,alpha_mix_gl,alpha_mix_loc,alpha_gl,beta_loc,alpha_loc,k_gl,k_loc):
        self.beta_gl = beta_gl
        self.gamma = gamma
        self.T = T #number of adjacent sentences in each window
        self.alpha_mix_gl = alpha_mix_gl
        self.alpha_mix_loc = alpha_mix_loc
        self.alpha_gl = alpha_gl
        self.beta_loc = beta_loc
        self.alpha_loc = alpha_loc
        self.k_gl = k_gl#number of global topics
        self.k_loc = k_loc#number of local topics
        self.bag_of_words,self.indiced_documents,self.index_of,self.list_of_words= get_bag_of_words()
        self.W = len(self.list_of_words)
        #number of times word w appeared in global topic z
        self.n_gl_z_w = np.zeros([self.k_gl,self.W],dtype= int)
        # number words assigned to global topic z
        self.n_gl_z = np.zeros(self.k_gl,dtype= int)
        # number of times word w appeared in local topic z
        self.n_loc_z_w = np.zeros([self.k_loc,self.W],dtype= int)
        # number words assigned to local topic z
        self.n_loc_z = np.zeros(self.k_loc,dtype= int)
        self.n_d_s_v = [] #number of times a word from sentence s in document d is assigned to window v
        self.n_d_s = []  # length of sentence s in document d
        #note that each sentence can be at most associated with T windows and the other windows will always have 0 n_d_s_v.
        # That said, we'll have:
        for document in self.indiced_documents:
            self.n_d_s.append([])
            self.n_d_s_v.append([])
            for sentence in document:
                self.n_d_s_v[-1].append(np.zeros(self.T,dtype = int))
                self.n_d_s[-1].append(0)
        self.n_d_v_gl = [] #number of times a word from window v from document d has be assigned to a global topic
        self.n_d_v_loc = [] #number of times a word from window v from document d has be assigned to a local topic
        # note that in a document with l sentences, we have l windows.for document with length less than T not to disturb us, we will set
        # length + T - 1 places for windows
        self.n_d_v = []  # number of times a word in document d has been assigned to window v
        for document in self.indiced_documents:
            self.n_d_v_gl.append(np.zeros(len(document) + self.T - 1,dtype=int))
            self.n_d_v_loc.append(np.zeros(len(document) + self.T - 1, dtype=int))
            self.n_d_v.append(np.zeros(len(document) + self.T - 1,dtype=int))

        self.n_d_gl_z = np.zeros([len(self.indiced_documents),self.k_gl],dtype= int)
        #number of times a word from document d was assigned to global topic z
        self.n_d_gl = np.zeros(len(self.indiced_documents),dtype= int)
        # number of times a word from document d was assigned to a global topic
        self.n_d_v_loc_z = []
        #number of times that a word from window v in document d was assigned to the local topic z
        for document in self.indiced_documents:
            self.n_d_v_loc_z.append([])
            for window in range(len(document) + self.T - 1):
                self.n_d_v_loc_z[-1].append(np.zeros(self.k_loc,dtype=int))

        # the following two counters are not explicitly used in the article but might come to hand later
        self.n_d_loc = np.zeros(len(self.indiced_documents),dtype= int) # number of times a local topic was assigned to document d
        self.n_d_loc_z = np.zeros([len(self.indiced_documents),self.k_loc],dtype= int)
        # number of times local topic z was assigned to document d
        #the final distributions we aim to obtain
        self.gl_topic_word_distribution = np.zeros([self.k_gl,self.W],dtype=float)
        self.loc_topic_word_distribution = np.zeros([self.k_gl, self.W], dtype=float)
        #initializing the topics, loc or gl and windows for each word
        self.window_of_word = []
        self.topic_of_word = []
        self.r_of_word = []
        for d,document in enumerate(self.indiced_documents):
            self.window_of_word.append([])
            self.topic_of_word.append([])
            self.r_of_word.append([])
            for s,sentence in enumerate(document):
                self.window_of_word[-1].append([])
                self.topic_of_word[-1].append([])
                self.r_of_word[-1].append([])
                for w,word in enumerate(sentence):
                    v = np.random.randint(self.T)
                    self.window_of_word[-1][-1].append(v)#choosing the window for a word
                    #note the window is indicated relatively
                    self.n_d_s_v[d][s][v] += 1
                    self.n_d_s[d][s] += 1
                    self.n_d_v[d][s + v] += 1
                    r = np.random.randint(2)
                    self.r_of_word[-1][-1].append(r)# 0 = gl 1 = loc
                    if r == 0:
                        k = np.random.randint(self.k_gl)
                        self.topic_of_word[-1][-1].append(k)
                        self.n_gl_z_w[k][word] += 1
                        self.n_gl_z[k] += 1
                        self.n_d_v_gl[d][s+v] +=  1
                        self.n_d_gl[d] += 1
                        self.n_d_gl_z[d][k] += 1
                    else:
                        k = np.random.randint(self.k_loc)
                        self.topic_of_word[-1][-1].append(k)
                        self.n_loc_z_w[k][word] += 1
                        self.n_loc_z[k] += 1
                        self.n_d_v_loc[d][s+v] += 1
                        self.n_d_v_loc_z[d][s+v][k] += 1
                        self.n_d_loc[d] += 1
                        self.n_d_loc_z[d][k] += 1
    def inference(self):
        counter = 1
        for d,document in enumerate(self.indiced_documents):
            for s,sentence in enumerate(document):
                for w,word in enumerate(sentence):
                    counter += 1
                    if counter % 50000 == 0:
                        print(str(int(counter/50000)) + "/4 done")

                    v = self.window_of_word[d][s][w]
                    r = self.r_of_word[d][s][w]
                    z = self.topic_of_word[d][s][w]
                    if r == 0:
                        self.n_gl_z_w[z][word] -= 1
                        self.n_gl_z[z] -= 1
                        self.n_d_v_gl[d][s+v] -= 1
                        self.n_d_gl_z[d][z] -= 1
                        self.n_d_gl[d] -= 1
                    elif r==1:
                        self.n_loc_z_w[z][word] -= 1
                        self.n_loc_z[z] -= 1
                        self.n_d_v_loc[d][s+v] -= 1
                        self.n_d_v_loc_z[d][s+v][z] -= 1
                        self.n_d_loc[d] -= 1
                        self.n_d_loc_z[d][z] -= 1
                    else:
                        print("error in choosing r: ",r" should be less than 2")
                    self.n_d_s_v[d][s][v] -= 1
                    self.n_d_s[d][s] -= 1
                    self.n_d_v[d][s + v] -= 1
                    #calulating the multinomial distribution to choose w's new topic
                    conditional_probability = []# p(v,r,z|V,R,Z,W)
                    new_label = []
                    for window in range(self.T):
                        # computing the distribution of topics. we will choose a topic from this distrubation in the next stage
                        for topic in range(self.k_gl):
                            term1 = float(self.n_gl_z_w[topic][word] + self.beta_gl) / (
                                        self.n_gl_z[topic] + self.W * self.beta_gl)
                            term2 = float(self.n_d_s_v[d][s][window] + self.gamma) / (
                                        self.n_d_s[d][s] + self.T * self.gamma)
                            term3 = float(self.n_d_v_gl[d][s-window] + self.alpha_mix_gl)/(self.n_d_v[d][s - window] + self.alpha_mix_gl + self.alpha_mix_loc)
                            term4 = float(self.n_d_gl_z[d][topic] + self.alpha_gl) / (self.n_d_gl[d] + self.k_gl * self.alpha_gl)
                            conditional_probability.append(term1 * term2 * term3 * term4)
                            new_label.append([window,0,topic])
                        # for global topics
                        for topic in range(self.k_loc):
                            term1 = float(self.n_loc_z_w[topic][word] + self.beta_loc) / (
                                        self.n_loc_z[topic] + self.W * self.beta_loc)
                            term2 = float(self.n_d_s_v[d][s][window] + self.gamma) / (
                                        self.n_d_s[d][s] + self.T * self.gamma)
                            term3 = float(self.n_d_v_loc[d][s-window] + self.alpha_mix_loc)/(self.n_d_v[d][s - window] + self.alpha_mix_gl + self.alpha_mix_loc)
                            term4 = float(self.n_d_v_loc_z[d][s-window][topic] + self.alpha_loc) / (self.n_d_v_loc[d][s - window] + self.k_gl * self.alpha_gl)
                            conditional_probability.append(term1 * term2 * term3 * term4)
                            new_label.append([window, 1, topic])
                    #choosing a topic for word based on the new distribution
                    for i in range(len(conditional_probability)):
                        conditional_probability[i] = abs(conditional_probability[i] - np.finfo(np.float32).epsneg)
                    temp_array = np.array(conditional_probability)
                    index_of_chosen_label = np.random.multinomial(1,temp_array/temp_array.sum()).argmax()#Draws a sample from the multinomial distribution we computed above
                    chosen_window,chosen_r,chosen_topic = new_label[index_of_chosen_label]
                    #changing the counters based on the new r , window & topic
                    if chosen_r == 0:#gl
                        self.n_gl_z_w[chosen_topic][word] += 1
                        self.n_gl_z[chosen_topic] += 1
                        self.n_d_s_v[d][s][chosen_window] += 1
                        self.n_d_s[d][s] += 1
                        self.n_d_v_gl[d][s + chosen_window] += 1
                        self.n_d_v[d][s + chosen_window] += 1
                        self.n_d_gl_z[d][chosen_topic] += 1
                        self.n_d_gl[d] += 1

                    elif chosen_r == 1:#loc
                        self.n_loc_z_w[chosen_topic][word] += 1
                        self.n_loc_z[chosen_topic] += 1
                        self.n_d_s_v[d][s][chosen_window] += 1
                        self.n_d_s[d][s] += 1
                        self.n_d_v_loc[d][s+chosen_window] += 1
                        self.n_d_v[d][s - chosen_window] += 1
                        self.n_d_v_loc_z[d][s + chosen_window][chosen_topic] += 1
                        self.n_d_loc[d] += 1
                        self.n_d_loc_z[d][chosen_topic] += 1
                    else:
                        print("error in iteration. r was supposed to be less than 2 but is ",chosen_r)
                    self.window_of_word[d][s][w] = chosen_window
                    self.r_of_word[d][s][w] = chosen_r
                    self.topic_of_word[d][s][w] = chosen_topic
    def compute_distributions(self): #will be called after the iterations are done

        temp_gl = self.n_gl_z_w + self.beta_gl
        temp = []
        for topic in range(self.k_gl):
            #sum = np.sum(temp_gl[topic, :])
            #for j in range(len(self.gl_topic_word_distribution[topic])):
                # if temp_gl[topic][j] != 0:
                #     print(temp_gl[topic][j])
                #     print(temp_gl[topic][j] / sum)
                #     print(float(temp_gl[topic][j] / sum))
                #     print("++++++++++")
                # self.gl_topic_word_distribution[topic][j] = float(temp_gl[topic][j] / sum)
                # print(self.gl_topic_word_distribution[topic][j])
                # print("***********")
            self.gl_topic_word_distribution[topic, :] = (temp_gl[topic, :] )/np.sum(temp_gl[topic, :])
            # temp.append([x for x in self.gl_topic_word_distribution[topic, :] if x != 0])
            # print(np.sum(temp_gl[topic, :]))
            # print(temp)


        temp_loc = self.n_loc_z_w + self.beta_loc
        for topic in range(self.k_loc):
            self.loc_topic_word_distribution[topic, :] = temp_loc[topic, :] * 1 / np.sum(temp_loc[topic, :])
    def learning_process(self,number_of_iterations):
        for i in range(number_of_iterations):
            print("********************************************")
            print("inference number " + str(i) + " started ")
            t_start = time.time()
            self.inference()
            duration = time.time() - t_start
            print("inference number " + str(i) + " done in " + str(int(duration/60)) + " minutes")
        self.compute_distributions()
k_gl = 10
k_loc = 7
mg_lda = MGLDA(beta_gl = 0.1,gamma = 0.1,T = 3,alpha_mix_gl = 0.1
               ,alpha_mix_loc = 0.1,alpha_gl = 0.1,beta_loc = 0.1,alpha_loc = 0.1,k_gl = k_gl,k_loc = k_loc)

mg_lda.learning_process(number_of_iterations= 60)
with open('../results/a1.txt', 'w',encoding='utf-8') as f:
    for row in mg_lda.gl_topic_word_distribution:
        f.write(str(row) + '\n')
with open('../results/a2.txt', 'w',encoding='utf-8') as f:
    for row in mg_lda.loc_topic_word_distribution:
        f.write(str(row) + '\n')
top_eight_of_globals =[[] for i in range(k_gl)] # top 8 words for every global aspect
for i in range(k_gl):
    top_eight_indexes_gl = np.array(mg_lda.gl_topic_word_distribution[i]).argsort()[-8:][::-1]
    for j in range(8):
        top_eight_of_globals[i].append(mg_lda.list_of_words[top_eight_indexes_gl[j]])
top_eight_of_locals =[[] for i in range(k_loc)]# top 8 words for every local aspect
for i in range(k_loc):
    top_eight_indexes_loc = np.array(mg_lda.gl_topic_word_distribution[i]).argsort()[-8:][::-1]
    for j in range(8):
        top_eight_of_locals[i].append(mg_lda.list_of_words[top_eight_indexes_loc[j]])
with open('../results/aspectsobtained.txt', 'w',encoding='utf-8') as f:
    f.write("Global topics :\n")
    for i in range(k_gl):
        f.write("*********************\n")
        f.write("Global topic " + str(i + 1) +":\n")
        f.write(str(top_eight_of_globals[i]))
        f.write("\n")
    f.write("\n*************************************************\n")
    f.write("Local topics (aspects) :\n")
    for i in range(k_loc):
        f.write("*********************\n")
        f.write("Local topic " + str(i + 1) + ":\n")
        f.write(str(top_eight_of_locals[i]))
        f.write("\n")



