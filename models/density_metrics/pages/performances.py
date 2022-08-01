import dash
dash.register_page(__name__, order=3)

from pandas import value_counts
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Output, Input

# Plotly theme
import plotly.io as pio
pio.templates.default = "plotly_white"

# Dataframe
from pages.df.df_performances import dframe_issue, dframe_pr


# layout of thrid (performance) tab ******************************************
layout = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4('PR Performance within an Organization',
                            className = 'title_text',
                            style={"text-align": "center"}),
                dcc.Graph(id='p_graph1', figure={})
                ], width=6),
            dbc.Col([
                    html.H4('Issue Performance within an Organization',
                            className = 'title_text',
                            style={"text-align": "center"}),
                dcc.Graph(id='p_graph2', figure={})
            ], width=6),
            dbc.Col([
                    html.H4('Selected on a repo to see the breakdown of PR performance',
                            className = 'title_text',
                            style={"text-align": "center"}),
                dcc.Graph(id='breakdown_performance', figure={})
            ], width=6),
            dbc.Col([
                    html.H4('Selected on a repo to see the breakdown of issue performance',
                            className = 'title_text',
                            style={"text-align": "center"}),
                dcc.Graph(id='breakdown_performance2', figure={})
            ], width=6),
        ]),
        dcc.Markdown('''
            #### Performances Metrics:
            Performances metrics are the metrics for Pull Requests and Issue. Performances are calculated based on
            how fast the Pull Request/ Issue are closed. The faster a Pull Request/ Issue is closed, the higher weight
            it is within the calculation.

            Fast (closed within 30 days) = 1,
            Mild (closed within 60 days) = 0.66,
            Slow (closed within 90 days) = 0.33,
            Stale (closed more than 90 days) = 0.1

            PR/Issue opened within 45 days and are not yet closed are given 0.5, Hard-cap timeout = 365 days

            ''')
        ])
    ],
    color="light",
)

@callback(
    Output(component_id='p_graph1', component_property="figure"),
    Output(component_id="p_graph2", component_property="figure"),
    [Input(component_id='select_org', component_property='value')]
)

def update_graph(select_org):

    df_pr = dframe_pr.groupby(['rg_name', 'repo_name']).sum().reset_index()
    pr_final = df_pr[df_pr['rg_name'] == select_org].sort_values(by='total', ascending=False)[:10]
    
    df_issue = dframe_issue.groupby(['rg_name', 'repo_name']).sum().reset_index()
    issue_final = df_issue[df_issue['rg_name'] == select_org].sort_values(by='total', ascending=False)[:10]

    piechart_pr = px.pie(
        data_frame=pr_final,
        values='total',
        names='repo_name',
        hole=.25
    )
    piechart_pr.update_traces(textposition='inside', textinfo='percent+label')
    piechart_pr.update_layout(
    title_text="PR Performance",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='PR', x=0.5, y=0.5, font_size=20, showarrow=False)])

    piechart_issue=px.pie(
        data_frame=issue_final,
        values='total',
        names='repo_name',
        hole=.25
    )
    piechart_issue.update_traces(textposition='inside', textinfo='percent+label')
    piechart_issue.update_layout(
    title_text="Issue Performance",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='Issue', x=0.5, y=0.5, font_size=18, showarrow=False)])

    return (piechart_pr, piechart_issue)


#---------------------------------------sub graph for PR---------------------------------------

@callback(
    Output(component_id='breakdown_performance', component_property='figure'),
    Input(component_id='p_graph1', component_property='clickData'),
    Input(component_id='select_org', component_property='value')
)

def update_side_graph1(clk_data, select_org):
    if clk_data is None:
        df_org = dframe_pr[dframe_pr['rg_name'] == 'kubernetes']
        df_repo = df_org[df_org['repo_name'] == 'kubernetes'].groupby(['yearmonth', 'segment', 'color']).sum().reset_index()

        sub_piechart_pr = go.Figure(
                            data =[
                                go.Bar(
                                x = df_repo['yearmonth'].tolist(),
                                y = df_repo['num'].tolist(),
                                marker_color= df_repo['color'].tolist(),
                                text = df_repo['segment'].tolist()
                                )],
                            layout=dict(
                                title=dict(text = 'kubernetes')
                            )
        )

        return sub_piechart_pr
    
    else:
        print(f'click data: {clk_data}')
        clk_repo = clk_data['points'][0]['label']
        df_org = dframe_pr[dframe_pr['rg_name'] == select_org]
        df_repo = df_org[df_org['repo_name'] == clk_repo].groupby(['yearmonth', 'segment', 'color']).sum().reset_index()

        sub_piechart_pr = go.Figure(
                            data = [
                                go.Bar(
                                    x = df_repo['yearmonth'].tolist(),
                                    y = df_repo['num'].tolist(),
                                    marker_color= df_repo['color'].tolist(),
                                    text = df_repo['segment'].tolist()
                                )],
                            layout = dict(
                                title=f'{clk_repo}'
                            )
        )

        return sub_piechart_pr


#---------------------------------------sub graph for Issue---------------------------------------

@callback(
    Output(component_id='breakdown_performance2', component_property='figure'),
    Input(component_id='p_graph2', component_property='clickData'),
    Input(component_id='select_org', component_property='value')
)


def update_side_graph2(clk_data, select_org):
    if clk_data is None:
        df_org = dframe_issue[dframe_issue['rg_name'] == 'kubernetes']
        df_repo = df_org[df_org['repo_name'] == 'kubernetes'].groupby(['yearmonth', 'segment','color']).sum().reset_index()
        
        sub_piechart_issue = go.Figure(
                            data = [
                                go.Bar(
                                    x = df_repo['yearmonth'].tolist(),
                                    y = df_repo['num'].tolist(),
                                    marker_color= df_repo['color'].tolist(),
                                    text = df_repo['segment'].tolist()
                                )],
                            layout=dict(
                                title=dict(text = 'kubernetes')
                            )
        )

        return sub_piechart_issue
    
    else:
        print(f'click data: {clk_data}')
        clk_repo = clk_data['points'][0]['label']
        df_org = dframe_issue[dframe_issue['rg_name'] == select_org]
        df_repo = df_org[df_org['repo_name'] == clk_repo].groupby(['yearmonth', 'segment','color']).sum().reset_index()

        sub_piechart_issue = go.Figure(
                            data = [
                                go.Bar(
                                    x = df_repo['yearmonth'].tolist(),
                                    y = df_repo['num'].tolist(),
                                    marker_color= df_repo['color'].tolist(),
                                    text = df_repo['segment'].tolist()
                                )],
                            layout = dict(
                                title=f'{clk_repo}'
                            ) 
        )

        return sub_piechart_issue