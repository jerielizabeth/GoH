# -*- coding: utf-8 -*-

"""Series of functions for preprocessing and modeling a corpus.

Functions developed relying on the examples of
    http://radimrehurek.com/topic_modeling_tutorial/1%20-%20Streamed%20Corpora.html
    http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
    http://radimrehurek.com/topic_modeling_tutorial/3%20-%20Indexing%20and%20Retrieval.html
"""

import os
import sys
import re
import tarfile
import itertools
import nltk
import gensim
from gensim import utils
from gensim.parsing.preprocessing import STOPWORDS
from textblob import TextBlob
import GoH.utilities
from GoH.preprocess import ENTITIES
from nltk.stem.wordnet import WordNetLemmatizer

def process_page(page):
    """
    Preprocess a single periodical page, returning the result as
    a unicode string.

    Removes all non-alpha characters (except "'") from the text.

    Args:
        page (str): Passes in the page object

    Returns:
        str: Content of the file, but without punctuation and non-alpha characters.
    """
    content = utils.any2unicode(page, 'utf8').strip()
    content = re.sub(r"[^a-zA-Z']", " ", content)
    
    return content
    

def iter_Periodicals(fname, log_every=None):
    """
    Yield plain text of each periodical page, as a unicode string. Extracts from a zip of the entire corpus.

    Args:
        fname (str): Name of the archive file.

    Yields:
        str: Yields the content of the file after passing it through the :func:`process_page` function.
    """
    extracted = 0
    with tarfile.open(fname, 'r:gz') as tf:
        for file_number, file_info in enumerate(tf):
            if file_info.isfile():
                if log_every and extracted % log_every == 0:
                    logging.info("extracting file #%i: %s" % (extracted, file_info.name))
                title = file_info.name[2:]
                content = tf.extractfile(file_info).read()
                yield title, process_page(content)
                extracted += 1


def head(stream, n=10):
    """Convenience fnc: return the first `n` elements of the stream, as plain list."""
    return list(itertools.islice(stream, n))


def best_phrases(document_stream, top_n=2000, prune_at=100000):
    """Return a set of `top_n` most common noun phrases."""
    np_counts = {}
    for docno, doc in enumerate(document_stream):
        # prune out infrequent phrases from time to time, to save RAM.
        # the result may not be completely accurate because of this step
        if docno % 1000 == 0:
            sorted_phrases = sorted(np_counts.items(), key=lambda item: -item[1])
            np_counts = dict(sorted_phrases[:prune_at])
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docno, len(np_counts), head(sorted_phrases)))
        
        # how many times have we seen each noun phrase?
        for np in TextBlob(doc).noun_phrases:
            # only consider multi-word NEs where each word contains at least one letter
            if u' ' not in np:
                continue
            # ignore phrases that contain too short/non-alphabetic words
            if all(word.isalpha() and len(word) > 2 for word in np.split()):
                np_counts[np] = np_counts.get(np, 0) + 1

    sorted_phrases = sorted(np_counts, key=lambda np: -np_counts[np])
    return set(head(sorted_phrases, top_n))


def get_entities(filepath):
    """Load saved list of phrases or named entities. These are used to
    """
    with open(filepath) as f:
        return f.read().splitlines()


def tokenize(message, lemmatize=True, tokenizer='whitespace', entities=ENTITIES, stopwords=STOPWORDS):
    """
    Break text (string) into a list of Unicode tokens.
    
    The resulting tokens can be longer phrases (named entities) too,
    e.g. `new_york`, `real_estate` etc.

    Args:
        message(str) : The content of a page, as streamed in through the :func:`iter_Periodicals` function.
        tokenizer(str) : Uses the utilities :func:`tokenizer` function. Currently enables choice
            between the whitespace tokenizer (default) and the NLTK word tokenizer.
        entities(str) : List of noun phrases saved
        stopwords(str) : List of stopwords, currently the defaults from Gensim.
    Returns:
        list: List of tokens in the text.
    """
    phrases = []
            
    for np in TextBlob(message).noun_phrases:
        if ' ' in np and np in entities:            
            phrases.append(np)

    message = message.lower()
    
    for phrase in phrases:
        replacement_phrase = re.sub('\s', '_', phrase)
        message = re.sub(phrase, replacement_phrase, message)
        
    tokens = GoH.utilities.tokenize_text(message, tokenizer)
    
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    token_list = []
    for token in tokens:
        if len(token) < 3 or token in stopwords:
            continue
        token_list.append(token)
                
    return token_list


class Tokenized_Corpus(object):
    
    def __init__(self, fname, lemmatize, tokenizer):
        self.fname = fname
        self.tokenizer = tokenizer
        self.lemmatize = lemmatize

        
    def __iter__(self):
        for title, message in iter_Periodicals(self.fname):
            yield title, tokenize(message, self.lemmatize, self.tokenizer)