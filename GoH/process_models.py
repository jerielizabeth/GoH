from bokeh.charts import Bar, HeatMap, TimeSeries, show, output_file
# from bokeh.io import output_notebook
from bokeh.models import HoverTool, BoxSelectTool, Legend
from bokeh.palettes import viridis, d3
import gensim
import logging
import json
import os
import pandas as pd
from sklearn import preprocessing

## Model Creation
def process_period(base_dir, period, num_topics=30, iterations=50, passes=8):
    """
    """
    corpus = gensim.corpora.MmCorpus(os.path.join(base_dir, "{}.mm".format(period)))
    dictionary = gensim.corpora.Dictionary.load(os.path.join(base_dir, "{}.dict".format(period)))
    model = gensim.models.LdaModel(corpus, 
                                   num_topics=num_topics, 
                                   id2word=dictionary, 
                                   alpha='auto', 
                                   iterations=iterations, 
                                   passes=passes
                                  )                               
    return (model, corpus, dictionary)


## Create Dataframe from Models 
def queue_docs(base_dir, scheme, period):
    return (os.path.join(base_dir, 'corpora/{}/{}.txt'.format(scheme, period)),
            os.path.join(base_dir, 'models/{}/{}.model'.format(scheme, period)),
            os.path.join(base_dir,'2017-05-corpus-stats/2017-05-Composite-OCR-statistics.csv'),
            os.path.join(base_dir, 'corpora/{}/{}.mm'.format(scheme, period))    
           )

def doc_list(index_filename):
    """
    """
    with open(index_filename) as data_file:    
        data = json.load(data_file)
    docs = pd.DataFrame.from_dict(data, orient='index').reset_index()
    docs.columns = ['index_pos', 'doc_id']
    docs['index_pos'] = docs['index_pos'].astype(int)
  
    return docs


def doc_topic(lda_model, corpus):
    """
    """
    dtm = lda_model[corpus]
    doc_topics = []
    i = 0
    for doc in dtm:
        for topic in doc:
            topic_id = topic[0]
            topic_weight = topic[1]
            doc_topics.append((i, topic_id, topic_weight))
        i = i+1
    df = pd.DataFrame(doc_topics, columns=['index_pos', 'topic_id', 'topic_weight'])  
    
    return df


def topic_words(lda_model):
    """
    """
    topic_words = []
    for i in range(0,len(lda_model.show_topics(-1))):
        words_list = lda_model.show_topic(i, topn=6)
        words = []
        for each in words_list:
            words.append(each[0])
        topic_words.append((i, ', '.join(words)))
    return pd.DataFrame(topic_words, columns=['topic_id', 'topic_words'])


def doc_metadata(metadata_filename):
    """
    """
    data = pd.read_csv(metadata_filename, usecols=['doc_id', 'year','title'])
    return data


def test_function(docs_tuple):
    corpus = gensim.corpora.MmCorpus(docs_tuple[3])
    lda_model = gensim.models.LdaModel.load(docs_tuple[1])

    return (corpus, lda_model)


def compile_dataframe( docs_tuple):
    """
    docs_tuple = index_filepath, model_filepath, metadata_filepath, corpus_filepath
    """
    corpus = gensim.corpora.MmCorpus(docs_tuple[3])
    lda_model = gensim.models.LdaModel.load(docs_tuple[1])
#     print(type(lda_model))
    
    docs = doc_list(docs_tuple[0])
    metadata = doc_metadata(docs_tuple[2])
    doc2topics = doc_topic(lda_model, corpus)
    topics = topic_words(lda_model)

    doc2metadata = docs.merge(metadata, on='doc_id', how="left")
    topics_expanded = doc2topics.merge(topics, on='topic_id')
    
    df = topics_expanded.merge(doc2metadata, on="index_pos", how="left")
    
    return df


def model_to_df(base_dir, directory, filename):
    """
    """
    docs = queue_docs(base_dir, directory, filename)
    df = compile_dataframe(docs)
    
    return df


## Manipulate Dataframes
def filter_dataframe_by_dates(df, start_year, end_year):
    """
    """
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]

    return filtered_df


def compute_prevalence(df, groupby_fields):
    """
    base: ['topic_id', 'year', 'topic_words']
    """
    agg_df = df.groupby(groupby_fields)[['topic_weight']].sum().reset_index()
    min_max_scaler = preprocessing.MinMaxScaler()
    agg_df['normalized_weights'] = pd.Series(min_max_scaler.fit_transform(agg_df.topic_weight), 
                                               index=agg_df.index)
    
    return agg_df


# Visualization Functions
def create_heatmap(df, x_axis):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("weight", "@normalized_weights")
            ]
        )

    p = HeatMap(df, 
                   x=x_axis, 
                   y='topic_words', 
                   values='normalized_weights',
                   stat=None,
                   sort_dim={'x': False}, 
                   width=900, 
                   plot_height=500,
                   tools=[hover],
                   legend=False,
                  )
    p.yaxis.major_label_orientation = 'horizontal'
    # p.xaxis.minor_tick_line_color = None

    return p


def create_timeseries(df, x_axis):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "($x{int}, $y)"),
            ("topic_words", "@topic_words")
            ]
        )
    p = TimeSeries(df, 
                   x=x_axis,
                   y="normalized_weights", 
                   legend=False,
                   ylabel='topics distribution',
                   color="topic_words",
                   palette=viridis(25), 
                   tools=[hover, BoxSelectTool()]
                  )
    # p.xaxis.minor_tick_line_color = None

    return p


def create_bargraph(df):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("title", "@title")
            ]
        )

    p = Bar(df, 
            label='topic_id', 
            values='normalized_weights', 
            stack='title', 
            legend=False, 
            tools=[hover], 
            plot_width=600,
            palette=d3['Category20'][20]
           )
    
    return p   

## Composit Function
def visualize_models(df, period, filter_df):
    """
    """
    if filter_df is True:
        end_year = int(period[0].split('-')[-1])
        start_year = int(period[1])

        df = filter_dataframe_by_dates(df, start_year, end_year)
            
    agg_df = compute_prevalence(df, ['topic_id', 'year', 'topic_words'])
    
    print("Topic Distribution for {}".format(period))
    
    show(create_heatmap(agg_df, 'year'))
    show(create_timeseries(agg_df, 'year'))
    
    title_dist = compute_prevalence(df,['topic_id', 'title', 'year', 'topic_words'])
    show(create_bargraph(title_dist))
    
    for topic_id in title_dist.topic_id.unique():
        words = title_dist.loc[title_dist['topic_id'] == topic_id, 'topic_words'].iloc[0]
        print("Topic {}: {}".format(topic_id, words))