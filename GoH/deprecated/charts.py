# -*- coding: utf-8 -*-

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def chart_error_rate_distribution( df, title ):
    
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
    
    # sort df by doc_id
    df = df.sort_values(by='doc_id')
    
    # graph the error_rate by the doc_id

    plt.plot(df['error_rate'])
    plt.title('Error rate by Title for {}'.format(title))
    plt.xlabel('Doc Id')
    plt.ylabel('Rate')
    return(plt)