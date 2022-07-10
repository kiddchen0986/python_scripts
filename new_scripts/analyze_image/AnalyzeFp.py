import struct
import numpy
import itertools
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

print(__version__) #need to be >=1.9.0

file1 = "/media/minchao/ext/share/Jira/CET-35/SNR_modulees_SNR_5_6_7_retest_shanghai/0E11G2UC71FE1E03_20180411-174631-633_img7 noise_fp!60_128_4.raw"

file2 = "/media/minchao/ext/share/Jira/CET-35/SNR_modulees_SNR_5_6_7_retest_shanghai/0E11G2UC71041E03_20180411-180906-296_img7 noise_fp!60_128_4.raw"

array1 = []
array2 = []
array1P = []
array2P = []
array1f = []
array2f = []

width = 60
height = 128
crop_width = 52
crop_height = 120

with open(file1, "rb") as f1:
    bytes = f1.read(width*height*4)
    for i in range(height):
        for j in range(width):
            index = i * width + j
            floatValue = struct.unpack('f', bytes[index * 4: index * 4 + 4])
            if(not(i<4 or i > height-5 or j < 4 or j> width -5)):
                array1.append(floatValue)

with open(file2, "rb") as f2:
    bytes = f2.read(width*height*4)
    for i in range(height):
        for j in range(width):
            if(not(i<4 or i > height-5 or j < 4 or j> width -5)):
                index = i*width + j
                floatValue = struct.unpack('f', bytes[index*4: index*4+4])
                array2.append(floatValue)

array1 = list(itertools.chain.from_iterable(array1))
array2 = list(itertools.chain.from_iterable(array2))

mean1 = numpy.sum([i*i for i in array1])/len(array1)
print(mean1)
mean1 = pow(mean1, 0.5)

mean2 = numpy.sum([i*i for i in array2])/len(array2)
mean2 = pow(mean2, 0.5)


count = 0;
for i in range(crop_height):
    for j in range(crop_width):
        index = i*crop_width + j
        if(abs(array1[index]) > mean1):
            array1P.append(struct.pack('f', array1[index]))
            array1f.append(array1[index])
            count = count + 1
        else:
            array1P.append(struct.pack('f', 0.0))

print("test1 count is " + str(count))


count = 0;
for i in range(crop_height):
    for j in range(crop_width):
        index = i*crop_width + j
        if(abs(array2[index]) > mean2):
            array2P.append(struct.pack('f', array2[index]))
            array2f.append(array2[index])
            count = count + 1
        else:
            array2P.append(struct.pack('f', 0.0))

print("test2 count is " + str(count))

array1P = list(itertools.chain.from_iterable(array1P))
array2P = list(itertools.chain.from_iterable(array2P))

init_notebook_mode(connected=True)

max1 = max(array1f)
min1 = min(array1f)
max2 = max(array2f)
min2 = min(array2f)
print(max1, min1, max2, min2, len(array1f), len(array2f))

trace1 = go.Histogram(x=array1f, name='text1', xbins=dict(start=min1, end=max1, size=5))
trace2 = go.Histogram(x=array2f, name='text2', xbins=dict(start=min2, end=max2, size=5))
data = [trace1, trace2]
layout = go.Layout(title='tests compare', xaxis=dict(title='value'), yaxis=dict(title='count'), bargap=0.2, bargroupgap=0.1)
fig = go.Figure(data=data, layout=layout)
plot(fig, filename = "test1")

with open("/media/minchao/ext/share/Jira/CET-35/SNR_modulees_SNR_5_6_7_retest_shanghai/test1_noise_fp!52_120_4.raw", "wb") as fw:
    fw.write(bytearray(array1P))

with open("/media/minchao/ext/share/Jira/CET-35/SNR_modulees_SNR_5_6_7_retest_shanghai/test2_noise_fp!52_120_4.raw", "wb") as fw:
    fw.write(bytearray(array2P))


