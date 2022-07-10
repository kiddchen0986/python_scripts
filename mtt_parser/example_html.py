""" example_html.py

Example of how one may use the mtt_parser to read .html result files.
Do note that when working with .html files you MUST specify target parameters
for the parser to look for. Take a look in one of the .html files and find the
parameters you wish to parse before calling parser.init().

prerequisite:
    html files must include blob data for this example to work.

"""

from mtt_tools import mtt_tools as mtt

obj = mtt.data() #create empty data object
parser = mtt.parser(obj) #create parser and link to data object

log_path = "path/to/folder" #type your path to mtt log folder
targets = ["Uniformity", #add wanted parameters to a list
           "Capacitance Signal Strength",
           "Number of blobs pixels"]
parser.init(log_path,targets) #initialize parser with log path and target list
parser.parse() #start parsing.

"""
Now you have a parsed data object filled with data. The easiest way forward is
to interact with the object through an interactive console, like iPython, and
use the data object help methods to work with the data.
"""
print("------------")
if obj.search("sensorid"): #SensorId exists
    data = obj.get_data("number_of_blobs_pixels", include_hash=True)
    yield_limit = obj.get_data("number_of_blobs_pixels_limit")[0]
    y,y_no_retest = obj.get_yield(data , yield_limit)
    if y>=0 and y_no_retest>=0: #get_yield returns -1 upon failure
        y = 1-y
        y_no_retest = 1-y_no_retest
        print("blob yield:" + str(y))
        print("blob yield no retest:" + str(y_no_retest))
