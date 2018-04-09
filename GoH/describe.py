# -*- coding: utf-8 -*-

from bokeh.plotting import figure, output_file, output_notebook, save, show
from collections import defaultdict
from GoH import utilities
# from GoH import charts
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from nltk import FreqDist
import numpy as np
import operator
from os import listdir
from os.path import isfile, join
import pandas as pd
import re
import seaborn as sns



def identify_errors(tokens, dictionary):
    """Compare words in documents to words in dictionary. 

    Args:
        tokens (list): List of all tokens in the document.
        dictionary (set): The set of approved words.
    Returns:
        set : Returns the set of tokens in the documents that are not 
            also dictionary words.
    """
    return set(tokens).difference(dictionary)


def get_error_stats(errors, tokens):
    """ Returns a dictionary recording each error and its 
    frequency in the document.

    Uses the FreqDist function from NLTK.

    Args:
        errors (set): Set of errors identified in `identify_errors`.
        tokens (list): Tokenized content of the file being evaluated.
    """
    freq_distribution = FreqDist(tokens) 
    
    error_report = {}
    for error in list(errors):
        error_count = freq_distribution[error]
        error_report.update({error:error_count})
        
    return error_report    


def total_errors(error_report):
    """ Calculates the total errors recorded in the document.

    Args:
        error_report (dict): Dictionary of errors and counts generated
            using `get_error_stats` function.
    """
    return(sum(error_report.values()))


def error_rate(error_total, tokens):
    """ Calculates the error rate of the document to 3 decimal places.

    Arguments:
    error_total -- Integer. Calculated using the `total_errors` 
    function from the dictionary of errors and their counts.
    tokens -- List of tokens that compose the text
    """
    if len(tokens) > 0:
        return(float("{0:.3f}".format(error_total/len(tokens))))
    else:
        return(np.nan)

   
def generate_doc_report(text, spelling_dictionary):
    """ 
    Creates a report (dictionary) on each document that includes:
        - number of tokens (num_tokens)
        - number of unique tokens (num_unique_tokens)
        - number of errors (num_errors)
        - error rate for the document (error_rate)
        - dictionary of the errors and their counts (errors)

    Uses a number of functions, including:
        - `GoH.utilities.strip_punct`
        - `GoH.utilities.tokenize_text`
        - `GoH.utilities.to_lower`
        - `GoH.utilities.identify_errors`
        - `GoH.reports.get_error_stats`
        - `GoH.reports.total_errors`
        - `GoH.reports.error_rate`

    Arguments:
    - text -- the content of the file being evaluated
    - spelling_dictionary -- a set containing the collection of verified words.
    """
    text = utilities.strip_punct(text)
    tokens = utilities.tokenize_text(text)
    tokens = utilities.to_lower(tokens)
    errors = identify_errors(tokens, spelling_dictionary)
    error_report = get_error_stats(errors, tokens)
    error_total = total_errors(error_report)
    rate = error_rate(error_total, tokens)
    return {'num_tokens': len(tokens),
             'num_unique_tokens': len(set(tokens)),
             'num_errors': error_total,
             'error_rate': rate,
             'errors': error_report}


def process_directory(directory, spelling_dictionary):
    """ 
    Composit function for processing an entire directory of files.
    Returns the statistics on the whole directory as a list of dictionaries.

    Uses the following functions:
        - `GoH.utilities.readfile`
        - `GoH.reports.generate_doc_report`

    Arguments:
    - directory -- the location of the directory of files to evaluate.
    - spelling_dictionary -- the set containing all verified words against which
    the document is evaluated.
    """
    corpus = (f for f in listdir(directory) if not f.startswith('.') and isfile(join(directory, f)))
        
    statistics = []
    for document in corpus:
        content = utilities.readfile(directory, document)
        stats = generate_doc_report(content, spelling_dictionary)
        stats.update({"doc_id": document})
        statistics.append(stats)
 
    return(statistics) 


def get_errors_summary(statistics):
    """
    Get statistics on the errors for the whole directory.
    Creates a dictionary (errors_summary) from all the reported errors/frequencies
    that records the error (as key) and the total count for that error (as value).
    Developed using: http://stackoverflow.com/questions/11011756, 
    http://stackoverflow.com/questions/27801945/
    """
    all_errors = (report['errors'] for report in statistics)       
    
    errors_summary = defaultdict(int)
    for doc in all_errors:
        for key, value in doc.items():
            errors_summary[key] += value

    return errors_summary


def top_errors(errors_summary, min_count):
    """ 
    Use the errors_summary to report the top errors.
    """

    # Subset errors_summary using the min_count
    frequent_errors = {key: value for key, value in errors_summary.items() if value > min_count}

    # return sorted list of all errors with a count higher than the min_count
    return sorted(frequent_errors.items(), key=operator.itemgetter(1), reverse=True)


def long_errors(errors_summary, min_length=10):
    """
    Use the error_summary to isolate tokens that are longer thatn the min_length. 
    Used to identify strings of words that have been run together due to the failure
    of the OCR engine to recognize whitespace.

    Arguments:
    - errors_summary -- 
    """
    errors = list(errors_summary.keys())

    return ([x for x in errors if len(x) > min_length], min_length)


def tokens_with_special_characters(errors_summary):
    errors = list(errors_summary.keys())

    special_characters = []
    for error in errors:
        if re.search("[^a-z0-9-']", error):
            special_characters.append(error)
        else:
            pass

    sc_dict = dict(map(lambda key: (key, errors_summary.get(key, None)), special_characters))

    return sorted(sc_dict.items(), key=operator.itemgetter(1), reverse=True)


def docs_with_high_error_rate(corpus_statistics, min_error_rate=.2):
    # Gather list of doc_id and num_errors
    docs_2_errors = {}
    for report in corpus_statistics:
        docs_2_errors.update({report['doc_id']: report['error_rate']})

    # Subset dictionary to get only records with error_rate above minimum
    problem_docs = {key: value for key, value in docs_2_errors.items() if value > min_error_rate}

    # return dictionary with doc_id and error_count if error rate higher than min_error_rate
    return sorted(problem_docs.items(), key=operator.itemgetter(1), reverse=True)


def docs_with_low_token_count(corpus_statistics, max_token_count=350):
    # Gather list of doc_ids and total token count
    docs_2_tokens = {}
    for report in corpus_statistics:
        docs_2_tokens.update({report['doc_id']: report['num_tokens']})

    # Subset dictionary to get only records wth value below the max
    short_docs = {key: value for key, value in docs_2_tokens.items() if value < max_token_count}

    # return dictionary with doc_id and token_count if count is lower than max_token_count
    return (short_docs, max_token_count)


def token_count(df):
    return df['num_tokens'].sum()


def average_verified_rate(df):
    """ To compute average error rate, add up the total number of tokens
    and the total number of errors """
    total_tokens = token_count(df)
    total_errors = df['num_errors'].sum()

    if total_tokens > 0:
        return (total_tokens - total_errors)/total_tokens
    else:
        return np.nan


def average_error_rate(df):
    error_sum = df['error_rate'].sum()
    total_docs = len(df.index)

    return error_sum/total_docs


def overview_report(directory, spelling_dictionary, title):
    corpus_statistics = process_directory(directory, spelling_dictionary)

    df = utilities.stats_to_df(corpus_statistics)

    print("Directory: {}\n".format(directory))
    print("Average verified rate: {}\n".format(average_verified_rate(df)))
    print("Average of error rates: {}\n".format(average_error_rate(df)))
    print("Total token count: {}\n".format(token_count(df)))

    chart_error_rate_distribution(df, title)
    # chart_error_rate_per_doc( df, title )

    return corpus_statistics

def overview_statistics(directory, spelling_dictionary, title):
    """
    """
    corpus_statistics = process_directory(directory, spelling_dictionary)

    return utilities.stats_to_df(corpus_statistics)



## Charts

def chart_error_rate_distribution( df, title ):
    """
    """
    
    df = df[pd.notnull(df['error_rate'])]
    
    # graph the distribution of the error rates
    x = pd.Series(df['error_rate'], name="Error Rate per Periodical Page")
    ax = sns.distplot(x)
    # p = Histogram(df,
    #         values='error_rate',
    #         color='lime',
    #         title="Distribution of error rates for {}".format(title) )
    # p.x_range = Range1d(-0.01,1)
    
    return(ax)

def chart_error_rate_per_doc( df, title ):
    """
    """
    
    # sort df by doc_id
    df = df.sort_values(by='doc_id')
    
    # graph the error_rate by the doc_id

    plt.plot(df['error_rate'])
    plt.title('Error rate by Title for {}'.format(title))
    plt.xlabel('Doc Id')
    plt.ylabel('Rate')
    return(plt)