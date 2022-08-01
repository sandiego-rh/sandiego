import dash

dash.register_page(__name__, order=1, path='/')

import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Output, Input, State

# Plotly theme
import plotly.io as pio
pio.templates.default = "plotly_white"

# Dataframe
from pages.df.df_activities import dframe_perc, breakdown_frame


# layout of first (activity) tab ******************************************
layout = dbc.Card(
    [
        dbc.CardBody(
            [
            dbc.Row([
                dbc.Col([
                    html.H4('Density within an Organization',
                            className = 'title_text',
                            style={"text-align": "center"}),
                    dcc.Graph(id='scatter', figure={}, clickData=None, hoverData=None,
                    config={
                        'staticPlot': False,
                        'scrollZoom': True,
                        'doubleClick': 'reset',
                        'showTips': True
                    })
                ], width=6),
                dbc.Col([
                    html.H4('Selected Repo Breakdown in Activities By Time',
                            className = 'title_text',
                            style={"text-align": "center"}),
                    dcc.Graph(id='breakdown', figure={})
                ], width=6),
            dcc.Markdown('''
                #### Activities Metrics:
                Activities metrics are the metrics for activiness within each repo. Activities are calculated based on:
                
                weighted increment in star = 0.01,
                weighted increment in watcher = 0.1,
                weighted increment in fork = 0.2,
                weighted increment in issue = 0.5,
                weighted increment in Pull Request = 1,
                weighted increment in open Pull Request = 1.2,
                weighted increment in commit = 1.3,
                weighted increment in closed Pull Request = 1.5,
                weighted increment in committers = 1.6,
                weighted increment in merged Pull Request = 1.8

            ''')
            ])
        ])
    ],
    color="light",
)

#-------------------------------------------------------------------------building graph

@callback(
    Output(component_id="scatter", component_property="figure"),
    [Input(component_id='select_org', component_property='value')]
)

def update_graph(select_org):

    dframe_org = dframe_perc[dframe_perc['org'] == select_org]
    barchart=px.bar(
        data_frame=dframe_org,
        x="org",
        y="percentage",
        color="repo_name",
        text="repo_name"
    )

    return (barchart)


#---------------------------------Breakdown chart for repo activities-------------------------------
@callback(
    Output(component_id='breakdown', component_property='figure'),
    Input(component_id='scatter', component_property='clickData'),
    Input(component_id='select_org', component_property='value')
)


def update_side_graph(clk_data, select_org):
    if clk_data is None:

        # Set kubernetes org, kubernetes repo as the default display
        df_org = breakdown_frame[breakdown_frame["rg_name"] == "kubernetes"]
        df_repo = (
            df_org[df_org["repo_name"] == "kubernetes"].groupby(["rg_name", "repo_name", "yearmonth"]).sum().reset_index()
        )
        breakdown_fig = go.Figure(
            data=[
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["committer_increment"],
                    name="Increase in committer",
                    marker_color="indianred",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["pull_request_increment"],
                    name="Increase in PR",
                    marker_color="lime"
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["open_pull_request_increment"],
                    name="Increase in open PR",
                    marker_color="aqua",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["closed_pull_request_increment"],
                    name="Increase in closed PR",
                    marker_color="cornflowerblue",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["merged_pull_request_increment"],
                    name="Increase in merged PR",
                    marker_color="RoyalBlue",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["issue_increment"],
                    name="Increase in issue",
                    marker_color="lightsalmon"
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["star_increment"],
                    name="Increase in star",
                    marker_color="aliceblue"
                ),
                go.Bar(x=df_repo["yearmonth"],
                y=df_repo["fork_increment"],
                name="Increase in fork",
                marker_color="cornsilk"
                ),
            ]
        )

        return breakdown_fig

    else:

        clk_repo = clk_data["points"][0]["text"]
        df_org = breakdown_frame[breakdown_frame["rg_name"] == select_org]
        df_repo = df_org[df_org["repo_name"] == clk_repo].groupby(["rg_name", "repo_name", "yearmonth"]).sum().reset_index()
        breakdown_fig = go.Figure(
            data=[
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["committer_increment"],
                    name="Increase in committer",
                    marker_color="indianred",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["pull_request_increment"],
                    name="Increase in PR",
                    marker_color="lime"
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["open_pull_request_increment"],
                    name="Increase in open PR",
                    marker_color="aqua",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["closed_pull_request_increment"],
                    name="Increase in closed PR",
                    marker_color="cornflowerblue",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["merged_pull_request_increment"],
                    name="Increase in merged PR",
                    marker_color="RoyalBlue",
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["issue_increment"],
                    name="Increase in issue",
                    marker_color="lightsalmon"
                ),
                go.Bar(
                    x=df_repo["yearmonth"],
                    y=df_repo["star_increment"],
                    name="Increase in star",
                    marker_color="aliceblue"
                ),
                go.Bar(x=df_repo["yearmonth"],
                y=df_repo["fork_increment"],
                name="Increase in fork",
                marker_color="cornsilk"),
            ]
        )

        breakdown_fig.update_layout(title=f"{clk_repo}")

        return breakdown_fig