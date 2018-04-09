import GoH.modeldata
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def create_period_dataframe(base_dir, model, model_scheme, period):
    """
    Compiles the dataframe for a given model, periodization, and period.
    Args:
        base_dir (str): 
        model (str): folder name for the model files
        model_scheme (str): name of the periodization scheme ('full_corpus', 'historical-period',
            'decades', 'cumulative_historical_periods', 'cumulative_decades')
        period (str): timeperiod within the scheme to examine.
    """
    df = GoH.modeldata.model_to_df(base_dir, model, model_scheme, period)
    return df[df['norm_topic_weight'] > 0]


def create_bargraph(df, topic_id):
    """
    Uses Seaborn to create a bargraph of the proportion of total weight for a topic 
    in a given year.
    Args:
        df (dataframe): dataframe to chart. Use the GoH.modeldata.topic_series function to get into desired form.
        topic_id (str): value of the widget for the selected topic.
    """
    g = sns.barplot(x='year', y='normalized_weight', data=df, hue='topic_id')
    g.set(ylim=(0, 0.5))
    return g


def create_regress_plot(df, topic_id):
    """
    Uses Seaborn to create a lowess regress plot of the proportion of total weight for a topic 
    in a given year.
    Args:
        df (dataframe): dataframe to chart. Use the GoH.modeldata.topic_series function to get into desired form.
        topic_id (str): value of the widget for the selected topic.
    """
    g = sns.regplot(x='year', y='normalized_weight', data=df, lowess=True)
    g.set(ylim=(0, 0.5))
    return g


def get_doc_topics(df, doc_id):
    """
    Return the topics assigned to a given document
    Args:
        df (dataframe): dataframe with corpus information. Use results of `create_period_dataframe`
        doc_id (str): takes the document filename as a string to pull up the related topics.
    """
    return df[df['doc_id'] == doc_id]