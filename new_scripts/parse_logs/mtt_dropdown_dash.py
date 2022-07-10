import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly
from LogParser import *
import plotly.graph_objs as go

app = dash.Dash()

#Only use *.html to handle ofilm logs
path = r'D:\FPCGit\python_scripts\new_scripts\parse_logs\data'
log_pattern = '*.json'

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

p = logParserYieldReport(path, log_pattern)
yield_results = list(p.yield_results())
p.df = pd.DataFrame(yield_results)
df_module_yield = p.get_unique_sensor_yield()
df_module_yield.to_excel('sensor_yield.xls', encoding='utf-8')
df_log_yield = p.get_general_yield()
df_log_yield.to_excel('log_yield.xls', encoding='utf-8')

app.layout = html.Div([
    dcc.Dropdown(
        id='test-dropdown',
        options=[
            {'label': i, 'value': i} for i in df_module_yield.columns[2:]
        ],
        value=df_module_yield.columns[2]
    ),
    html.H4('MTT Module Yield DataTable'),

    dt.DataTable(
        rows=df_module_yield.to_dict('records'),
        columns=df_module_yield.columns,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-yield'
    ),
    html.H4('MTT Yield DataTable'),
    dt.DataTable(
        rows=df_log_yield.to_dict('records'),
        columns=df_log_yield.columns,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-log-yield'
    ),

    dcc.Graph(
        id='graph-test'
    ),
])

@app.callback(
    Output('graph-test', 'figure'),
    [Input('test-dropdown', 'value')])
def update_graph(test):
    print('update_graph', test)
    if 'defective' in test:
        df_test = pd.DataFrame(logParserDefectivePixels(path, log_pattern).yield_results())
        df_test.sort_values(by='defective_pixels_result', inplace=True, ascending=False)
        df_test.to_excel('defective_pixels.xls', encoding='utf-8')

        df_image_constant = pd.DataFrame(logParserCtlImageConstant(path, log_pattern).yield_results())

        df_test = df_test.merge(df_image_constant)

        df_image_drive = pd.DataFrame(logParserCtlImageDrive(path, log_pattern).yield_results())
        df_test = df_test.merge(df_image_drive)

        #df_image_constant.sort_values(by='image_constant_result', inplace=True, ascending=False)
        df_image_constant.to_excel('image_constant.xls', encoding='utf-8')
        #df_image_drive.sort_values(by='image_drive_result', inplace=True, ascending=False)
        df_image_drive.to_excel('image_drive.xls', encoding='utf-8')

    elif 'dead' in test:
        df_test = pd.DataFrame(logParserDefectivePixels(path, log_pattern).yield_results())
        df_test.sort_values(by='result', inplace=True, ascending=False)
        df_test.to_excel('dead_pixels.xls', encoding='utf-8')

    elif 'MQT' in test or 'modulequality' in test:
        df_test = pd.DataFrame(logParserMqt(path, log_pattern).yield_results())
        df_test.sort_values(by='snr', ascending=False, inplace=True)
        df_test.to_excel('mqt.xls', encoding='utf-8')

    elif 'afd' in test:
        df_test = pd.DataFrame(logParserAfdCal(path).yield_results())
        df_test.sort_values(by='afd_cal_0_0', inplace=True, ascending=False)
        df_test.to_excel('afd.xls', encoding='utf-8')

    elif 'capacitance' in test:
        df_test = pd.DataFrame(logParserCap(path).yield_results())
        df_test.sort_values(by='result', inplace=True, ascending=False)
        df_test.to_excel('capacitance.xls', encoding='utf-8')
    else:
        raise Exception('No details')

    return setup_figure(df_test)

def setup_figure(df_test):
    cols = [col for col in df_test.columns if col != 'host_id' and col != 'log' and col != 'result' and col != 'MQT' and
            col != 'error_code' and 'result' not in col]

    number_of_plots = len(cols) if 'udr' not in df_test.columns else len(cols) + 1
    fig = plotly.tools.make_subplots(
        rows=number_of_plots, cols=1,
        subplot_titles=cols)

    for i, col in enumerate(cols):
        df_test[col].dropna(inplace=True)
        fig.append_trace(go.Histogram(
            x=df_test[col], name=col
        ), i + 1, 1)

    if 'udr' in df_test.columns:
        fig.append_trace(go.Scatter(
            x=df_test['snr'],
            y=df_test['udr'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='snr_udr'
        ), 4, 1)

    fig['layout']['showlegend'] = True
    fig['layout']['height'] = 6400 if number_of_plots > 10 else 1600
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    fig['layout']['yaxis3']['type'] = 'log'
    return fig

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)