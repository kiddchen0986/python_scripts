# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import logging


def parse_json_settings(report):
    try:
        # analysis step results log from json
        settings = {}
        for result in ['result', 'results']:
            if result in report['Result']['TestLog']['Steps']['analysis']['Items']:
                settings['analysis_result'] = report['Result']['TestLog']['Steps']['analysis']['Items'][result]
        if 'DefPixelsAnalysisDeadPixelsResult' in settings['analysis_result']:
            settings['analysis_DeadPixels'] = settings['analysis_result']['DefPixelsAnalysisDeadPixelsResult']
            settings['analysis_DeadPixels_CB'] = settings['analysis_DeadPixels']['CheckerboardResult']
            settings['analysis_DeadPixels_ICB'] = settings['analysis_DeadPixels']['InvertedCheckerboardResult']
        if 'SwingingDefPixelsAnalysisDeadPixelsResult' in settings['analysis_result']:
            settings['analysis_SwingDeadPixels'] = settings['analysis_result']['SwingingDefPixelsAnalysisDeadPixelsResult']
            settings['analysis_SwingDeadPixels_CB'] = settings['analysis_SwingDeadPixels']['CheckerboardResult']
            settings['analysis_SwingDeadPixels_ICB'] = settings['analysis_SwingDeadPixels']['InvertedCheckerboardResult']

        # measurement step results log from json
        if 'Analysis' in report['Result']['TestLog']['Steps']['measurement']['Items']['settings']:
            settings['measurement_Analysis'] = report['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']

            data_type = {'measurement_DeadPixels': 'DeadPixelsAnalysisSettings',
                         'measurement_swingDeadPixels': 'SwingingPixelsAnalysisSettings',
                         'measurement_ImageConstant': 'ImageConstantAnalysisSettings'}
            for key, value in data_type.items():
                if value in settings['measurement_Analysis']:
                    settings[key] = settings['measurement_Analysis'][value]

    except KeyError as e:
        logging.error(
            'KeyError {} happens in json settings {}, might be no test result, regard all nan'.format(e, report))

    return settings
