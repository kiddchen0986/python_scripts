# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#


import os
from Parsers.logParserYieldReport import logParserYieldReport
from Parsers.logParserMqt import logParserMqt
from Parsers.LogParserCurrent import LogParserCurrent
from Parsers.logParserCtlImageConstant import logParserCtlImageConstant
from Parsers.logParserCtlImageDrive import logParserCtlImageDrive
from Parsers.logParserCap import logParserCap
from Parsers.logParserDefectivePixels import logParserDefectivePixels
from Parsers.LogParserHuaweiSNR import LogParserHuaweiSNR
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import reduce, partial
import argparse
import pandas as pd
import logging
from collections import OrderedDict

parser_default_set = {'yield_report': {'default_pattern': '*.json', 'class': logParserYieldReport},
                      'mqt': {'default_pattern': '*.json', 'class': logParserMqt},
                      'current': {'default_pattern': '*.json', 'class': LogParserCurrent},
                      'defective_pixels': {'default_pattern': '*.json', 'class': logParserDefectivePixels},
                      'image_constant': {'default_pattern': '*.json', 'class': logParserCtlImageConstant},
                      'image_drive': {'default_pattern': '*.json', 'class': logParserCtlImageDrive},
                      'cap': {'default_pattern': '*.json', 'class': logParserCap},
                      'huawei_snr': {'default_pattern': 'None', 'class': LogParserHuaweiSNR}}


def yield_result(log_parser):
    results = list(log_parser.yield_results())
    if len(results) == 0:
        logging.error('No {} test data, and are you setting correct path ?'.format(log_parser))
        exit(-1)

    return pd.DataFrame(results)


def analyze(log_parser):
    print('Generating ' + str(log_parser) + '...')
    log_parser.analyze()


def generate_separate_reports(log_parsers):
    with ThreadPoolExecutor() as pool:
        pool.map(analyze, log_parsers)


def generate_merged_report(log_parsers, path, report_prefix):
    with ThreadPoolExecutor() as pool:
        data_frames = pool.map(yield_result, log_parsers)
    merge_keys = ['log', 'host_id', 'sensorid']
    pd_merge_partial = partial(pd.merge, on=merge_keys)
    df = reduce(pd_merge_partial, data_frames)
    df.sort_values(by='sensorid', ascending=False, inplace=True)
    df_max, df_min = df.max(), df.min()
    df_max['log'] = 'MAX'
    df_min['log'] = 'MIN'
    df.loc['MAX'] = df_max
    df.loc['MIN'] = df_min
    df.to_excel(os.path.join(path, report_prefix + '_all.xls'), encoding='utf-8', index=False)

    print('Generating ' + report_prefix + "_merged.xls...")


def generate_all_report(path, report_prefix, merged, parser_filters):
    parsers = []
    for key, value in parser_filters.items():
        if value == 'None':
            continue
        if value != '*.json' and value != '*.txt' and value != '*.html':
            print('parser{}: pattern {} invalid, it should be *.json or *.txt or *.html')
            return
        if key in parser_default_set:
            parsers.append(parser_default_set[key]['class'](path, value, os.path.join(path, report_prefix + '_{}.xls'.format(key))))
        else:
            print('Error:Invalid parameter' + key)
            return
    if len(parsers) == 0:
        print('Error: Not selected any parser')
        return

    if merged:
        generate_merged_report(parsers, path, report_prefix)

    generate_separate_reports(parsers)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="MTT log input path", type=str)
    parser.add_argument("report_prefix", help="Report prefix, the report will be saved in the same path of MTT log, \
                                              and named as report prefix", type=str)
    parser.add_argument("-m", '--merged', help="Enable generate merged data report, default is False", type=bool,
                        default=True)
    for item, val in parser_default_set.items():
        parser.add_argument('--'+item,
                            help="Enable generate {} report,".format(item) + "type should be *.json and *.txt *.html",
                            type=str,
                            default=val['default_pattern'])

    args = parser.parse_args()
    parser_list = OrderedDict()

    for item, default_val in parser_default_set.items():
        if args.__getattr__(item) != 'None':
            parser_list[item] = args.__getattr__(item)

    generate_all_report(args.path, args.report_prefix, args.merged, parser_list)
    print('Finished')
