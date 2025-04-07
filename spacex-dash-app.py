# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown list for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'Kennedy Space Center', 'value': 'KSC LC-39A'},
            {'label': 'Cape Canaveral SFC', 'value': 'CCAFS LC-40'},
            {'label': 'Vandenberg SFC', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    html.Br(),
    
    # TASK 2: Pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Range slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    
    # TASK 4: Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: Callback for the pie chart based on the selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Group by Launch Site and sum the successes to get the total successes per site
        df_grouped = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(df_grouped, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
        return fig
    else:
        # Filter the dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count the successes and failures
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        # Map numeric class values to more meaningful labels
        outcome_counts['class'] = outcome_counts['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, 
                     values='count', 
                     names='class', 
                     title=f"Launch Outcome for {entered_site}")
        return fig

# TASK 4: Callback for the scatter chart based on the selected launch site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(selected_site, payload_range):
    # Unpack the payload range values
    low, high = payload_range
    
    # Filter spacex_df based on the payload mass range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        # Use the filtered dataframe as is for all sites
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs. Mission Outcome for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        # Filter the dataframe for the selected launch site
        specific_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(specific_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Mission Outcome for {selected_site}',
                         labels={'class': 'Launch Outcome'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
