import dash
dash.register_page(__name__, order=2)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash import dcc, html, callback
from dash.dependencies import Output, Input

# Plotly theme
import plotly.io as pio
pio.templates.default = "plotly_white"

# Dataframe
from pages.df.df_communities import df_pr_committers


# layout of second (community) tab ******************************************
layout = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4('Number of Unique Committers Over Time',
                            className = 'title_text',
                            style={"text-align": "center"}),
                    dcc.Graph(id='c_graph2', figure={})
                ], width=20),
                dbc.Col([
                    html.H4('Selected Repo breakdown In Committers',
                            className = 'title_text',
                            style={"text-align": "center"}),
                    dcc.Graph(id='breakdown_commit', figure={})
                ], width=20),
            ]),
            dcc.Markdown('''
                #### Communities Metrics:
                Communities metrics are the display of the # unique committers by org by month over time.
                By clicking on different repos, a detailed breakdown table will show where the committers are from 
                and whether they are affiliated to a company or they are self contributors. Number in 
                *green* indicates a growth in commits for the contributor,
                number in *red* indicates a decline in commits for the contributor.

            ''')
        ])
    ],
    color="light",
)

#----------------------Call backs-------------------

@callback(
    Output(component_id="c_graph2", component_property="figure"),
    [Input(component_id='select_org', component_property='value')]
)

def update_graph(select_org):

    dff = df_pr_committers[df_pr_committers['rg_name'] == select_org]

    barchart=px.bar(
        data_frame=dff,
        x="yearmonth",
        y="num_of_unique_commit",
        color="repo_name",
        text="repo_name"
    )

    return (barchart)


#--------------------breakdown graph-------------------
@callback(
Output(component_id='breakdown_commit', component_property='figure'),
Input(component_id='c_graph2', component_property='hoverData'),
Input(component_id='c_graph2', component_property='clickData'),
Input(component_id='c_graph2', component_property='selectedData'),
Input(component_id='select_org', component_property='value')
)

def update_side_graph(hov_data, clk_data, slct_data, select_org):

    # Set kubernetes org, kubernetes repo as the default display
    if clk_data is None:
        df_org = df_pr_committers[df_pr_committers['rg_name'] == 'kubernetes']
        df_repo = df_org[df_org['repo_name'] == 'kubernetes']
        sub_frame = df_repo[["rg_name", "repo_name", 'yearmonth', 'cmt_committer_name', 'cntrb_company', 'cntrb_location', 'num_of_commit']]
        
        # create a pivot table to display the dataframe by committer
        pvt_table = pd.pivot_table(sub_frame, values='num_of_commit',
                                index=['cmt_committer_name', 'cntrb_company', 'cntrb_location'],
                            columns=['yearmonth'], aggfunc=np.sum)

        pvt_table = pvt_table.fillna(0)
        pvt_table = pvt_table.reset_index().rename(columns={'2022-1':'Jan', '2022-2':'Feb', '2022-3':'Mar',
                                                    '2022-4':'Apr', '2022-5':'May', '2022-6':'Jun',
                                                    '2022-7':'Jul'})
        pvt_table = pvt_table.sort_values(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'], ascending=False)


        table_fig = go.Figure(data=[go.Table(
                columnwidth = [30,30,30],
                header=dict(values=["Contributor Name",
                    "Contributor Company",
                    "Contributor Location",
                    "Jan","Feb","Mar","Apr","May","Jun","Jul"],
                line_color='darkslategray',
                align='center',
                font=dict(color='black', family="verdana", size=12),
                height=30
                ),
            cells = dict(values=[pvt_table.cmt_committer_name,
                                pvt_table.cntrb_company,
                                pvt_table.cntrb_location,
                                pvt_table.Jan,
                                pvt_table.Feb,
                                pvt_table.Mar,
                                pvt_table.Apr,
                                pvt_table.May,
                                pvt_table.Jun,
                                pvt_table.Jul],
                    line_color='darkslategray',
                    align='left',
                    font_color=[
                        'darkslategray',
                        'darkslategray',
                        'darkslategray',
                        'darkslategray',
                        # for every month, if the value for next month is greater than the previous
                        # month, then mark it with green; if it is smaller than the previous month,
                        # then mark it with red. Black if it stays the same.
                        ['green' if row['Feb'] > row['Jan']
                        else "red" if row['Feb'] < row['Jan']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Mar'] > row['Feb']
                        else "red" if row['Mar'] < row['Feb']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Apr'] > row['Mar']
                        else "red" if row['Apr'] < row['Mar']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['May'] > row['Apr']
                        else "red" if row['May'] < row['Apr']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Jun'] > row['May']
                        else "red" if row['Jun'] < row['May']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Jul'] > row['Jun']
                        else "red" if row['Jul'] < row['Jun']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ],
                    height=30
                    ))
                ])

        table_fig.update_layout(title= 'kubernetes')

        return table_fig

    else:
        clk_repo = clk_data['points'][0]['text']
        df_org = df_pr_committers[df_pr_committers['rg_name'] == select_org]
        df_repo = df_org[df_org['repo_name'] == clk_repo]
        sub_frame = df_repo[["rg_name", "repo_name", 'yearmonth', 'cmt_committer_name', 'cntrb_company', 'cntrb_location', 'num_of_commit']]
        pvt_table = pd.pivot_table(sub_frame, values='num_of_commit',
                                index=['cmt_committer_name', 'cntrb_company', 'cntrb_location'],
                            columns=['yearmonth'], aggfunc=np.sum)
        pvt_table = pvt_table.fillna(0)
        pvt_table = pvt_table.reset_index().rename(columns={'2022-1':'Jan', '2022-2':'Feb', '2022-3':'Mar',
                                                    '2022-4':'Apr', '2022-5':'May', '2022-6':'Jun',
                                                    '2022-7':'Jul'})
        pvt_table = pvt_table.sort_values(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'], ascending=False)

        table_fig = go.Figure(data=[go.Table(
                columnwidth = [30,30,30],
                header=dict(values=["Contributor Name",
                    "Contributor Company",
                    "Contributor Location",
                    "Jan","Feb","Mar","Apr","May","Jun","Jul"],
                line_color='darkslategray',
                align='center',
                font=dict(color='black', family="Lato", size=15),
                height=30
                ),
            cells=dict(values=[pvt_table.cmt_committer_name,
                                pvt_table.cntrb_company,
                                pvt_table.cntrb_location,
                                pvt_table.Jan,
                                pvt_table.Feb,
                                pvt_table.Mar,
                                pvt_table.Apr,
                                pvt_table.May,
                                pvt_table.Jun,
                                pvt_table.Jul],
                    line_color='darkslategray',
                    align='left',
                    font_color=[
                        'darkslategray',
                        'darkslategray',
                        'darkslategray',
                        'darkslategray',
                        # for every month, if the value for next month is greater than the previous
                        # month, then mark it with green; if it is smaller than the previous month,
                        # then mark it with red. Black if it stays the same.
                        ['green' if row['Feb'] >row['Jan']
                        else "red" if row['Feb'] < row['Jan']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Mar'] >row['Feb']
                        else "red" if row['Mar'] < row['Feb']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Apr'] >row['Mar']
                        else "red" if row['Apr'] < row['Mar']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['May'] >row['Apr']
                        else "red" if row['May'] < row['Apr']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Jun'] >row['May']
                        else "red" if row['Jun'] < row['May']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ['green' if row['Jul'] >row['Jun']
                        else "red" if row['Jul'] < row['Jun']
                        else 'darkslategray'
                        for index,row in pvt_table.iterrows()
                        ],
                        ],
                    height=30
                    ))
                ])

        table_fig.update_layout(title=f'{clk_repo}')

        return table_fig