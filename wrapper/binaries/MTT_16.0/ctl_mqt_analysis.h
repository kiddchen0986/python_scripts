/*
* Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
*
* All rights are reserved.
* Proprietary and confidential.
* Unauthorized copying of this file, via any medium is strictly prohibited.
* Any use is subject to an appropriate license granted by Fingerprint Cards AB.
*/

#ifndef CTL_MQT_ANALYSIS_H
#define CTL_MQT_ANALYSIS_H

#include "public/fpc_sensor_info.h"
#include "ctl_rerun_test_analysis_defs.h"
#include <stdbool.h>

typedef struct
{
    uint16_t cropping_left;
    uint16_t cropping_top;
    uint16_t cropping_right;
    uint16_t cropping_bottom;

    float blob_threshold;
    uint32_t blob_limit;

    uint8_t snr_preset;
    float snr_limit;

    float udr_limit;

    bool fixed_pattern_enabled;
    float fixed_pattern_threshold;
    uint32_t fixed_pattern_limit;

    bool is_static_mqt;
} mqt_analysis_settings_t;

/*!
 * \brief Re-run MQT2 analysis
 *
 * \param product       Product type
 * \param hw_id         Hardware id
 * \param settings      Settings to use for the re analysis
 * \param path_to_fmi   Path to the FMI file containing the zebra images.
 * \param output_dir    Directory to store analysis result in.
 *
 * \return 0 if success
 */
CTL_RERUN_ANALYSIS_API uint32_t ctl_mqt2_analysis(
    fpc_product_type_t product,
    uint16_t hw_id,
    mqt_analysis_settings_t settings,
    char* path_to_fmi,
    char* output_dir);

/*!
* \brief Re-run MQT2 analysis with extended log output
*
* \param product       Product type
* \param hw_id         Hardware id
* \param settings      Settings to use for the re analysis
* \param path_to_fmi   Path to the FMI file containing the zebra images.
* \param output_dir    Directory to store analysis result in.
* \param key           Key needed for the extended information.
*
* \return 0 if success
*/
CTL_RERUN_ANALYSIS_API uint32_t ctl_mqt2_analysis_extended(
    fpc_product_type_t product,
    uint16_t hw_id,
    mqt_analysis_settings_t settings,
    char* path_to_fmi,
    char* output_dir,
    uint32_t key);

/*!
* \brief Re-run MQT2 analysis with extended log output.
* Only the fp_image from extended images will be saved.
*
* \param product       Product type
* \param hw_id         Hardware id
* \param settings      Settings to use for the re analysis
* \param path_to_fmi   Path to the FMI file containing the zebra images.
* \param output_dir    Directory to store analysis result in.
* \param key           Key needed for the extended information.
*
* \return 0 if success
*/
CTL_RERUN_ANALYSIS_API uint32_t ctl_mqt2_analysis_extended_fp_only(
    fpc_product_type_t product,
    uint16_t hw_id,
    mqt_analysis_settings_t settings,
    char* path_to_fmi,
    char* output_dir,
    uint32_t key);

#endif