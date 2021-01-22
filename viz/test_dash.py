import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.io as pio
import plotly.express as px

from dash.dependencies import Input,Output

# Data prep
pio.templates.default = "plotly_white"
summary = pd.read_pickle("data/summary_data.pkl")
summary["activity_year"] = summary["starttime"].dt.year.astype(str)
summary = summary[summary["distance"]<500] # remove outliers
activities = summary.head(10)["activityid"]

# app initialization
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])

## Layout definition
app.layout = html.Div([
    html.H1("Sport activities explorer"),
    dcc.Tabs(id="tabs",value="tab-1",children=[
        dcc.Tab(label="Activities summary",value="tab-1"),
        dcc.Tab(label="Activities detail",value="tab-2")
    ]),
    html.Div(id='tabs-content')
])

@app.callback(
    Output("tabs-content",'children'),
    Input("tabs","value"))
def render_tabs(tab):
    tab_sum = html.Div([
        dbc.Row(dbc.Col(html.Div("Summary of all activities"))),
        dbc.Row([
            dbc.Col(width=3,children=html.Div(children=[
                html.H3("User inputs"),
                "Chose starting year",
                dcc.Slider(id="choice-year",
                    min = summary['starttime'].dt.year.min(),
                    max = summary['starttime'].dt.year.max(),
                    value=2012,
                    marks = {str(year): str(year) for year in range(summary['starttime'].dt.year.min(),
                                                                    summary['starttime'].dt.year.max()+1,2)}),
                "Chose X axis metric",
                dcc.Dropdown(id="x-axis",options=[
                    {"label":var,"value":var} for var in summary.columns
                ],
                    value="distance"),
                "Chose Y axis metric",
                dcc.Dropdown(id="y-axis",options=[
                    {"label":var,"value":var} for var in summary.columns
                ],
                    value="averagespeed"),
                "Logarithmic scale",
                dcc.Checklist(id="log_scale",options=[{"label":" For X  ","value":"yes_x"},
                                                  {"label":" For Y  ","value":"yes_y"}],
                              value=[]),
            ])),
            dbc.Col(width=9,children=html.Div(children=[
                html.H3("Graphics"),
                html.H4("Repartition of activities per sport"),
                dcc.Graph("bars-intro"),
                html.H4("Metrics comparison"),
                dcc.Graph("gr-summary")
            ]))
        ])
    ])
    tab_detail = html.Div([
        html.H3("Titi")
    ])
    if tab=="tab-1": return tab_sum
    else: return tab_detail

@app.callback(
    Output("bars-intro","figure"),
    Input("choice-year","value"))
def update_bar_intro(year):
    bars = summary.loc[summary["starttime"].dt.year>=int(year),["type",'activity_year']].value_counts().reset_index(name="count")
    intro_graph = px.bar(bars,y="type",x="count",orientation="h",
        color="activity_year",
        labels={"count":"Sport","type":"Number","activity_year":"Year"})
    return intro_graph

@app.callback(
    Output('gr-summary', 'figure'),
    Input('choice-year', 'value'),
    Input('x-axis','value'),
    Input("y-axis","value"),
    Input("log_scale","value"))
def update_scatter_summary(year,x_var,y_var,log):
    dd = summary[summary["starttime"].dt.year>=int(year)]
    fig = px.scatter(dd,x="distance",y=y_var,color="type",
                    log_x=True if "yes_x" in log else False,
                    log_y=True if "yes_y" in log else False
                    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)  