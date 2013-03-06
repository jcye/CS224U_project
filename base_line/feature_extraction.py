
"""
basic_sentiment_analysis
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the code and examples described in 
http://fjavieralba.com/basic-sentiment-analysis-with-python.html

"""

from pprint import pprint
import nltk
import yaml
import sys
import os
import re
from pprint import pprint

class Splitter(object):

    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):

    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

class DictionaryTagger(object):

    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        print sentence[0][0]
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                #print "expression_form:",expression_form
                #print "expression_lemma:",expression_lemma
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        #print tag_sentence
        return tag_sentence

class FeatureGenerator(object):

    def __init__(self, word_score_file):
        self.dictionary = {}
        self.index = {}
        self.size = 0
        input_file = open(word_score_file, "rb" )

        i = 0
        lines = input_file.readlines()
        for line in lines:
            tmp = line.split()
            word = tmp[0]
            if word not in self.dictionary:
                self.dictionary[word] = 0
                self.index[i] = word
                i += 1
        self.size = i 

    def feature_generator(self, postagged_sentences):
        return [self.feature_for_sentence(sentence) for sentence in postagged_sentences]

    def feature_for_sentence(self, sentence):
        for i in range(len(sentence)):
            key = sentence[i][1]
            if key in self.dictionary.keys():
                self.dictionary[key] += 1
        return 

    def write_to_file(self, output_file, positive):
        out = open(output_file, 'a')
        i = 0
        if (positive):
            out.write("1 ")
        else:
            out.write("0 ")
        while i<self.size:
            key = str(self.index[i])
            value = self.dictionary[key]
            out.write(str(value) + " ")
            i += 1
        out.write("\n")
        out.close()

def value_of(sentiment):
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0

def sentence_score(sentence_tokens, previous_token, acum_score):    
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
            elif 'dec' in previous_tags:
                token_score /= 2.0
            elif 'inv' in previous_tags:
                token_score *= -1.0
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])

def calculate_sentiment(text):
    splitter = Splitter()
    postagger = POSTagger()
    dicttagger = DictionaryTagger([ 'dicts/positive.yml', 'dicts/negative.yml', 
                                    'dicts/inc.yml', 'dicts/dec.yml', 'dicts/inv.yml'])

    splitted_sentences = splitter.split(text)
    pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
    dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)
    score = sentiment_score(dict_tagged_sentences)
    return score

def generate_feature(text, output_file, positive):
    splitter = Splitter()
    postagger = POSTagger()
    generator = FeatureGenerator('dicts/word_score.yml')

    splitted_sentences = splitter.split(text)
    pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
    generator.feature_generator(pos_tagged_sentences)
    generator.write_to_file(output_file, positive)

def batch_generate (pos_dir, neg_dir, feature_file):
    pos_file_list = os.listdir(pos_dir)
    neg_file_list = os.listdir(neg_dir)
    feature_out = open(feature_file, 'wb')
    
    for i in range(len(pos_file_list)):
        cur_file = open(pos_dir + "/" + pos_file_list[i], 'rb')
        cur_text = cur_file.read()
        generate_feature(cur_text, feature_file, True)
        cur_file.close()

    for i in range(len(neg_file_list)):
        cur_file = open(neg_dir + "/" + neg_file_list[i], 'rb')
        cur_text = cur_file.read()
        generate_feature(cur_text, feature_file, False)
        cur_file.close()

    feature_out.close()

def batch_process (pos_dir, neg_dir, pos_output, neg_output):
    pos_file_list = os.listdir(pos_dir)
    neg_file_list = os.listdir(neg_dir)
    pos_out = open(pos_output, 'wb')
    neg_out = open(neg_output, 'wb')
    
    for i in range(len(pos_file_list)):
        cur_file = open(pos_dir + "/" + pos_file_list[i], 'rb')
        cur_text = cur_file.read()
        cur_score = calculate_sentiment(cur_text)
        pos_out.write(pos_file_list[i] + " " + str(cur_score) + "\n")
        cur_file.close()
    pos_out.close()

    for i in range(len(neg_file_list)):
        cur_file = open(neg_dir + "/" + neg_file_list[i], 'rb')
        cur_text = cur_file.read()
        cur_score = calculate_sentiment(cur_text)
        neg_out.write(neg_file_list[i] + " " + str(cur_score) + "\n")
        cur_file.close()
    neg_out.close()

def single_process (file):
    cur_file = open(file, 'rb')
    cur_text = cur_file.read()
    #calculate_sentiment(cur_text)
    #generate_feature(cur_text)

if __name__ == "__main__":
    pos_dir1 = "data/pos1"
    neg_dir1 = "data/neg1"
    pos_dir2 = "data/pos2"
    neg_dir2 = "data/neg2"
    #pos_output = "pos_out.txt"
    #neg_output = "neg_out.txt"
    feature_file1 = "feature/feature_train.txt"
    feature_file2 = "feature/feature_test.txt"
    batch_generate (pos_dir1, neg_dir1, feature_file1)
    batch_generate (pos_dir2, neg_dir2, feature_file2)
    #debug_file = "data/neg/cv000_29416.txt"
    #batch_process(pos_dir, neg_dir, pos_output, neg_output)
    #single_process(debug_file)


