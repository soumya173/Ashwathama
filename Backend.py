import re
import random
import sqlite3
from collections import Counter
from string import punctuation
from math import sqrt
import logging
LOG_FILENAME = './Ashwathama_Logs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


# Example log "logging.error("Anything you need to print")
# from nltk.corpus import words as nltk_words
# from nltk.corpus import wordnet

#####################################################
# Installation Notes for nltk.corpus.words
#
# Step 1 : First install nltk
#   - pip install nltk
# Step 2 : Enter into python shell
#   - python
# Step 3 : inside python shell download english words from nktl library (this step requires internet connection)
#   - nltk.download('words')
#

class Backend(object):
    def __init__(self):
        """initialize the connection to the database"""
        self.connection = sqlite3.connect('chatbot.sqlite')
        self.cursor = self.connection.cursor()

        self.bot_msg = 'Hello'

        self.init_db()

    def init_db(self):
        """create the tables needed by the program"""
        create_table_request_list = [
            'CREATE TABLE IF NOT EXISTS words(word TEXT UNIQUE)',
            'CREATE TABLE IF NOT EXISTS sentences(sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)',
            'CREATE TABLE IF NOT EXISTS associations (word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)',
        ]
        for create_table_request in create_table_request_list:
            try:
                self.cursor.execute(create_table_request)
            except:
                pass

    def get_id(self, entityName, text):
        """Retrieve an entity's unique ID from the database, given its associated text.
        If the row is not already present, it is inserted.
        The entity can either be a sentence or a word."""
        tableName = entityName + 's'
        columnName = entityName
        self.cursor.execute('SELECT rowid FROM ' + tableName + ' WHERE ' + columnName + ' = ?', (text,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            self.cursor.execute('INSERT INTO ' + tableName + ' (' + columnName + ') VALUES (?)', (text,))
            return self.cursor.lastrowid

    def get_words(self, text):
        """Retrieve the words present in a given string of text.
        The return value is a list of tuples where the first member is a lowercase word,
        and the second member the number of time it is present in the text."""
        wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
        wordsRegexp = re.compile(wordsRegexpString)
        wordsList = wordsRegexp.findall(text.lower())
        return Counter(wordsList).items()

    def clean_tables(self):
        """This will clear all the table data required for chat.
        WARNING : Do not call this method unless you want to reset everything. This is dangerous."""
        truncate_table_request_list = [
            'TRUNCATE TABLE words',
            'TRUNCATE TABLE sentences',
            'TRUNCATE TABLE associations',
        ]
        for truncate_table_request in truncate_table_request_list:
            try:
                self.cursor.execute(truncate_table_request)
            except:
                pass

    def basic_validation(self, words):
        # Get the list of valid words from nltk dictionary
        # set_of_words = set(nltk_words.words())

        # for word in words:
            # Check if the input word is a valid english word
            # if word not in set_of_words:
            #   return False


            # if not wordnet.synsets(word):
            #     return False

        return True

    def filter_punctuation(self, inp_str):
        inp_str = inp_str.replace(".", "")
        inp_str = inp_str.replace(",", "")
        inp_str = inp_str.replace("?", "")

        return inp_str

    def process_known_questions(self, question):
        greetings_text = ["hi", "hello", "greetings"]
        greetings_resp = ["Hey", "Hello there", "Hello", "Hey, what's up?", "Hi", "Hi, how can I help you?"]

        question = question.lower()
        question = self.filter_punctuation(question)

        if question in greetings_text:
            self.bot_msg = random.choice(greetings_resp)
            return True

        if re.search("how are.*", question) != None:
            self.bot_msg = random.choice(["Everything's fine", "Absolutely fine"])
            return True

        if re.search('what is.*name', question) != None:
            self.bot_msg = "My name is Ashwathama"
            return True

        if re.search('who (created|made) you', question) != None:
            self.bot_msg = "Some developer :)"
            return True

        if re.search('what is your task', question) != None:
            self.bot_msg = "Provide you the required info"
            return True

        if re.search('how can you help me', question) != None:
            self.bot_msg = "You can ask questions, I'll try to provide you answers"
            return True

        if re.search('college fees', question) != None or re.search('college department', question) != None or re.search('college faculty', question) != None or re.search('college library', question) != None or re.search('college info', question) != None or re.search('college name', question) != None or re.search('my college', question) != None:
            self.bot_msg = "Please find all these info in the official college website"
            return True

        if re.search('where you studied', question) != None:
            self.bot_msg = "Python library"
            return True

        if re.search('where are you from', question) != None:
            self.bot_msg = "I'm from your PC"
            return True

        if re.search('why you born', question) != None:
            self.bot_msg = "To make the world a better place"
            return True

        return False

    def process(self, input_str):
        inp_words = input_str.split(" ")

        # If input word is not valid, stop processing
        if not self.basic_validation(inp_words) :
            self.bot_msg = "Please enter valid english words."
            return self.bot_msg

        # Check for basic questions, if known answer immediately
        if self.process_known_questions(input_str) :
            return self.bot_msg

        # store the association between the bot's message words and the user's response
        words = self.get_words(self.bot_msg)

        words_length = sum([n * len(word) for word, n in words])
        sentence_id = self.get_id('sentence', input_str)
        for word, n in words:
            word_id = self.get_id('word', word)
            weight = sqrt(n / float(words_length))
            self.cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
        self.connection.commit()

        # retrieve the most likely answer from the database
        self.cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
        words = self.get_words(input_str)
        words_length = sum([n * len(word) for word, n in words])
        for word, n in words:
            weight = sqrt(n / float(words_length))
            self.cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))

        # if matches were found, give the best one
        self.cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
        row = self.cursor.fetchone()
        self.cursor.execute('DROP TABLE results')

        # otherwise, just randomly pick one of the least used sentences
        if row is None:
            self.cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
            row = self.cursor.fetchone()

        # tell the database the sentence has been used once more, and prepare the sentence
        self.bot_msg = row[1]
        self.cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))

        return self.bot_msg
