import dash_table
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from subprocess import call
import pandas as pd
import random
import simpy
import numpy as np
import math
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots

initial = pd.DataFrame([0])
initial.to_csv('progress.csv')

# Empty DataFrame to start the DataTable (workaround for bug in DataTable - https://github.com/plotly/dash-table/issues/436#issuecomment-615924723)
start_table_df = pd.DataFrame(columns=[''])

############################################ the dash app layout ################################################
external_stylesheets = [dbc.themes.SUPERHERO] #dbc.themes.BOOTSTRAP

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.title = "Discrete-Event Simulation for Optimal Gating Factor in Semiconductor Scheduling System"

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("No. of step 1 tools:"),
                dbc.Input(
                    id="s1_tools", type="number", placeholder="No. of step 1 tools",
                    min=1, max=30, step=1, value=8,
                )
            ]
        ),

        dbc.FormGroup(
            [
                dbc.Label("No. of step 2 tools:"),
                dbc.Input(
                    id="s2_tools", type="number", placeholder="No. of step 2 tools",
                    min=1, max=30, step=1, value=18,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("No. of step 3 tools:"),
                dbc.Input(
                    id="s3_tools", type="number", placeholder="No. of step 3 tools",
                    min=1, max=30, step=1, value=4,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("No. of step 4 tools:"),
                dbc.Input(
                    id="s4_tools", type="number", placeholder="No. of step 4 tools",
                    min=1, max=30, step=1, value=3,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("No. of step 5 tools:"),
                dbc.Input(
                    id="s5_tools", type="number", placeholder="No. of step 5 tools",
                    min=1, max=30, step=1, value=8,
                )
            ]
        ),

                
        dbc.FormGroup(
            [
                dbc.Label("Step 1-2 Q-time spec (hours):"),
                dbc.Input(
                    id="s12_qt_spec", type="number", placeholder="Step 1-2 Q-time spec",
                    min=1, max=30, step=1, value=6,
                )
            ]
        ),
        

        dbc.FormGroup(
            [
                dbc.Label("Step 2-3 Q-time spec (hours):"),
                dbc.Input(
                    id="s23_qt_spec", type="number", placeholder="Step 2-3 Q-time spec",
                    min=1, max=30, step=1, value=10,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 3-4 Q-time spec (hours):"),
                dbc.Input(
                    id="s34_qt_spec", type="number", placeholder="Step 3-4 Q-time spec",
                    min=1, max=30, step=1, value=5,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 4-5 Q-time spec (hours):"),
                dbc.Input(
                    id="s45_qt_spec", type="number", placeholder="Step 4-5 Q-time spec",
                    min=1, max=30, step=1, value=10,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 1 initial lots:"),
                dbc.Input(
                    id="s1_lots", type="number", placeholder="Step 1 initial lots",
                    min=1, max=50, step=1, value=10,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 2 initial lots:"),
                dbc.Input(
                    id="s2_lots", type="number", placeholder="Step 2 initial lots",
                    min=1, max=50, step=1, value=6,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 3 initial lots:"),
                dbc.Input(
                    id="s3_lots", type="number", placeholder="Step 3 initial lots",
                    min=1, max=50, step=1, value=6,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 4 initial lots:"),
                dbc.Input(
                    id="s4_lots", type="number", placeholder="Step 4 initial lots",
                    min=1, max=50, step=1, value=6,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Step 5 initial lots:"),
                dbc.Input(
                    id="s5_lots", type="number", placeholder="Step 5 initial lots",
                    min=1, max=50, step=1, value=6,
                )
            ]
        ),
        
        dbc.FormGroup(
            [
                dbc.Label("Simulation length (days):"),
                dbc.Input(
                    id="sim_day", type="number", placeholder="Simulation length (days):",
                    min=1, max=30, step=1, value=5,
                )
            ]
        ),

        
        html.Div(
            [
                dcc.Interval(id="progress-interval", n_intervals=0, interval=1000, disabled=False),
                dbc.Progress(id="progress", striped=True, animated=True),
            ]
        ),
        
        html.Div((html.P([html.Br()]))),
        
        html.Div(
            [
                dbc.Button("Apply", id="submit-button-state",
                   color="primary", block=True),
            ]
        ),
    ],
    body=True,
)



# layout for the whole page
app.layout = dbc.Container(
    [
      html.Div(
          html.Nav(
              html.Span(
                  "IND5003 PROJECT: Discrete-Event Simulation for Optimal Gating Ratio in Semiconductor Scheduling System",
              className = "navbar-brand mb-0 h1"),
              className = "navbar navbar-dark bg-dark")
          ),
        # now onto the main page, i.e. the controls on the left
        # and the graphs on the right.
        dbc.Row(
            [
                # here we place the controls we just defined,
                # and tell them to use up the left 3/12ths of the page.
                dbc.Col(controls, md=2),
                # now we place the graphs on the page, taking up
                # the right 9/12ths.
                dbc.Col(
                    [
                        html.Div((html.P([html.Br()]))),
                                
                        dbc.Row(html.Div(html.Span(html.H5("Select one of the simulated result to show the charts"
                                )), style= {'display': 'none'}, id='table-header')),
                                
                        html.Div((html.P([html.Br()]))),
                        # the main graph that displays coronavirus over time.
                        dbc.Row(html.Div([
                            dash_table.DataTable(
                                id='table1',
                                data=start_table_df.to_dict('records'), 
                                columns = [{'id': c, 'name': c} for c in start_table_df.columns],
                                fixed_rows={'headers': True, 'data': 0},
                                style_table={'height': 400, 'minWidth': '90%'},
                                row_selectable="single",
                                selected_rows=[],
                                filter_action="native",
                                sort_action="native",
                                sort_mode="single",
                                page_action="native",
                                page_current= 0,
                                page_size= 10,
                                # editable=True,
                                style_as_list_view=True,
                                style_cell = {'backgroundColor': 'rgb(78, 93, 108)', 'color': 'white',
                                              'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                              'height': 'auto',},
                                style_header={'backgroundColor': 'rgb(223, 105, 26)',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 0, 'whiteSpace': 'normal'
                                    }, 
                                style_cell_conditional=[
                                            {
                                                'textAlign': 'center'
                                            }
                                        ]
                            )
                        ], style= {'display': 'none'}, id='table1-container')),
                        
                        dbc.Row(html.Div((html.P([html.Br()])))),
                        
                        dbc.Row(
                            [
                                html.Div((html.P([html.Br()]))),
                                dbc.Col(dcc.Loading(id = "loading-icon1", 
                children=[html.Div(dcc.Graph(id='c1'), style= {'display': 'block'})],type="default")),
                                dbc.Col(dcc.Loading(id = "loading-icon2", 
                children=[html.Div(dcc.Graph(id='c2'), style= {'display': 'block'})],type="default")),
                                dbc.Col(dcc.Loading(id = "loading-icon3", 
                children=[html.Div(dcc.Graph(id='c3'), style= {'display': 'block'})],type="default")),
                                dbc.Col(dcc.Loading(id = "loading-icon4", 
                children=[html.Div(dcc.Graph(id='c4'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                        
                        html.Div((html.P([html.Br()]))),
                        
                        dbc.Row(
                            [
                                dbc.Col(dcc.Loading(id = "loading-icon6", 
                children=[html.Div(dcc.Graph(id='c6'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                        html.Div((html.P([html.Br()]))),
                        dbc.Row(
                            [
                                dbc.Col(dcc.Loading(id = "loading-icon7", 
                children=[html.Div(dcc.Graph(id='c7'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                        html.Div((html.P([html.Br()]))),                        
                        dbc.Row(
                            [
                                dbc.Col(dcc.Loading(id = "loading-icon8", 
                children=[html.Div(dcc.Graph(id='c8'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                        html.Div((html.P([html.Br()]))),                                                
                        dbc.Row(
                            [
                                dbc.Col(dcc.Loading(id = "loading-icon9", 
                children=[html.Div(dcc.Graph(id='c9'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                        html.Div((html.P([html.Br()]))),                                                                        
                        dbc.Row(
                            [
                                dbc.Col(dcc.Loading(id = "loading-icon10", 
                children=[html.Div(dcc.Graph(id='c10'), style= {'display': 'block'})],type="default")),
                            ]
                        ),
                                              
                    ],
                    md=10
                ),
            ],
            align="top",
        ),
    ],
    # fluid is set to true so that the page reacts nicely to different sizes etc.
    fluid=True,
)


# In[13]:

#update text box "simulated completed" and run simulation
@app.callback(
    [Output('table-header', 'style'), Output('table1-container','style')],
    [Input("submit-button-state", "n_clicks"), Input("s1_tools", "value"), Input("s2_tools", "value")
     , Input("s3_tools", "value"), Input("s4_tools", "value"), Input("s5_tools", "value")
     , Input("s12_qt_spec", "value"), Input("s23_qt_spec", "value"), Input("s34_qt_spec", "value"), Input("s45_qt_spec", "value")
     , Input("s1_lots", "value"), Input("s2_lots", "value"), Input("s3_lots", "value"), Input("s4_lots", "value")
     , Input("s5_lots", "value"), Input("sim_day", "value")],
)
def button(n_clicks, s1t, s2t, s3t, s4t, s5t, s12q, s23q, s34q, s45q, s1l, s2l, s3l, s4l, s5l, simday):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100

    initial = pd.DataFrame([0])
    initial.to_csv('progress.csv')
    if n_clicks is None:
        raise PreventUpdate

    elif n_clicks is not None:
        print("button click!")
        call(["python", 'simpy_final.py', str(s1t), str(s2t), str(s3t), str(s4t), str(s5t), str(s12q), str(s23q), str(s34q),
              str(s45q), str(s1l), str(s2l), str(s3l), str(s4l), str(s5l), str(simday)])

        # only add text after 5% progress to ensure text isn't squashed too much
        return {'display': 'block'}, {'display': 'block'}
    
@app.callback(
    [Output('table1','data'), Output('table1','columns')],
    [Input("progress", "value")]
)
def update_table(value):

    if value != 100:

        raise PreventUpdate
    else:
        table_data = pd.read_csv('database_gr.csv', index_col=0)
        table_data['CR'] = table_data['CR'].astype(float).round(3)
        table_data.columns = ['Gating Ratio 1', 'Gating Ratio 2', 'Gating Ratio 3', 'Gating Ratio 4', 'Gating Ratio 5', 'Total Output (lots)', 'Step 1-2 Q-time breached (lots)', 'Step 2-3 Q-time breached (lots)', 'Step 3-4 Q-time breached (lots)', 'Step 4-5 Q-time breached (lots)', 'Combined Ratio']
        table_data['Gating Ratio 1'] = table_data['Gating Ratio 1'].astype(float).round(3)
        table_data['Gating Ratio 2'] = table_data['Gating Ratio 2'].astype(float).round(3)
        table_data['Gating Ratio 3'] = table_data['Gating Ratio 3'].astype(float).round(3)
        table_data['Gating Ratio 4'] = table_data['Gating Ratio 4'].astype(float).round(3)
        table_data['Gating Ratio 5'] = table_data['Gating Ratio 5'].astype(float).round(3)
        return table_data.to_dict("rows"), [{"id": x, "name": x} for x in table_data.columns]
    
@app.callback(
    [Output("progress", "value"), Output("progress", "children"), Output("progress-interval", "disabled")],
    [Input("progress-interval", "n_intervals"), Input("submit-button-state", "n_clicks")]
)
def update_progress(interval, n_clicks):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress_pct = pd.read_csv('progress.csv', index_col=0).iloc[0,0]
    if progress_pct != 100 or n_clicks is not None:
        return progress_pct, "{}%".format(round(progress_pct,1)) if progress_pct >= 5 else "", False
    
    else:
        return progress_pct, "{}%".format(round(progress_pct,1)) if progress_pct >= 5 else "", True
    
    
#callback to update qtime histogram1
@app.callback(
   [Output('c1', 'figure'), Output('c1', 'style')],
   [Input('table1', "selected_rows"), Input('s12_qt_spec', 'value')], 
   [State("progress", "value")]
)
def update_histogram1(selected_rows, spec, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_qt = pd.read_csv('database_qt.csv', index_col=0)
        qt_filtered = temp_qt[(temp_qt['Gating Ratio 1'] == GR1) & (temp_qt['Gating Ratio 2'] == GR2) & 
                              (temp_qt['Gating Ratio 3'] == GR3) & (temp_qt['Gating Ratio 4'] == GR4) &
                              (temp_qt['Gating Ratio 5'] == GR5) & (temp_qt['step'] == '1-2')]
        qt_filtered['Q-time actual'] = qt_filtered['Q-time actual']/60
        fig = px.histogram(qt_filtered, x="Q-time actual", template = 'plotly', color = 'priority', barmode="overlay",nbins=20)
        fig.update_yaxes(title_text="Q-time breached lot counts")
        fig.update_xaxes(title_text="Q-time actual (hours)  |  spec in red line")
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              yref= 'paper', y0= 0, y1= 1,
              xref= 'x', x0= spec, x1= spec, line = dict(color = "red")
            )
        ])
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=80,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
            title_text="Step 1-2 Queue Time"
        )
        return fig, {'display': 'block'}
    
#callback to update qtime histogram2
@app.callback(
   [Output('c2', 'figure'), Output('c2', 'style')],
   [Input('table1', "selected_rows"), Input('s23_qt_spec', 'value')], 
   [State("progress", "value")]
)
def update_histogram2(selected_rows, spec, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_qt = pd.read_csv('database_qt.csv', index_col=0)
        qt_filtered = temp_qt[(temp_qt['Gating Ratio 1'] == GR1) & (temp_qt['Gating Ratio 2'] == GR2) & 
                              (temp_qt['Gating Ratio 3'] == GR3) & (temp_qt['Gating Ratio 4'] == GR4) &
                              (temp_qt['Gating Ratio 5'] == GR5) & (temp_qt['step'] == '2-3')]
        qt_filtered['Q-time actual'] = qt_filtered['Q-time actual']/60
        fig = px.histogram(qt_filtered, x="Q-time actual", template = 'plotly', color = 'priority', barmode="overlay",nbins=20)
        fig.update_yaxes(title_text="Q-time breached lot counts")
        fig.update_xaxes(title_text="Q-time actual (hours)  |  spec in red line")
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              yref= 'paper', y0= 0, y1= 1,
              xref= 'x', x0= spec, x1= spec, line = dict(color = "red")
            )
        ])
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=80,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
            title_text="Step 2-3 Queue Time"
        )
        return fig, {'display': 'block'}

#callback to update qtime histogram3
@app.callback(
   [Output('c3', 'figure'), Output('c3', 'style')],
   [Input('table1', "selected_rows"), Input('s34_qt_spec', 'value')], 
   [State("progress", "value")]
)
def update_histogram3(selected_rows, spec, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_qt = pd.read_csv('database_qt.csv', index_col=0)
        qt_filtered = temp_qt[(temp_qt['Gating Ratio 1'] == GR1) & (temp_qt['Gating Ratio 2'] == GR2) & 
                              (temp_qt['Gating Ratio 3'] == GR3) & (temp_qt['Gating Ratio 4'] == GR4) &
                              (temp_qt['Gating Ratio 5'] == GR5) & (temp_qt['step'] == '3-4')]
        qt_filtered['Q-time actual'] = qt_filtered['Q-time actual']/60
        fig = px.histogram(qt_filtered, x="Q-time actual", template = 'plotly', color = 'priority', barmode="overlay",nbins=20)
        fig.update_yaxes(title_text="Q-time breached lot counts")
        fig.update_xaxes(title_text="Q-time actual (hours)  |  spec in red line")
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              yref= 'paper', y0= 0, y1= 1,
              xref= 'x', x0= spec, x1= spec, line = dict(color = "red")
            )
        ])
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=80,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
            title_text="Step 3-4 Queue Time"
        )
        return fig, {'display': 'block'}
    
#callback to update qtime histogram4
@app.callback(
   [Output('c4', 'figure'), Output('c4', 'style')],
   [Input('table1', "selected_rows"), Input('s45_qt_spec', 'value')], 
   [State("progress", "value")]
)
def update_histogram4(selected_rows, spec, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_qt = pd.read_csv('database_qt.csv', index_col=0)
        qt_filtered = temp_qt[(temp_qt['Gating Ratio 1'] == GR1) & (temp_qt['Gating Ratio 2'] == GR2) & 
                              (temp_qt['Gating Ratio 3'] == GR3) & (temp_qt['Gating Ratio 4'] == GR4) &
                              (temp_qt['Gating Ratio 5'] == GR5) & (temp_qt['step'] == '4-5')]
        qt_filtered['Q-time actual'] = qt_filtered['Q-time actual']/60
        fig = px.histogram(qt_filtered, x="Q-time actual", template = 'plotly', color = 'priority', barmode="overlay",nbins=20)
        fig.update_yaxes(title_text="Q-time breached lot counts")
        fig.update_xaxes(title_text="Q-time actual (hours)  |  spec in red line")
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              yref= 'paper', y0= 0, y1= 1,
              xref= 'x', x0= spec, x1= spec, line = dict(color = "red")
            )
        ])
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=80,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
            title_text="Step 4-5 Queue Time"
        )
        return fig, {'display': 'block'}

#callback to update resource chart 1
@app.callback(
   [Output('c6', 'figure'), Output('c6', 'style')],
   [Input('table1', "selected_rows")], 
   [State("progress", "value")]
)
def update_line1(selected_rows, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_res = pd.read_csv('database_res.csv', index_col=0)
        res_filtered = temp_res[(temp_res['Gating Ratio 1'] == GR1) & (temp_res['Gating Ratio 2'] == GR2) & 
                              (temp_res['Gating Ratio 3'] == GR3) & (temp_res['Gating Ratio 4'] == GR4) &
                              (temp_res['Gating Ratio 5'] == GR5) & (temp_res['step'] == 1)][['time','remaining_mc','in_queue']]
        res_filtered['time'] = res_filtered['time'] / 60
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['remaining_mc'].to_list(), 
                       name="Remaining machine count"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['in_queue'].to_list(), 
                       name="Lots in queue"),
            secondary_y=True,
        )
        
        # Add figure title
        fig.update_layout(
            title_text="Step 1: Remaining machine counts vs. Lots in queue"
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Simulation (hours)")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Remaining machine count", secondary_y=False)
        fig.update_yaxes(title_text="No. of lots in queue", secondary_y=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=40,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
        )
        
        return fig, {'display': 'block'}
    

#callback to update resource chart 2
@app.callback(
   [Output('c7', 'figure'), Output('c7', 'style')],
   [Input('table1', "selected_rows")], 
   [State("progress", "value")]
)
def update_line2(selected_rows, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_res = pd.read_csv('database_res.csv', index_col=0)
        res_filtered = temp_res[(temp_res['Gating Ratio 1'] == GR1) & (temp_res['Gating Ratio 2'] == GR2) & 
                              (temp_res['Gating Ratio 3'] == GR3) & (temp_res['Gating Ratio 4'] == GR4) &
                              (temp_res['Gating Ratio 5'] == GR5) & (temp_res['step'] == 2)][['time','remaining_mc','in_queue']]
        res_filtered['time'] = res_filtered['time'] / 60
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['remaining_mc'].to_list(), 
                       name="Remaining machine count"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['in_queue'].to_list(), 
                       name="Lots in queue"),
            secondary_y=True,
        )
        
        # Add figure title
        fig.update_layout(
            title_text="Step 2: Remaining machine counts vs. Lots in queue"
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Simulation (hours)")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Remaining machine count", secondary_y=False)
        fig.update_yaxes(title_text="No. of lots in queue", secondary_y=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=40,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
        )
        
        return fig, {'display': 'block'}
    
#callback to update resource chart 3
@app.callback(
   [Output('c8', 'figure'), Output('c8', 'style')],
   [Input('table1', "selected_rows")], 
   [State("progress", "value")]
)
def update_line3(selected_rows, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_res = pd.read_csv('database_res.csv', index_col=0)
        res_filtered = temp_res[(temp_res['Gating Ratio 1'] == GR1) & (temp_res['Gating Ratio 2'] == GR2) & 
                              (temp_res['Gating Ratio 3'] == GR3) & (temp_res['Gating Ratio 4'] == GR4) &
                              (temp_res['Gating Ratio 5'] == GR5) & (temp_res['step'] == 3)][['time','remaining_mc','in_queue']]
        res_filtered['time'] = res_filtered['time'] / 60
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['remaining_mc'].to_list(), 
                       name="Remaining machine count"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['in_queue'].to_list(), 
                       name="Lots in queue"),
            secondary_y=True,
        )
        
        # Add figure title
        fig.update_layout(
            title_text="Step 3: Remaining machine counts vs. Lots in queue"
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Simulation (hours)")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Remaining machine count", secondary_y=False)
        fig.update_yaxes(title_text="No. of lots in queue", secondary_y=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=40,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
        )
        return fig, {'display': 'block'}
    
    
#callback to update resource chart 4
@app.callback(
   [Output('c9', 'figure'), Output('c9', 'style')],
   [Input('table1', "selected_rows")], 
   [State("progress", "value")]
)
def update_line4(selected_rows, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_res = pd.read_csv('database_res.csv', index_col=0)
        res_filtered = temp_res[(temp_res['Gating Ratio 1'] == GR1) & (temp_res['Gating Ratio 2'] == GR2) & 
                              (temp_res['Gating Ratio 3'] == GR3) & (temp_res['Gating Ratio 4'] == GR4) &
                              (temp_res['Gating Ratio 5'] == GR5) & (temp_res['step'] == 4)][['time','remaining_mc','in_queue']]
        res_filtered['time'] = res_filtered['time'] / 60
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['remaining_mc'].to_list(), 
                       name="Remaining machine count"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['in_queue'].to_list(), 
                       name="Lots in queue"),
            secondary_y=True,
        )
        
        # Add figure title
        fig.update_layout(
            title_text="Step 4: Remaining machine counts vs. Lots in queue"
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Simulation (hours)")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Remaining machine count", secondary_y=False)
        fig.update_yaxes(title_text="No. of lots in queue", secondary_y=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=40,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
        )
        
        return fig, {'display': 'block'}
    
    
#callback to update resource chart 5
@app.callback(
   [Output('c10', 'figure'), Output('c10', 'style')],
   [Input('table1', "selected_rows")], 
   [State("progress", "value")]
)
def update_line5(selected_rows, value):
    if value != 100:
        return {}, {'display': 'none'}
        
    if value == 100:
        temp_gr = pd.read_csv('database_gr.csv', index_col=0)
        GR1 = temp_gr.iloc[[selected_rows[0]]]['GR1'].values[0]
        GR2 = temp_gr.iloc[[selected_rows[0]]]['GR2'].values[0]
        GR3 = temp_gr.iloc[[selected_rows[0]]]['GR3'].values[0]
        GR4 = temp_gr.iloc[[selected_rows[0]]]['GR4'].values[0]
        GR5 = temp_gr.iloc[[selected_rows[0]]]['GR5'].values[0]
        temp_res = pd.read_csv('database_res.csv', index_col=0)
        res_filtered = temp_res[(temp_res['Gating Ratio 1'] == GR1) & (temp_res['Gating Ratio 2'] == GR2) & 
                              (temp_res['Gating Ratio 3'] == GR3) & (temp_res['Gating Ratio 4'] == GR4) &
                              (temp_res['Gating Ratio 5'] == GR5) & (temp_res['step'] == 5)][['time','remaining_mc','in_queue']]
        res_filtered['time'] = res_filtered['time'] / 60
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['remaining_mc'].to_list(), 
                       name="Remaining machine count"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=res_filtered['time'].to_list(), y=res_filtered['in_queue'].to_list(), 
                       name="Lots in queue"),
            secondary_y=True,
        )
        
        # Add figure title
        fig.update_layout(
            title_text="Step 5: Remaining machine counts vs. Lots in queue"
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Simulation (hours)")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Remaining machine count", secondary_y=False)
        fig.update_yaxes(title_text="No. of lots in queue", secondary_y=True)
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=40,
                pad=0
            ),
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
            paper_bgcolor='rgb(78, 93, 108)',
            font = dict(color='rgb(255, 255, 255)'),
        )
        
        return fig, {'display': 'block'}
    

if __name__ == '__main__':
    pd.DataFrame([0]).to_csv('progress.csv')
    app.run_server(debug=False)
