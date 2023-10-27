from dash import dcc, html, dash_table
import dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


df = pd.read_csv('internet_cleaned.csv')
df = df[df['year'] == 2019] 

df['id'] = df['iso_alpha3']
df.set_index('id', inplace=True, drop=False)
print(df.head())

app = dash.Dash(__name__, prevent_initial_callbacks=True)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {'name': i, 'id': i, 'deletable': True, 'selectable':True, 'hideable':True}
            if i == 'iso_alpha3' or i == 'year' or i == 'id'
            else {'name': i, 'id': i, 'deletable':True, 'selectable':True}
            for i in df.columns
        ],
        data=df.to_dict('records'),  # the contents of the table
        editable=True,  # allow editing of data inside all cells
        filter_action='native', # allow filtering of data by user ('native') or not ('none')
        sort_action='native',  # enables data to be sorted per-column by user or not ('none')
        sort_mode='single',  # sort across 'multi' or 'single' columns
        column_selectable='multi', # allow users to select 'multi' or 'single' columns
        row_deletable=True, # allow users to select 'multi' or 'single' rows
        row_selectable='multi',  # choose if user can delete a row (True) or not (False)
        selected_columns=[],  # ids of columns that user selects
        selected_rows=[], # indices of rows that user selects
        page_action='native', # all data is passed to the table up-front or not ('none')
        page_current=0,  # page number that user is on
        page_size=6, # number of rows visible per page
        style_cell={ # ensure adequate header width when text is shorter than cell's text
            'minwidth': 95, 'maxwidth': 95, 'width': 95
        },
        style_cell_conditional=[ # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c },
                'textAlign': 'left'
            } for c in ['country', 'iso_alpha3']
        ],
        style_data={  # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height':'auto'
        }
    ),
    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')
])

@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [
        Input(component_id='datatable-interactivity', component_property='derived_virtual_data'),
        Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
        Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
        Input(component_id='datatable-interactivity', component_property='selected_rows'),
        Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
        Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
        Input(component_id='datatable-interactivity', component_property='active_cell'),
        Input(component_id='datatable-interactivity', component_property='selected_cells')
    ]
)
    


def update_bar(all_rows_data, selected_row_indices, selected_rows_names, selected_rows, order_of_rows_indices, order_of_rows_names, active_cell, selected_cell):

    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(selected_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(selected_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(selected_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(active_cell))
    print("Complete data of all selected cells: {}".format(selected_cell))
    
    #adding some comment to see how to publish and merge to the main brach
    
    
    dff = pd.DataFrame(all_rows_data)

    colors = [ '#7FDBFF' if i in selected_row_indices else '#0074D9' for i in range(len(dff))]
    print(all_rows_data)

    if 'country' in dff and 'did online course' in dff:
        return [
            dcc.Graph(id='bar-chart',
                    figure=px.bar(
                        data_frame=dff,
                        x='country',
                        y='did online course',
                        labels={'did online course': " of Pop took online course"}
                    ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                    .update_traces(marker_color=colors, hovertemplate='<b>%{y}%</b><extra></extra>'))
        ]



@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)

def update_styles(selected_columns):
    return [
        {'if': {'column_id': i},
         'background_color': '#D2F3FF'
        } for i in selected_columns]


@app.callback(
    Output(component_id='choromap-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property='derived_virtual_data'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows')]
)

def update_map(all_rows_data, selected_row_indices):
    dff = pd.DataFrame(all_rows_data)

    borders = [5 if i in selected_row_indices else 1 
               for i in range(len(dff))]
    
    if 'iso_alpha3' in dff and 'internet daily' in dff and 'country' in dff:
        return [
            dcc.Graph(id='choropleth',
                        style={'height':700},
                        figure=px.choropleth(
                            data_frame=dff,
                            locations='iso_alpha3',
                            scope='europe',
                            color='internet daily',
                            title='% of Pop that Uses Internet Daily',
                            hover_data=['country', 'internet daily'],
                            ).update_layout(showlegend=False, title=dict(font=dict(size=28), x=0.5, xanchor='center'))
                            .update_traces(marker_line_width=borders, hovertemplate="<b>%{customdata[0]}</b><br><br>" +
                                                                                "%{customdata[1]}" + "%")
                            )
        ]

if __name__ == '__main__':
    app.run_server(debug=True)