# -*- coding: utf-8 -*-
"""
Created on Thu 4/20 20:58:51 2019

@author: samyu
"""
import glob, os, nltk, pandas,string, json, math, time
from string import digits
from nltk.stem.porter import PorterStemmer
from pyspark import SparkContext, SparkConf

def word_count_all_files():
    conf = SparkConf().setAppName("Pyspark Pgm1")
    sc = SparkContext.getOrCreate(conf = conf)
    files_list = glob.glob('input\*')
    for counter,file in enumerate(files_list):
        rdd = sc.textFile(file)
        counts = rdd.flatMap(lambda line: line.split(" ")).map(lambda word: ((clean(word),file), 1)).reduceByKey(lambda a, b: a + b)
        counts.coalesce(1).saveAsTextFile(f"counts{counter}.csv")


def clean(word):
    word = word.lower()
    s = word
    word = ''.join([i for i in s if not i.isdigit()])
    word = word.translate(str.maketrans('','',string.punctuation))
    word = word.replace("'","").replace('"', '')
    word = word.replace("\u2019","").replace('\u2018', '')
    word = word.replace("\u201c","").replace('\u201d', '')
    word = porter.stem(word)

    return word


# Setup
porter = PorterStemmer()
remove_digits = str.maketrans('', '', digits)
# Clean word
g_found_docs =[]
def build_index():
    # For the sake not breaking the unknwown testing enviroment
    # We will read file names as input\\doc1.txt instead of using
    # os.chdir to take off input\, instead we will cleanup using simple slicing
    out_files_list = glob.glob('counts*.csv\part-00000')
    # hopefully none of the words have the name super_unique_total_files, if this is a problem replace with RNG names lol
    my_dict= {"super_unique_total_files":len(out_files_list)}
    remove_digits = str.maketrans('', '', digits)
    ################################### NEEEEEED TO BE ABLE TO READ MULTIPLE LINES ALSO CLEAN OUT APOSRIPHES######################
    # Loop over our files clean them and save all words to a list
    for i,file in enumerate(out_files_list):
        with open(file, 'r') as outputfile:
            lines = outputfile.readlines()
        for line in lines:
            tuple0 =  eval(line)
            #print("Tuple: " + str(tuple0))
            keyword = tuple0[0][0]
            #print("Keyword: " + str(keyword))
            filename = tuple0[0][1]
            filename = filename[6:]

            #print("Filename: " + str(filename))
            #filename = line[0][1]
            #print(line)
            #key_tuple, file_value = line
            #keyword, filename = key_tuple

            file_value = tuple0[1]
           # print("Filevalue: " + str(file_value))

            file_dict = {filename:file_value}

            if keyword not in my_dict:
                my_dict[keyword] = file_dict
            else:
                current_dict = my_dict[keyword]
                current_dict[filename] = file_value
                my_dict[keyword] = current_dict



    json_object = json.dumps(my_dict)
    json_file = open("inverted-index.json","w")
    json_file.write(json_object)
    json_file.close()
    # I should prolly refactor this... its kinda hacky
def clean_words(query_list):
    for i,query in enumerate(query_list):

        query = query.lower()
        query = query.translate(str.maketrans('','',string.punctuation))
        query = query.translate(remove_digits)
        concatenated_query = ""
        my_keyword_list = query.split()
        for j,my_keyword in enumerate(my_keyword_list):
            my_keyword = porter.stem(my_keyword)

            concatenated_query= concatenated_query+my_keyword+ " "
        concatenated_query = concatenated_query.rstrip()
        query_list[i] = concatenated_query
    return query_list

class Weighted:
    def __init__(self, document, given_count):
        self.document = document
        self.partial_weight_dict ={}
        self.total_weight = None
        self.count_words = given_count
    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self.document == other.document

    def add_partial(self,keyword,partial_weight):
        self.partial_weight_dict[keyword] = partial_weight
        return None
    def sum_weights(self):
        sums = sum(self.partial_weight_dict.values())
        self.total_weight = sums
        return None
# Query is going to be a string
def num_words_in_query(query):
    # This is kinda hacky haha I hope you can understand it
    query_count = len(query.split())
    return query_count
def get_words_list(query):
    words_list = query.split()
    return words_list

# returns first index of first instance of weighted object

def check_if_weight_already_in_list(found_weighted_object,weighted_list):
    for i,weighted_object in enumerate(weighted_list):
        if found_weighted_object.document == weighted_object.document:
            return i
    return -2

# Open Up the index
json_file = open("inverted-index.json","r")
json_file = json.load(json_file) # This returns a dictionary object


# Iterate each key(aka each line in the key-word file)
def main(key_word_list):
    all_keywords = key_word_list
    key_word_list = key_word_list.split()
    key_word_list = clean_words(key_word_list)
# Iterate each key(aka each line in the key-word file)
    for key in key_word_list:
        weight_list = [] # Create a list of Weighted objects that store the document name, total weight and composite weights
        # Iterate of the number of words in a key(single line of text)
        for i in range(0,num_words_in_query(key)):

            # Split those words up from their single line
            words = get_words_list(key)
            # Search the dictionary(json_file) for a single keyword
            found = json_file.get(words[i],'false')
            # If that keyword is not found continue on to the single space delimted keyword in our string(single line of text)
            if found == 'false':
                continue
            # Else calculate the weight of that single keyword from our inverted index by using our stored values
            else:
                document_list = found.keys() # A list of the documents that contain our single keyword
                # Iterate over that list of documents
                for document in document_list:
                    # fetch the number of appearences of our single keyword that the document stores in its dictionary
                    num_appear = found[document]
                    # Calculate the weight of that single keyword
                    # (1 + log2 freq(key,doc)) * log2 (N / n(doc))

                    partial_weight =  0
                    # Create a Weighted object that will store the document name and a list of partial weights of each single keyword in our string(line of text)
                    found_document = Weighted(document,num_appear)
                    # add a count thingy
                    # See if our newley created document is already in the weighted list
                    # This is a case for a query that has multiple words and multiple words are present in the same document
                    index_found_doc = check_if_weight_already_in_list(found_document,weight_list)
                    # if the index found is 0 or greater that means the document is already in our list
                    if index_found_doc >=0:
                    # Update the already weighted document with a new keyword and a new partial weight
                        weight_list[index_found_doc].add_partial(words[i],partial_weight)
                    # Otherwise add a new weighted document to the weighted list
                    else:
                        found_document.add_partial(words[i],partial_weight)
                        weight_list.append(found_document)

        # Sum up all the weights for our query(single line of text)
        for weight in weight_list:
            weight.sum_weights()

        if not weight_list:
            print("Keyword "+key+" is NOT in the index!!!\n")
        else:
            print("\nstemmed keyword = " + key+"\n")

            words2 = get_words_list(key)
            weight_list.sort(key=lambda x: x.count_words, reverse=True)
            for i,thing in enumerate(weight_list):
                print("===Next file===")
                print("file="+thing.document, end = ": ")
                g_found_docs.append(thing.document)
                print("count="+str(thing.count_words))
                #print("file="+thing.document, end = ": ")
                #rounded_total_weight = round(thing.total_weight,6)
                #print("total score="+str(rounded_total_weight))
                #for key,value in thing.partial_weight_dict.items():
                #   rounded_value = round(value,6)
                #   print ("weight("+str(key)+")"+"="+str(rounded_value))
                time.sleep(1)

                print_context(thing.document,key,key_word_list)
                time.sleep(1)


def print_context(doc,word_context,list_keyword):
    count = 0
    doc = f"input\{doc}"
    fp = open(doc,"r",encoding = "utf_8")
    for line in fp:
        word_list = line.split()
        #print("Context for up to first 10 hits:")
        for j,word in enumerate(word_list):
            word = word.lower()
            s = word
            word = ''.join([i for i in s if not i.isdigit()])
            if word =="":
                continue
            word = word.translate(str.maketrans('','',string.punctuation))
            word = word.replace("'","").replace('"', '')
            word = word.replace("\u2019","").replace('\u2018', '')
            word = word.replace("\u201c","").replace('\u201d', '')
            word = porter.stem(word)

            if word == word_context:
                print("Line that the word appears in:")
                print(line)
                count+=1
        if count == 10:
            break



if __name__ =="__main__":
    print("Welcome to the tiny-google engine!")
    choice = input("Build inverted-index?(y/n):")
    if choice == "y":
        print("Building...")
        word_count_all_files()
        build_index()
        print("Built!\n")
    elif(choice =="n"):
        print("Using existing current index then!")
    else:
        print("Incorrect input detected exiting program.")
        exit()
    while(True):
        print("To exit, type 'exit-1'")
        my_keyword = input("Please enter the keyword or keywords you are looking for: ")
        if my_keyword == "exit-1":
            exit(1)
        else:
            main(my_keyword)

        
