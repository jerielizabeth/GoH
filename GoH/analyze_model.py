# -*- coding: utf-8 -*-

import GoH.extract_model
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns


def subset_by_set(dt, metadata, column="abrev", value=""):
    """
    Args:

    Returns:
    """
    df = dt.merge(metadata, how='left', on='doc_id')
    
    return df[df[column].isin(value)]


def light_smooth(subbed_df, smooth_value):
    """
    Args:

    Returns:
    """
    m = subbed_df.pivot(index="doc_id", columns="topic", values="word_counts").fillna(0)
    m = m + smooth_value
    df = m.unstack().reset_index()
    df.columns = ['topic', 'doc_id', 'word_counts']

    return df


def aggregate_by_time(df, metadata):
    """
    Args:

    Returns:
    """
    df = df.merge(metadata, how="left", on="doc_id")
    
    return df.groupby([df.date_formatted.dt.year, 'topic']).agg({'word_counts': 'sum'}).reset_index()


def norm_matrix(df, verify):
    """
    Args:

    Returns:
    """
    m = df.pivot(index="date_formatted", columns="topic", values="word_counts")
    m = m.div(m.sum(axis=1), axis=0)
    if verify == True:
        print(m.iloc[0].sum())
    df = m.unstack().reset_index()
    df.columns = ['topic', 'year', 'topic_proportion']
    
    return df


def prepare_data_set(df, metadata, smooth_value, subset=True, doc_set="", smooth=True, norm=True, verify=False):
    """Compilation function.

    Args:

    Returns:
    """
    if subset == True:
        df = subset_by_set(df, metadata, value=doc_set)
    if smooth == True:
        df = light_smooth(df, smooth_value)
    df = aggregate_by_time(df, metadata)
    if norm == True:
        df = norm_matrix(df, verify)
    
    return df


def select_topics(df, columns=""):
    """
    Args:

    Returns:
    """

    return df[df['topic'].isin(columns)]


def plot_select_topics(df, collection):
    """
    Args:

    Returns:
    """
    df = select_topics(df, collection)
    sns.lmplot(x="year", y="topic_proportion", hue='topic', data=df, fit_reg=False, size=4, aspect=2)
    plt.ylim(0, 0.2)
    plt.xlim(1845, 1925)

    
def plot_sum_select_topics(df, collection):
    """
    Args:

    Returns:
    """
    subset = df.pivot(index="year", columns="topic", values="topic_proportion")
    summed = subset[collection].sum(axis=1)
    summed.plot(figsize=(9,5))
    plt.ylim(0, 0.2)
    plt.xlim(1845, 1925)


def plot_and_sum_topics(df, collection, title):
    """
    Args:

    Returns:
    """
    plot_select_topics(df, collection)
    plot_sum_select_topics(df, collection)
    plt.title(title)

