import csv
import pandas as pd
import plotly.graph_objs as go
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

csv_E1_30 = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1 3.0V/out/summary_mqt_E1_3.0V.csv"
csv_E1_33 = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1 3.3V/out/summary_mqt.csv"
csv_E2_33 = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E2 3.3V/out/summary_mqt_E2_3.3V.csv"

df = pd.read_csv(csv_E1_30, sep=";")
E1_30_SNR = df['Snr'].tolist()
E1_30_signal = df['signal_power'].tolist()
E1_30_fpNoise = df['noise_fp'].tolist()

df=pd.read_csv(csv_E1_33, sep=";")
E1_33_SNR = df['Snr'].tolist()
E1_33_signal = df['signal_power'].tolist()
E1_33_fpNoise = df['noise_fp'].tolist()

df=pd.read_csv(csv_E2_33, sep=";")
E2_33_SNR = df['Snr'].tolist()
E2_33_signal = df['signal_power'].tolist()
E2_33_fpNoise = df['noise_fp'].tolist()

init_notebook_mode(connected=True)

# E1_30 and E1_33 snr compare
max1 = max(E1_30_SNR)
min1 = min(E1_30_SNR)
max2 = max(E1_33_SNR)
min2 = min(E1_33_SNR)

trace1 = go.Histogram(x=E1_30_SNR, name='E1_30_SNR', xbins=dict(start=min1, end=max1, size=0.5))
trace2 = go.Histogram(x=E1_33_SNR, name='E1_33_SNR', xbins=dict(start=min2, end=max2, size=0.5))

data = [trace1, trace2]
layout = go.Layout(title='E1_30_33_SNR_Compare', xaxis=dict(title='value'), yaxis=dict(title='count'), bargap=0.2, bargroupgap=0.1)
fig = go.Figure(data=data, layout=layout)
plot(fig, filename = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1_30_33_SNR_Compare.html")

#E1_30 and E2_33 snr compare
max1 = max(E1_30_SNR)
min1 = min(E1_30_SNR)
max2 = max(E2_33_SNR)
min2 = min(E2_33_SNR)

trace1 = go.Histogram(x=E1_30_SNR, name='E1_30_SNR', xbins=dict(start=min1, end=max1, size=0.5))
trace2 = go.Histogram(x=E2_33_SNR, name='E2_33_SNR', xbins=dict(start=min2, end=max2, size=0.5))
data = [trace1, trace2]
layout = go.Layout(title='E1_30_E2_33_SNR_Compare', xaxis=dict(title='value'), yaxis=dict(title='count'), bargap=0.2, bargroupgap=0.1)
fig = go.Figure(data=data, layout=layout)
plot(fig, filename = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1_30_E2_33_SNR_Compare.html")

#E1_30 and E2_33 signal compare
max1 = max(E1_30_signal)
min1 = min(E1_30_signal)
max2 = max(E2_33_signal)
min2 = min(E2_33_signal)

trace1 = go.Histogram(x=E1_30_signal, name='E1_30_SIGNAL', xbins=dict(start=min1, end=max1, size=10))
trace2 = go.Histogram(x=E2_33_signal, name='E2_33_SIGNAL', xbins=dict(start=min2, end=max2, size=10))
data = [trace1, trace2]
layout = go.Layout(title='E1_30_E2_33_SIGNAL_Compare', xaxis=dict(title='value'), yaxis=dict(title='count'), bargap=0.2, bargroupgap=0.1)
fig = go.Figure(data=data, layout=layout)
plot(fig, filename = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1_30_E2_33_SIGNAL_Compare.html")

#E1_30 and E2_33 FPNOISE compare
max1 = max(E1_30_fpNoise)
min1 = min(E1_30_fpNoise)
max2 = max(E2_33_fpNoise)
min2 = min(E2_33_fpNoise)

trace1 = go.Histogram(x=E1_30_fpNoise, name='E1_30_fpNoise', xbins=dict(start=min1, end=max1, size=1))
trace2 = go.Histogram(x=E2_33_fpNoise, name='E2_33_fpNoise', xbins=dict(start=min2, end=max2, size=1))
data = [trace1, trace2]
layout = go.Layout(title='E1_30_E2_33_fpNoise_Compare', xaxis=dict(title='value'), yaxis=dict(title='count'), bargap=0.2, bargroupgap=0.1)
fig = go.Figure(data=data, layout=layout)
plot(fig, filename = "/media/minchao/ext/share/project/E1/1291 LOG 0421 MQT/E1_30_E2_33_fpNoise_Compare.html")




