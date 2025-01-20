# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)

                                dcc.Dropdown(
                                    id = 'site-dropdown',
                                    options = [
                                        {'label': 'Successful Launches from Each Site', 'value': 'ALL-S'},
                                        {'label': 'All Successful and Failed Launches', 'value': 'ALL-L'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                    ],
                                    value = 'ALL-S',
                                    placeholder = 'Select Launch Site',
                                    searchable = True,
                                    style = {'width': '80%', 'padding': '2px', 'fontsize': '22px', 'text-align-last': 'left'}
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=500, value=[min_payload, max_payload],
                                                marks={2500:{'label':'2500 kg'},
                                                       5000:{'label':'5000 kg'},
                                                       7500:{'label':'7500 kg'}
                                                }
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown',component_property='value')
)

def site_chart(selected_site):
    if selected_site == 'ALL-S':
        selection_df = spacex_df[spacex_df['class'] == 1] # Successful launches from each site
        sel_title = 'Origin of successful launches'
        return px.pie(
            selection_df, values = 'class', names = 'Launch Site', title = sel_title
        )
    if selected_site == 'ALL-L':
        selection_df = spacex_df # All data
        sel_title = 'All Successful and Failed Launches'
    else:
        selection_df = spacex_df[spacex_df['Launch Site'] == selected_site] # Just selected site launches
        sel_title = 'Launches from '+selected_site

    successful_launches = selection_df['class'].value_counts().sort_index(ascending = True)
    successful_launches.reindex(index = ['1','0'])

    pie_labels = ['Failure', 'Success']
    pie_colmap = {0:'#773322', 1:'#227733'} # Custom colors

    return px.pie(
        successful_launches, values = successful_launches.values, labels = pie_labels,
        color = successful_launches.index, color_discrete_map = pie_colmap, names = pie_labels, title = sel_title
    )

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown',component_property='value'),
     Input(component_id='payload-slider', component_property='value')
    ]
)

def scatter_chart(selected_site, payload_range):
    selection_df = spacex_df[
                   (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                   (spacex_df['Payload Mass (kg)'] <= payload_range[1])
                   ]

    if 'ALL' not in selected_site:
        selection_df = selection_df[selection_df['Launch Site'] == selected_site]

    return px.scatter(
        selection_df, x = 'Payload Mass (kg)', y = 'class', size = 'Payload Mass (kg)',
        color = 'Booster Version Category', title = 'Payload versus Success',
        labels = {'class':'Success', 'Payload Mass (kg)':'Payload Mass (kg)'}
    )

# Run the app
if __name__ == '__main__':
    app.run_server()
