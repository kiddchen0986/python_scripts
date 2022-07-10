from LogParser import logParserDfdCal

path = r'D:\Logs\OPPO\Fingechip\1511\FC-C-059'
path_xls = r'D:\Logs\OPPO\Fingechip\1511\FC-C-059\dfd_cal.xls'

logParserDfdCal(path, '*.json', path_xls).analyze()