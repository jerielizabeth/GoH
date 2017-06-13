import gensim
import json
import os
import pandas as pd
# from sklearn import preprocessing


def process_period(base_dir, period, num_topics=30, iterations=50, passes=8):
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


def doc_list(index_filename):
    with open(index_filename) as data_file:    
        data = json.load(data_file)
    docs = pd.DataFrame.from_dict(data, orient='index').reset_index()
    docs.columns = ['index_pos', 'doc_id']
    docs['index_pos'] = docs['index_pos'].astype(int)
  
    return docs


def doc_topic(lda_model, corpus):
    """
    """
    doc_topics = []
    i = 0
    for doc in corpus:
        topics = lda_model.get_document_topics(corpus[i])
        for topic in topics:
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
        words_list = lda_model.show_topic(i, topn=4)
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


def compile_dataframe(index_filename, model_file, metadata_filename, corpus_file):
    """
    """
    corpus = gensim.corpora.MmCorpus(corpus_file)
    lda_model = gensim.models.LdaModel.load(model_file)
    
    docs = doc_list(index_filename)
    metadata = doc_metadata(metadata_filename)
    doc2topics = doc_topic(lda_model, corpus)
    topics = topic_words(lda_model)

    doc2metadata = docs.merge(metadata, on='doc_id')
    topics_expanded = doc2topics.merge(topics, on='topic_id')
    
    df = topics_expanded.merge(doc2metadata, on="index_pos", how="left")
    
    return df


# def compute_topic_distribution():

