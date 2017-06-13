from gensim import utils
from gensim.parsing.preprocessing import STOPWORDS
from GoH.preprocess import ENTITIES
import itertools
import logging
# from nltk.tokenize import WhitespaceTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
import os
import re
import sys
import tarfile
from textblob import TextBlob


def process_page(page):
    """
    Preprocess a single periodical page, returning the result as
    a unicode string.

    Removes all non-alpha characters from the text.

    Args:
        page (str): Passes in the page object

    Returns:
        str: Content of the file, but without punctuation and non-alpha characters.
    """
    content = utils.any2unicode(page, 'utf8').strip()
    content = re.sub(r"[^a-zA-Z]", " ", content)
    
    return content


def iter_Periodicals(fname, log_every=500):
    """
    Yield plain text of each periodical page, as a unicode string. Extracts from a zip of the entire corpus.

    Args:
        fname (str): Name of the archive file.

    Yields:
        str: Yields the content of the file after passing it through the :func:`process_page` function.
    """
    doc_id = 0
    with tarfile.open(fname, 'r:gz') as tf:
        for file_number, file_info in enumerate(tf):
            if file_info.isfile():
                if log_every and doc_id % log_every == 0:
                    logging.info("extracting file #%i: %s" % (doc_id, file_info.name))
                title = file_info.name[2:]
                content = tf.extractfile(file_info).read()
                yield title, doc_id, process_page(content)
                doc_id += 1


def head(stream, n=10):
    """Convenience fnc: return the first `n` elements of the stream, as plain list."""
    return list(itertools.islice(stream, n))


def connect_phrases(content, entities=ENTITIES):
    """Convert named entities into a single token.

    """
    phrases = []
        
    for np in TextBlob(content).noun_phrases:
        if ' ' in np and np.lower() in entities:            
            phrases.append(np.lower())

    content = content.lower()
    
    for phrase in phrases:
        replacement_phrase = re.sub('\s', '_', phrase)
        content = re.sub(phrase, replacement_phrase, content)

    return content


def filter_tokens(tokens, stopwords=STOPWORDS):
    """Filter out short and stopword tokens for clustering.
    """
    token_list = []
    for token in tokens:
        if len(token) > 3 and token not in stopwords:
            token_list.append(token)
        else:
            continue
                
    return token_list


def lemmatize_tokens(tokens):
    """Convert tokens to lemmas.
    """
    lemmatizer = WordNetLemmatizer()
    lemma_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return lemma_tokens


def doc2id(corpus):
    doc_dict = {}
    for title, doc_id, content in iter_Periodicals(corpus):
        doc_dict[doc_id] = title
    return doc_dict


# class Basic_Corpus(object):
#     """Base level processing of the corpus. 
#     Simple application of the nltk `word_tokenize` function.

#     """
#     def __init__(self, fname):
#         self.fname = fname

#     def process_corpus(self, content):
#         return word_tokenize(content)
    
#     def __iter__(self):
#         for title, doc_id, content in iter_Periodicals(self.fname):
#             yield title, self.process_corpus(content)


class Standard_Corpus(object):
    """Standard processing of the corpus.
    Named entity phrases are identified prior to tokenizing and the tokens are filtered
    by frequency and length.
    """

    def __init__(self, fname):
        self.fname = fname

    def process_corpus(self, content):
        content = connect_phrases(content)
        tokens = word_tokenize(content)

        return filter_tokens(tokens)


    def __iter__(self):
        for title, doc_id, content in iter_Periodicals(self.fname):
            yield title, doc_id, self.process_corpus(content)


class Lemma_Corpus(object):
    """Adds lemmatization step to the standard corpus creation workflow.
    """
    def __init__(self, fname):
        self.fname = fname

    def process_corpus(self, content):
        content = connect_phrases(content)
        tokens = word_tokenize(content)
        lemmas = lemmatize_tokens(tokens)

        return filter_tokens(lemmas)

    def __iter__(self):
        for title, doc_id, content in iter_Periodicals(self.fname):
            yield title, doc_id, self.process_corpus(content)


class BoWCorpus(object):
    def __init__(self, corpus_object, dictionary):
        """
        From http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
        
        """
        self.corpus_object = corpus_object
        self.dictionary = dictionary

    def __iter__(self, log_every=500):
        for title, doc_id, tokens in self.corpus_object:
            if log_every and doc_id % log_every == 0:
                logging.info("{}".format(tokens))
            yield self.dictionary.doc2bow(tokens)
