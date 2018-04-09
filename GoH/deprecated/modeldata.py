import GoH.utilities
import json
import os
import pandas as pd


def queue_docs(base_dir, test, model_scheme, period):
    """
    base_dir, model_scheme, period
    """

    corpus_index = os.path.join(base_dir, 'corpora/{}/{}.txt'.format(model_scheme, period))
    dtm = os.path.join(base_dir, 'dataframes/{}/{}-{}_dtm.csv'.format(test, model_scheme, period))
    topic_labels = os.path.join(base_dir, 'dataframes/{}/{}-{}_topicLabels.csv'.format(test, model_scheme, period))
    metadata = os.path.join(base_dir,'2017-05-corpus-stats/2017-05-Composite-OCR-statistics.csv')

    return (corpus_index, dtm, topic_labels, metadata)



def doc_list(index_filename):
    """
    """
    with open(index_filename) as data_file:    
        data = json.load(data_file)
    docs = pd.DataFrame.from_dict(data, orient='index').reset_index()
    docs.columns = ['index_pos', 'doc_id']
    docs['index_pos'] = docs['index_pos'].astype(int)
  
    return docs



def doc_metadata(metadata_filename):
    """
    """
    data = pd.read_csv(metadata_filename, usecols=['doc_id', 'year','title'])
    return data




def normalize_df(dt):
    """
    """
    # Reorient from long to wide
    dtm = dt.pivot(index='index_pos', columns='topic_id', values='topic_weight').fillna(0)

    # Divide each value in a row by the sum of the row to normalize the values
    # https://stackoverflow.com/questions/18594469/normalizing-a-pandas-dataframe-by-row
    dtm = dtm.div(dtm.sum(axis=1), axis=0)

    # Shift back to a long dataframe
    dt_norm = dtm.stack().reset_index()
    dt_norm.columns = ['index_pos', 'topic_id', 'norm_topic_weight']

    return dt_norm



def compile_dataframe( docs_tuple, normalize=True):
    """
    docs_tuple = index, documentTopicMatrix, topicLabels, metadata
    """
    
    docs = doc_list(docs_tuple[0])
    metadata = doc_metadata(docs_tuple[3])
    doc2topics = pd.read_csv(docs_tuple[1])
    topics = pd.read_csv(docs_tuple[2])

    if normalize==True:
        doc2topics = normalize_df(doc2topics)

    doc2metadata = docs.merge(metadata, on='doc_id', how="left")
    topics_expanded = doc2topics.merge(topics, on='topic_id')
    
    df = topics_expanded.merge(doc2metadata, on="index_pos", how="left")
    
    return df




def model_to_df(base_dir, test, model_scheme, period):
    """
    base_dir, directory, corpus_file, model_scheme
    """
    docs = queue_docs(base_dir, test, model_scheme, period)
    df = compile_dataframe(docs)
    
    return df



# Standard manipulations of Compiled Dataframe

def filter_dataframe_by_dates(df, start_year, end_year):
    """
    """
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]

    return filtered_df



def topic_series(df, groupby_fields, labels):
    """
    base: ['year', 'topic_id']
    """
    
    grouped = df.groupby(groupby_fields).agg({'norm_topic_weight': 'sum'})

    # This achieves a similar computation as the normalizing function above, but without converting into a matrix first.
    # For each group (in this case year), we are dividing the values by the sum of the values. 
    normed = grouped.groupby(level=0).apply(lambda x: x / x.sum()).reset_index()
    normed.columns = [groupby_fields[0], groupby_fields[1], 'normalized_weight']
    
    return normed.merge(labels, on="topic_id")


def get_top(df, group, value, n=5):
    """
    Args:
        df (dataframe): pandas dataframe
        group (str): name of the column to group by, such as "topic_id" or "doc_id"
        value (str): name of the column to get max values from, such as "norm_topic_weight" or "normalized_weight"
    """
    return df.groupby(group).apply(lambda x: x[x[value].isin(x[value].nlargest(n))]).reset_index(drop=True)



def evaluate_topic_docs(df, topic_id, top_n=30):
    """
    """
    topic_df = df[df['topic_id'] == topic_id]
    topic_df = topic_df.sort_values('norm_topic_weight', ascending=False)
    docs = topic_df['doc_id'].tolist()[:top_n]
    GoH.utilities.open_original_docs(docs)

