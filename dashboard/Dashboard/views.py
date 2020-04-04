import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from Dashboard.utils import get_analytics_dict, get_top_tweets, init_jobs


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app = dash.Dash(__name__,
                     external_stylesheets=external_stylesheets)
server = dash_app.server

dash_app.layout = html.Div([

    html.H1("Twitter Scrapper with Dash !", style={"text-align":"center"}),

    html.Div(
        [
            dcc.Input(
                placeholder="Enter queries separated by a comma",
                id="query-input",
                style={"width":"60%"},
                ),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(id='dummy'),
            
        ]
        , style={"text-align":"center", "width":"100%", "columnCount":2}),
    

    html.Table(
        [
            html.Thead(
                html.Tr(
                    [html.Th("No. of Tweets"),
                     html.Th("No. of Likes"),
                     html.Th("No. of Retweets"), ]
                )
            ),

            html.Tbody([
                html.Th(0),
                html.Th(0),
                html.Th(0),
            ], id="count-table")
        ], style={"width": "100%"}
    ),

    html.H2("Hashtags and Mentions", style={"text-align": "center"}),

    dcc.Graph(id="hashtags-mentions-graph"),

    html.H2("Top Countries", style={"text-align": "center"}),

    html.Hr(),
    dcc.Graph(id="country-graph"),
    html.Hr(),

    html.H2("Top retweeted", style={"text-align":"center"}),

    html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("User handler"),
                        html.Th("Retweet"),
                        html.Th("Likes"),
                        html.Th("Text") 
                     ]
                )
            ),

            html.Tbody([
                html.Th(0),
                html.Th(0),
                html.Th(0),
                html.Th(0),
            ], id="tweets-table")
        ], style={"width": "100%"}
    ),


    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    ),

    dcc.Interval(
        id='retweets-interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
])


# ------------------------------- CALLBACKS ---------------------------------------- #

@dash_app.callback(Output("dummy", "children"), [Input("submit-button", "n_clicks")], [State("query-input", "value")])
def new_search(n_clicks, query):
    if not query:
        return "Please enter a query string, you can add multiple queries separated by a comma"
    query = query.split(",")
    query = list(map(lambda x: x.strip(), query))
    print(f"got a query{query}")
    init_jobs(query)
    return f"Dashboard started working on {query}..."



@dash_app.callback(Output('count-table', 'children'),
                   [Input('interval-component', 'n_intervals')])
def update_table(n):
    analytics = get_analytics_dict()
    return [
        html.Th(analytics['total_tweets'], style={"color": "#3366ff"}),
        html.Th(analytics['total_likes'], style={"color": "#ff0066"}),
        html.Th(analytics['total_retweets'], style={"color": "#009900"}),
    ]

@dash_app.callback(Output('hashtags-mentions-graph', 'figure'),
                   [Input('interval-component', 'n_intervals')])
def update_hashtags_mentions_graph(n):
    analytics = get_analytics_dict()
    hashtags = {"x": [], "y": []}
    for hashtag, count in analytics['hashtags']:
        hashtags['x'].append(hashtag)
        hashtags['y'].append(count)

    mentions = {"x": [], "y": []}
    for mention, count in analytics['mentions']:
        mentions['x'].append(mention)
        mentions['y'].append(count)

    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "Hashtags Count", "Mentions Count"))

    fig.add_trace(

        go.Bar(y=hashtags['x'], x=hashtags['y'], orientation='h'),
        row=1, col=1
    )

    fig.add_trace(

        go.Bar(y=mentions['x'], x=mentions['y'], orientation='h'),
        row=1, col=2
    )

    fig.update_layout(showlegend=False)

    return fig

@dash_app.callback(Output('country-graph', 'figure'),
                   [Input('interval-component', 'n_intervals')])
def update_contry_graph(n):
    analytics = get_analytics_dict().get('countries', None)
    if analytics:
        fig = go.Figure(go.Bar(
            x=[i[0]for i in analytics], 
            y=[i[1] for i in analytics]))
    else:
        fig = go.Figure(go.Bar(x=[], y=[], ))
    return fig


@dash_app.callback(Output('tweets-table', 'children'),
                   [Input('retweets-interval-component', 'n_intervals')])
def update_tweets_table(n):
    top_tweets = get_top_tweets()
    tweets_table = []
    for tweet in top_tweets:
        tweets_table.append(
            html.Tr([
                html.Th("@"+tweet.username, style={"color": "#3366ff"}),
                html.Th(tweet.retweets, style={"color": "#009900"}),
                html.Th(tweet.likes , style={"color": "#ff0066"}),
                html.Th(tweet.text , style={"text-align": "center"}),
                ]))
    return tweets_table
