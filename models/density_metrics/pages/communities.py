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

    barchart2=px.bar(
        data_frame=dff,
        x="yearmonth",
        y="num_of_unique_commit",
        color="repo_name",
        text="repo_name"
    )

    return (barchart2)


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
        dff2 = df_pr_committers[df_pr_committers['rg_name'] == 'kubernetes']
        dff2 = dff2[dff2['repo_name'] == 'kubernetes']
        sub_frame = dff2[["rg_name", "repo_name", 'yearmonth', 'cmt_committer_name', 'cntrb_company', 'cntrb_location', 'num_of_commit']]
        
        # create a pivot table to display the dataframe by committer
        table = pd.pivot_table(sub_frame, values='num_of_commit',
                                index=['cmt_committer_name', 'cntrb_company', 'cntrb_location'],
                            columns=['yearmonth'], aggfunc=np.sum)

        table = table.fillna(0)
        table = table.reset_index().rename(columns={'2022-1':'Jan', '2022-2':'Feb', '2022-3':'Mar',
                                                    '2022-4':'Apr', '2022-5':'May', '2022-6':'Jun',
                                                    '2022-7':'Jul'})
        table = table.sort_values(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'], ascending=False)


        fig = go.Figure(data=[go.Table(
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
            cells = dict(values=[table.cmt_committer_name,
                                table.cntrb_company,
                                table.cntrb_location,
                                table.Jan,
                                table.Feb,
                                table.Mar,
                                table.Apr,
                                table.May,
                                table.Jun,
                                table.Jul],
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
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Mar'] > row['Feb']
                        else "red" if row['Mar'] < row['Feb']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Apr'] > row['Mar']
                        else "red" if row['Apr'] < row['Mar']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['May'] > row['Apr']
                        else "red" if row['May'] < row['Apr']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Jun'] > row['May']
                        else "red" if row['Jun'] < row['May']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Jul'] > row['Jun']
                        else "red" if row['Jul'] < row['Jun']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ],
                    height=30
                    ))
                ])

        fig.update_layout(title= 'kubernetes')

        return fig

    else:
        clk_repo = clk_data['points'][0]['text']
        dff1 = df_pr_committers[df_pr_committers['rg_name'] == select_org]
        dff2 = dff1[dff1['repo_name'] == clk_repo]
        sub_frame = dff2[["rg_name", "repo_name", 'yearmonth', 'cmt_committer_name', 'cntrb_company', 'cntrb_location', 'num_of_commit']]
        table = pd.pivot_table(sub_frame, values='num_of_commit',
                                index=['cmt_committer_name', 'cntrb_company', 'cntrb_location'],
                            columns=['yearmonth'], aggfunc=np.sum)
        table = table.fillna(0)
        table = table.reset_index().rename(columns={'2022-1':'Jan', '2022-2':'Feb', '2022-3':'Mar',
                                                    '2022-4':'Apr', '2022-5':'May', '2022-6':'Jun',
                                                    '2022-7':'Jul'})
        table = table.sort_values(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'], ascending=False)

        fig2 = go.Figure(data=[go.Table(
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
            cells=dict(values=[table.cmt_committer_name,
                                table.cntrb_company,
                                table.cntrb_location,
                                table.Jan,
                                table.Feb,
                                table.Mar,
                                table.Apr,
                                table.May,
                                table.Jun,
                                table.Jul],
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
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Mar'] >row['Feb']
                        else "red" if row['Mar'] < row['Feb']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Apr'] >row['Mar']
                        else "red" if row['Apr'] < row['Mar']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['May'] >row['Apr']
                        else "red" if row['May'] < row['Apr']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Jun'] >row['May']
                        else "red" if row['Jun'] < row['May']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ['green' if row['Jul'] >row['Jun']
                        else "red" if row['Jul'] < row['Jun']
                        else 'darkslategray'
                        for index,row in table.iterrows()
                        ],
                        ],
                    height=30
                    ))
                ])

        fig2.update_layout(title=f'{clk_repo}')

        return fig2