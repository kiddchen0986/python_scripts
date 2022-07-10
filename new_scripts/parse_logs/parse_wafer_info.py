from LogParser import logParserWaferInfo
import pandas as pd

parser = logParserWaferInfo(r'D:\Logs\xiaomi\1291\ofilm\MTT15.1_log', 'wafer.xls')

out = parser.yield_results()
df = pd.DataFrame(out)

print(df.head())
