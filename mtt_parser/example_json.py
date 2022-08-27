""" example_json.py

Example of how one may use the mtt_parser to read .json result files.

prerequisite:
    json files includes snr data.
"""
from mtt_tools import mtt_tools as mtt

obj = mtt.data() #create empty data object
parser = mtt.parser(obj) #create parser and link to data object

log_path = "C:\\Hugo_documents\\logs\\1245" #type your path to mtt log folder
parser.init(log_path) #decide if you want to specify targets or not. If not just remove from method call.
parser.parse() #start parsing.
print("------------")
parameter = obj.search("snr_db")[0]
data = obj.get_data(parameter, include_hash=True)
limit = obj.get_data("TestModuleQuality:SnrLimit")[0]
y,y_no_retest = obj.get_yield(data, limit)
if y>=0 and y_no_retest>=0:
    print("snr (limit:" + str(limit) + ")")
    print("yield:" + str(y))
    print("yield no retest:" + str(y_no_retest))