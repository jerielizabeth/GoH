from bokeh.charts import Bar, HeatMap, TimeSeries, show, output_file
from bokeh.models import HoverTool, BoxZoomTool, Legend, ResetTool, SaveTool
from bokeh.palettes import viridis, d3
import seaborn as sns
import matplotlib.pyplot as plt


# Visualization Functions
def create_heatmap(df, x_axis, y_axis, values):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("weight", "@{}".format(values))
            ]
        )

    p = HeatMap(df, 
                   x=x_axis, 
                   y=y_axis, 
                   values=values,
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


def create_timeseries(df, x_axis, y_axis, model, colors=30):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "($x{int}, $y)"),
            ("topic_words", "@topic_words")
            ]
        )
    legend = Legend(location=(0, -30))
    p = TimeSeries(df, 
                   x=x_axis,
                   y=y_axis, 
                   legend=False,
                   ylabel='Proportion of Total Topic Weights per Topic ID for {}'.format(model),
                   color="topic_words",
                   palette=viridis(colors), 
                   tools=[hover, BoxZoomTool(), ResetTool(), SaveTool()]
                  )
    # p.xaxis.minor_tick_line_color = None
    p.add_layout(legend, 'right')

    return p


def create_bargraph(df, x_axis, y_axis):
    """
    """
    hover = HoverTool(
        tooltips=[
            ("title", "@topic_words")
            ]
        )

    p = Bar(df, 
            label=x_axis, 
            values=y_axis, 
            stack='topic_words', 
            legend=False, 
            tools=[hover], 
            plot_width=600,
            palette=d3['Category20'][20]
           )
    
    return p  


def create_regression_plot(df, yaxis):
  """
  Uses a lowess smoother to fit a nonparametric regression.
  Use with the normalized weights: tracing the pattern of the proportion
  of the topic per year.
  Pass in the results of `modeldata.topic_series()`
  """
  return sns.lmplot(x="year", y=yaxis, row="topic_words", data=df, lowess=True, size=2.5, aspect=3.5)

def create_facet_bargraph(df):
  """
  Uses FacetGrid to split by topic.
  Pass in the results of `modeldata.topic_series()`
  """
  g = sns.FacetGrid(df, row="topic_words", size=2.5, aspect=3.5)
  return g.map_dataframe(sns.barplot, x='year', y='normalized_weight')


## Composit Function
# def visualize_models(df, period, filter_df=False):
#     """
#     """
#     if filter_df is True:
#         end_year = int(period[0].split('-')[-1])
#         start_year = int(period[1])

#         df = filter_dataframe_by_dates(df, start_year, end_year)

#     # df = normalize_df(df)
            
#     agg_df = compute_prevalence(df, ['year', 'topic_id'])
#     keys = topicID_to_words(df)
#     merged = pd.merge(agg_df, keys, how='left', on='topic_id')
#     # print(merged)
#     print("\nTopic Distribution for {}".format(period))
    
#     show(create_heatmap(merged, 'year'))
#     show(create_timeseries(merged, 'year'))
    
    
#     title_dist = compute_prevalence(df,['title', 'topic_id',])
#     merged = pd.merge(title_dist, keys, how='left', on='topic_id')
#     show(create_bargraph(merged))
    
#     for topic_id in keys.index.values:
#         words = df.loc[df['topic_id'] == topic_id, 'topic_words'].iloc[0]
#         print("Topic {}: {}".format(topic_id, words))


