# -*- coding: utf-8 -*-

import gzip
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import sklearn.preprocessing

def extract_params(statefile):
    """Extract the alpha and beta values from the statefile.

    Args:
        statefile (str): Path to statefile produced by Mallet.
    Returns:
        tuple: alpha, beta    
    """
    with gzip.open(statefile, 'r') as state:
        params = [x.decode('utf8').strip() for x in state.readlines()[1:3]]
    return (list(params[0].split(":")[1].split(" ")), float(params[1].split(":")[1]))


def state_to_df(statefile):
    """Transform state file into pandas dataframe
    """
    return pd.read_csv(statefile,
                       compression='gzip',
                       sep=' ',
                       skiprows=[1,2]
                       )


def get_topic_keys(keyfile):
    """Turn topic/key information into pandas dataframe
    """
    df = pd.read_csv(keyfile, sep='\t', header=None)
    return df.rename(columns = {0:'topic', 1: 'overallWeight', 2: 'topic_words'})


def aggregate_data(df, topic_col='topic', word_col='type'):
    """
    """
    df = df.groupby([topic_col, word_col]).agg({word_col: {'count': lambda x: x.count()}})
    df.columns = df.columns.droplevel(0)
    
    return df.reset_index()


def pivot_and_smooth(df, smooth_value, rows='type', cols='topic'):
    """
    """
    matrix = df.pivot(index=rows, columns=cols, values='count').fillna(value=0)
    matrix = matrix + smooth_value
    
    return pd.DataFrame(sklearn.preprocessing.normalize(matrix, norm='l1', axis=0))


def graph_matrix(matrix):
    """
    Note: Negative correlations, which would indicate that the words in one topic are 
    missing from another topic, are not interesting for our purpose of measuring when topics
    overshare words. By centering at 0.5, we are focusing on positive overlap between topics.
    """
    f, ax = plt.subplots(figsize=(30,30))
    mask = np.zeros_like(matrix)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        sns.heatmap(matrix,
                    center = 0.5,
                    mask = mask, 
                    cmap = sns.diverging_palette(220, 10, as_cmap=True),
                    square = True,
                    xticklabels = 2,
                    cbar_kws={"label":"Correlation (Pearson) between Topics"},
                    ax = ax)


def get_top_pairs(matrix, n_pairs):
    df = pd.DataFrame(matrix.where(np.triu(np.ones(matrix.shape), k=1).astype(np.bool)).stack().sort_values(ascending=False)[:n_pairs]).reset_index()
    df = df.rename(columns = {'level_0': 'topic_1', 'level_1': 'topic_2', 0: 'correlation'})
    return df


def merge_frames(pairs, keys):
    merge1 = pairs.merge(keys, left_on='topic_1', right_on='topic', how='left')
    return merge1.merge(keys, left_on='topic_2', right_on='topic', how='left')