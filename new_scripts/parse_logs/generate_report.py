# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#


#Generate all the data analysis (excel and distribution images) in one script with multiple processes
import os
from LogParser import *
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from functools import reduce, partial
import argparse
import pandas as pd

# from new_scripts.parse_logs.analyze_excel_data import analyze_excel


def yield_result(parser):
    results = list(parser.yield_results())
    if len(results) == 0:
        logging.error('No {} test data, and are you setting correct path ?'.format(parser))
        exit(-1)

    return pd.DataFrame(results)

def analyze(parser):
    print('Generating ' + str(parser) + '...')
    parser.analyze()

def generate_separate_reports():
    with ProcessPoolExecutor() as pool:
        pool.map(analyze, parsers)


def generate_merged_report():
    with ProcessPoolExecutor() as pool:
        data_frames = pool.map(yield_result, parsers)

    merge_keys = ['log', 'host_id', 'sensorid']
    pd_merge_partial = partial(pd.merge, on=merge_keys)
    df = reduce(pd_merge_partial, data_frames)
    df.sort_values(by='sensorid', ascending=False, inplace=True)
    df.to_excel(os.path.join(path, report_prefix + '_all.xls'), encoding='utf-8', index=False)

    print('Generating ' + report_prefix + "_merged.xls...")


if __name__ == '__main__':
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="MTT log input path", type=str)
    parser.add_argument("report_prefix", help="Report prefix, the report will be saved in the same path of MTT log, \
                                              and named as report prefix", type=str)
    parser.add_argument("-p", '--log_pattern', help="What kind of log do you want to analyze ? Default is *.json; *.txt\
                                                     and *.html may fail", type=str, default=r'*.json')
    parser.add_argument("-m", '--merged', help="Generate merged data report, default is False", type=bool,
                        default=False)
    args = parser.parse_args()

    path = args.path
    log_pattern = args.log_pattern
    report_prefix = args.report_prefix

    parsers = {
        logParserYieldReport(path, log_pattern, os.path.join(path, report_prefix + '_yield.xls')),
        logParserAfdCal(path, log_pattern, os.path.join(path, report_prefix + '_afd_cal.xls')),
        logParserMqt(path, log_pattern, os.path.join(path, report_prefix + '_mqt.xls')),
        LogParser_Current(path, log_pattern, os.path.join(path, report_prefix + '_current.xls')),
        logParserDefectivePixels(path, log_pattern, os.path.join(path, report_prefix + '_defective_pixels.xls')),
        logParserCtlImageConstant(path, log_pattern, os.path.join(path, report_prefix + '_image_constant.xls')),
        logParserCtlImageDrive(path, log_pattern, os.path.join(path, report_prefix + '_image_drive.xls')),
        logParserCap(path, log_pattern, os.path.join(path, report_prefix + '_capacitance.xls'))
    }

    if args.merged:
        generate_merged_report()

    generate_separate_reports()

    print('Finished')
