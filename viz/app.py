import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.io as pio
import plotly.express as px

from dash.dependencies import Input,Output

def subset_data(indoor):
    if indoor=="no": dd = summary[summary["is_indoor"]==False]
    else: dd = summary
    return dd

# Data prep
pio.templates.default = "plotly_white"
summary = pd.read_pickle("data/summary_data.pkl")
summary["activity_year"] = summary["starttime"].dt.year.astype(str)
## remove outliers
summary = summary[(summary["distance"]<500) & (summary["elevationgain"]<10000)] 
activities = summary.head(10)["activityid"]

# app initialization
app = dash.Dash(external_stylesheets=[dbc.themes.SPACELAB],
                suppress_callback_exceptions=True)

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
        dbc.Row(dbc.Col(html.Div(html.H2("Summary of all activities")))),
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
                "Include virtual/indoor activities",
                dcc.RadioItems(id="choice-indoor",options=[{"label":"Yes","value":"yes"},
                                                           {"label":"No","value":"no"}],
                                value="yes"),
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
                dcc.Graph("gr-summary"),
                html.H4("Starting points"),
                dcc.Graph("map-intro")
            ]))
        ])
    ])
    tab_detail = html.Div([
        dbc.Row(dbc.Col(html.Div(html.H2("Individual activity explorer")))),
        dbc.Row([
            dbc.Col(width=3,children=html.Div(children=[
                html.H4("Chose the activity"),
                dcc.Dropdown(id="choice-act",options=[
                    {"label":act,"value":act} for act in activities
                ],value=activities[0]),
                html.H4("Color variable for the map"),
                dcc.Dropdown(id="choice-color-map",options=[
                    {"label":var,"value":var} for var in ["speed","altitudemeters"]
                ],value="altitudemeters"),
                html.H4("Metric for the first graph"),
                dcc.Dropdown(id="choice-metric1",options=[
                    {"label":var,"value":var} for var in ["speed","altitudemeters","watts","cadence","heartratebpm"]
                ],value="speed"),
                html.H4("Metric for the second graph"),
                dcc.Dropdown(id="choice-metric2",options=[
                    {"label":var,"value":var} for var in ["speed","altitudemeters","watts","cadence","heartratebpm"]
                ],value="heartratebpm")
            ])),
            dbc.Col(width=9,children=html.Div([
                html.H4("Activity map"),
                dcc.Graph("map-act"),
                html.H4("First metric"),
                dcc.Graph("plot1-act"),
                html.H4("Second metric"),
                dcc.Graph("plot2-act")
            ]))
        ])
    ])
    if tab=="tab-1": return tab_sum
    else: return tab_detail

## Summary tab
# summary barchart
@app.callback(
    Output("bars-intro","figure"),
    Input("choice-year","value"),
    Input("choice-indoor","value"))
def update_bar_intro(year,indoor):
    dd = subset_data(indoor)
    bars = dd.loc[dd["starttime"].dt.year>=int(year),["type",'activity_year']].value_counts().reset_index(name="count")
    intro_graph = px.bar(bars,y="type",x="count",orientation="h",
        color="activity_year",
        labels={"count":"Sport","type":"Number","activity_year":"Year"})
    return intro_graph
# summary scatter plot
@app.callback(
    Output('gr-summary', 'figure'),
    Input('choice-year', 'value'),
    Input("choice-indoor","value"),
    Input('x-axis','value'),
    Input("y-axis","value"),
    Input("log_scale","value"))
def update_scatter_summary(year,indoor,x_var,y_var,log):
    dd = subset_data(indoor)
    dd = dd[dd["starttime"].dt.year>=int(year)]
    fig = px.scatter(dd,x=x_var,y=y_var,color="type",hover_name="activityid",
                    log_x=True if "yes_x" in log else False,
                    log_y=True if "yes_y" in log else False
                    )
    return fig
#Map with all starting points
@app.callback(
    Output("map-intro","figure"),
    Input("choice-year","value"),
    Input("choice-indoor","value"))
def update_map_summary(year,indoor):
    dd = subset_data(indoor)
    dd = dd[dd["starttime"].dt.year>=int(year)]
    fig = px.scatter_mapbox(dd,lat="startlatitude",lon="startlongitude",color="type",
                            mapbox_style="open-street-map",zoom=3)
    return fig


## Details tab
# graph1
@app.callback(
    Output("plot1-act","figure"),
    Input("choice-act","value"),
    Input("choice-metric1","value")
)
def update_map_act(act_id,metric):
    dd = pd.read_pickle("data/"+act_id+".pkl")
    fig = px.line(dd,x="time",y=metric)
    return fig
# graph2
@app.callback(
    Output("plot2-act","figure"),
    Input("choice-act","value"),
    Input("choice-metric2","value")
)
def update_map_act(act_id,metric):
    dd = pd.read_pickle("data/"+act_id+".pkl")
    fig = px.line(dd,x="time",y=metric)
    return fig
# activity map
@app.callback(
    Output("map-act","figure"),
    Input("choice-act","value"),
    Input("choice-color-map","value")
)
def update_map_act(act_id,color_var):
    dd = pd.read_pickle("data/"+act_id+".pkl")
    fig = px.scatter_mapbox(dd,lon="longitudedegrees",lat="latitudedegrees",color=color_var,
                        zoom=11,mapbox_style="open-street-map")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)  