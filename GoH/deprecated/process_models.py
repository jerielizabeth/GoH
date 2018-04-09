from bokeh.charts import Bar, HeatMap, TimeSeries, show, output_file
# from bokeh.io import output_notebook
from bokeh.models import HoverTool, BoxSelectTool, Legend
from bokeh.palettes import viridis, d3
import gensim
import logging
import json
import os
import pandas as pd
import re
from sklearn import preprocessing

## Model Creation
def process_period(base_dir, period, num_topics=30, iterations=50, passes=8, random_state=12):
    """
    """
    corpus = gensim.corpora.MmCorpus(os.path.join(base_dir, "{}.mm".format(period)))
    dictionary = gensim.corpora.Dictionary.load(os.path.join(base_dir, "{}.dict".format(period)))
    model = gensim.models.LdaModel(corpus, 
                                   num_topics=num_topics, 
                                   id2word=dictionary, 
                                   alpha='auto', 
                                   iterations=iterations, 
                                   passes=passes,
                                   random_state=random_state
                                  )                               
    return (model, corpus, dictionary)


## Create Dataframe from Models 
def queue_docs(base_dir, directory, corpus_file, model_scheme):
    """
    base_dir, directory, corpus_file, model_scheme
    """
    return (os.path.join(base_dir, 'corpora/{}/{}.txt'.format(directory, corpus_file)),
            os.path.join(base_dir, 'dataframes/{}/{}_dtm.csv'.format(directory, model_scheme)),
            os.path.join(base_dir, 'dataframes/{}/{}_topicLabels.csv'.format(directory, model_scheme)),
            os.path.join(base_dir,'2017-05-corpus-stats/2017-05-Composite-OCR-statistics.csv')
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
    logging.info("Getting topic to document matrix")
    logging.info("Applying model to documents...")
    
    dtm = lda_model[corpus]

    doc_topics = []
    i = 0
    for doc in dtm:
        if i % 1000 == 0:
            logging.info("Processing doc num {}".format(i))

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


def word_topic(lda_model, words=20):
    """
    """
    topicWordProbMat = lda_model.print_topics(num_topics=-1, num_words=words)
    wordTopic = []
    for topic in topicWordProbMat:
        topic_id = topic[0]
        wordWeights = topic[1].split('+')
        for pair in wordWeights:
            splitPair = pair.split('*')
            weight = float(splitPair[0])
            word =  re.sub(r'"', '', splitPair[1]).strip()
            wordTopic.append((topic_id, word, weight))
            
    return pd.DataFrame(wordTopic, columns=['topic_id', 'token', 'token_weight']) 


def doc_metadata(metadata_filename):
    """
    """
    data = pd.read_csv(metadata_filename, usecols=['doc_id', 'year','title'])
    return data


def save_dataframes(directory, out_dir, scheme, period, lda_model, corpus):
    """
    """
    
    topicLabels = topic_words(lda_model)
    topicLabels.to_csv(os.path.join(out_dir, '{}-{}_topicLabels.csv'.format(scheme, period)), index=False)
    
    dtm = doc_topic(lda_model, corpus)
    dtm.to_csv(os.path.join(out_dir, '{}-{}_dtm.csv'.format(scheme, period)), index=False)
    
    wtm = word_topic(lda_model)
    wtm.to_csv(os.path.join(out_dir, '{}-{}_wtm.csv'.format(scheme, period)), index=False)


def model_to_df(base_dir, directory, corpus_file, model_scheme):
    """
    base_dir, directory, corpus_file, model_scheme
    """
    docs = queue_docs(base_dir, directory, corpus_file, model_scheme)
    df = compile_dataframe(docs)
    
    return df


## Manipulate Dataframes
def filter_dataframe_by_dates(df, start_year, end_year):
    """
    """
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]

    return filtered_df

def normalize_df(df):
    """
    """
    # Reorient from long to wide
    dtm = df.pivot(index='index_pos', columns='topic_id', values='topic_weight').fillna(0)

    # Divide each value in a row by the sum of the row to normalize the values
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

def compute_prevalence_normalizer(df, groupby_fields):
    """
    base: ['topic_id', 'year', 'topic_words']
    """
    agg_df = df.groupby(groupby_fields)[['topic_weight']].sum().reset_index()
    min_max_scaler = preprocessing.MinMaxScaler()
    agg_df['normalized_weights'] = pd.Series(min_max_scaler.fit_transform(agg_df.topic_weight), 
                                               index=agg_df.index)
    
    return agg_df


def compute_prevalence_percentage(df, groupby_fields):
    """
    base: ['topic_id', 'year']
    """
    # agg_df = df.groupby(groupby_fields)['topic_weight'].sum().reset_index()
    # groupby_fields.append('topic_weight')
    # wide_df = agg_df[groupby_fields].copy().pivot(index=groupby_fields[0],columns=groupby_fields[1],values="topic_weight").fillna(0)
    # new_df = pd.DataFrame(index=wide_df.index.values)
    # for column in list(wide_df.columns.values):
    #     new_df[column] = (wide_df[column]/wide_df[column].sum())*100
    # long_df = new_df.unstack().reset_index() 
    # merged_df = pd.merge(agg_df, 
    #                      long_df,  
    #                      how='left', 
    #                      left_on=[groupby_fields[0],groupby_fields[1]], 
    #                      right_on = ['level_1','level_0'])
    # merged_df.rename(columns = {0:'normalized_weights'}, inplace = True)
    # merged_df.drop(['level_0','level_1'], axis=1, inplace=True)

    pdf = df.groupby(groupby_fields).agg({'norm_topic_weight': 'sum'})

    pdf2 = pdf.groupby(level=0).apply(lambda x: x / x.sum()).reset_index()
    groupby_fields.append('proportional_weight')
    pdf2.columns = groupby_fields
    
    pdf2 = pdf2.merge(labels, on=groupby_fields[1])
    
    return merged_df


def compute_prevalence(df, groupby_fields):
    """
    base: ['year', 'topic_id']
    """
    # Get number of docs per year
    total_docs = df.groupby(groupby_fields[0])['doc_id'].apply(lambda x: len(x.unique())).reset_index()
    total_docs.columns = [groupby_fields[0], 'total_docs']

    # Group by year and topic id
    df_avg = df.groupby([groupby_fields[0], groupby_fields[1]]).agg({'norm_topic_weight': 'sum'}).reset_index()

    # Merge dataframes
    df_avg = df_avg.merge(total_docs, on=groupby_fields[0], how="left")

    # Compute the mean per topic
    df_avg['proportional_weight'] = df_avg['norm_topic_weight'] / df_avg['total_docs']

    # Merge the dataframes
    # df_avg = df_avg.merge(labels, on='topic_id')

    # pdf = df.groupby(groupby_fields).agg({'norm_topic_weight': 'sum'})

    # pdf2 = pdf.groupby(level=0).apply(lambda x: x / x.sum()).reset_index()
    # groupby_fields.append('proportional_weight')
    # pdf2.columns = groupby_fields

    return df_avg


def topicID_to_words(df):
    new_df = {}
    for topic_id in df.topic_id.unique():
        words = df.loc[df['topic_id'] == topic_id, 'topic_words'].iloc[0]
        new_df[topic_id] = words

    return pd.DataFrame(list(new_df.items()),columns=['topic_id','topic_words'])


# Visualization Functions
def create_heatmap(df, x_axis):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("weight", "@proportional_weight")
            ]
        )

    p = HeatMap(df, 
                   x=x_axis, 
                   y='topic_words', 
                   values='proportional_weight',
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
                   y="proportional_weight", 
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
            ("title", "@topic_words")
            ]
        )

    p = Bar(df, 
            label='title', 
            values='proportional_weight', 
            stack='topic_words', 
            legend=False, 
            tools=[hover], 
            plot_width=600,
            palette=d3['Category20'][20]
           )
    
    return p    

## Composit Function
def visualize_models(df, period, filter_df=False):
    """
    """
    if filter_df is True:
        end_year = int(period[0].split('-')[-1])
        start_year = int(period[1])

        df = filter_dataframe_by_dates(df, start_year, end_year)

    # df = normalize_df(df)
            
    agg_df = compute_prevalence(df, ['year', 'topic_id'])
    keys = topicID_to_words(df)
    merged = pd.merge(agg_df, keys, how='left', on='topic_id')
    # print(merged)
    print("\nTopic Distribution for {}".format(period))
    
    show(create_heatmap(merged, 'year'))
    show(create_timeseries(merged, 'year'))
    
    
    title_dist = compute_prevalence(df,['title', 'topic_id',])
    merged = pd.merge(title_dist, keys, how='left', on='topic_id')
    show(create_bargraph(merged))
    
    for topic_id in keys.index.values:
        words = df.loc[df['topic_id'] == topic_id, 'topic_words'].iloc[0]
        print("Topic {}: {}".format(topic_id, words))