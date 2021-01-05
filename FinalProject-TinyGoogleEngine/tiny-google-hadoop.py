# -*- coding: utf-8 -*-
"""
Created on Thu 4/20 20:58:51 2019

@author: samyu
"""
import glob, os, nltk, pandas,string, json, math, time
from string import digits
from itertools import groupby
from operator import itemgetter
import sys


from nltk.stem.porter import PorterStemmer
#from pyspark import SparkContext, SparkConf



# Setup
porter = PorterStemmer()
remove_digits = str.maketrans('', '', digits)
# Clean word
g_found_docs =[]
def read_input(file):
    for line in file:
        # split the line into words
        yield line.split()
def read_mapper_output(file, separator=" "):
    for line in file:
        yield line.rstrip().split(separator, 1)


def mapped(separator=" "):
    # input comes from STDIN (standard input)
    data = read_input(sys.stdin)
    for words in data:
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py
        #
        # tab-delimited; the trivial word count is 1
        for word in words:
            print(f"{word} {separator} 1")

def reduced(separator=" "):
    # input comes from STDIN (standard input)
    data = read_mapper_output(sys.stdin, separator=separator)
    # groupby groups multiple word-count pairs by word,
    # and creates an iterator that returns consecutive keys and their group:
    #   current_word - string containing a word (the key)
    #   group - iterator yielding all ["&lt;current_word&gt;", "&lt;count&gt;"] items
    for current_word, group in groupby(data, itemgetter(0)):
        try:
            total_count = sum(int(count) for current_word, count in group)
            print(f"{current_word} {separator} {total_count}")
        except ValueError:
            # count was not a number, so silently discard this item
            pass


def build_index():
    # For the sake not breaking the unknwown testing enviroment
    # We will read file names as input\\doc1.txt instead of using
    # os.chdir to take off input\, instead we will cleanup using simple slicing
    files_list = glob.glob('input\*')
    # hopefully none of the words have the name super_unique_total_files, if this is a problem replace with RNG names lol
    my_dict= {"super_unique_total_files":len(files_list)}
    porter = PorterStemmer()
    remove_digits = str.maketrans('', '', digits)
    ################################### NEEEEEED TO BE ABLE TO READ MULTIPLE LINES ALSO CLEAN OUT APOSRIPHES######################
    # Loop over our files clean them and save all words to a list
    for i,file in enumerate(files_list):
        fp = open(file,"r",encoding = "utf_8")

        # NEED TO READ LINE BY LINE
        for line in fp:
            word_list = line.split()
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
        #####################GOOOD###################        
                found = my_dict.get(word,"false")
                # Checks if WORD is in the index
                clean_file_name = file[6:]

                if found == "false":
                    # Remove the /input
                    # Storage of inverted index example #dictionary->[[doc1,2],[doc2,3],[doc3,4]] conceptual
                    # For speed purposes double dictionary muahahahahahahhahahahha
                    # #dictionary = word={
                    # doc1:2,
                    # doc2:3,
                    # doc3:4
                    # }
                    my_dict.update({word:{clean_file_name:1}})
                # Checks if this WORD found in this FILE has the FILE NAME listed in the WORD's dictionary
                else:
                    document_in_index = my_dict[word].get(clean_file_name,"false")
                    # Did NOT find the document name listed, add it
                    # For some reason this is not working correctly the second time through
                    if document_in_index == "false":
                        my_dict[word].update({clean_file_name:1})
                    # FOUND the document name increment by 1
                    else:
                        increment = my_dict[word][clean_file_name]
                        increment+=1
                        my_dict[word].update({clean_file_name:increment})
        fp.close()
    #print(my_dict)                  

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
                    
                    partial_weight =  (1+(math.log(num_appear,2))) * math.log((json_file['super_unique_total_files']/len(document_list)),2)
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
            print("\nkeywords = " + key+"\n")

            words2 = get_words_list(key)
            weight_list.sort(key=lambda x: x.count_words, reverse=True)
            for i,thing in enumerate(weight_list):
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
                print("Context for up to first 10 hits:")
                print(line)
                count+=1
        if count == 10:
            break



if __name__ =="__main__":
    #word_count()
    print("Welcome to the tiny-google engine!")
    choice = input("Build inverted-index?(y/n):")
    if choice == "y":
        print("Building...")
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
            
        