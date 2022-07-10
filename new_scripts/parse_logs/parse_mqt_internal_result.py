from util import gen_find
from util import CreateFolder
import json
import pandas as pd
from collections import OrderedDict
import matplotlib.pyplot as plt
import os
import shutil

path = r"C:\project\1228-G175\output_0.7"
output_summary = os.path.join(path, 'mqt_internal_summary.xls')
fixPattern_path = os.path.join(path, "fixPatternTest")
CreateFolder(fixPattern_path)

internal_result = []
fixPatternLimit = 15
fixPatternPass = 0
fixPatternAll = 0

title = "signal_power;contrast_strength;noise_fp;noise_thermal;noise_thermal_lp_x;noise_thermal_lp_y" \
        ";saturation_fraction;low_pass_fraction;high_freq_noise_fraction;best_angle;displacement;displacement_error" \
        ";displacement_fit_error;displacement_curvature;displacement_rel_curvature;displacement_max_error"

files = gen_find("*.json", path)
for file in files:
    with open(file, encoding='utf-8', mode='r') as fh:
        content = json.load(fh)
        test_data = OrderedDict()
        for  test in content['sequence']:
            if test['name'] == 'read_analysis_input':
                test_data['fmi_name'] = test['fmi_file_name']
            if test['name'] == 'module_quality':
                test_data['fmi_rename'] = test['measurement']['result']['zebra_image_re-analyze_result']
                if 'snr_db' in test['analysis']['result']['snr']:
                    test_data['snr_db'] = test['analysis']['result']['snr']['snr_db']
                else:
                    test_data['snr_db'] = -1

                if 'fixed_pattern_pixels' in test['analysis']['result']['fixed_pattern']:
                    test_data['fixed_pattern_pixels'] = test['analysis']['result']['fixed_pattern']['fixed_pattern_pixels']
                    fixPatternAll = fixPatternAll + 1
                    if(test_data['fixed_pattern_pixels'] <= fixPatternLimit):
                        fixPatternPass = fixPatternPass + 1
                    else:
                        srcFmiFile = os.path.join(path, test['measurement']['result']['zebra_image_re-analyze_result'])
                        dstFmiFile = os.path.join(fixPattern_path, test['measurement']['result']['zebra_image_re-analyze_result'])
                        shutil.copyfile(srcFmiFile, dstFmiFile)
                        fixPatternFileName = test['measurement']['result']['zebra_image_re-analyze_result'].split('_zebra_image')[0] + '_fixed_pattern_image!56_72_1.raw'
                        srcFixPatternFile = os.path.join(path, fixPatternFileName)
                        dstFixPatternFile = os.path.join(fixPattern_path, fixPatternFileName)
                        shutil.copyfile(srcFixPatternFile, dstFixPatternFile)

                else:
                    test_data['fixed_pattern_pixels'] = -1
                test_data['signal_power'] = test['restricted']['values']['value0']
                test_data['contrast_strength'] = test['restricted']['values']['value1']
                test_data['noise_fp'] = test['restricted']['values']['value2']
                test_data['noise_thermal'] = test['restricted']['values']['value3']
                test_data['noise_thermal_lp_x'] = test['restricted']['values']['value4']
                test_data['noise_thermal_lp_y'] = test['restricted']['values']['value5']
                test_data['saturation_fraction'] = test['restricted']['values']['value6']
                test_data['low_pass_fraction'] = test['restricted']['values']['value7']
                test_data['high_freq_noise_fraction'] = test['restricted']['values']['value8']
                test_data['best_angle'] = test['restricted']['values']['value9']
                test_data['displacement'] = test['restricted']['values']['value10']
                test_data['displacement_error'] = test['restricted']['values']['value11']
                test_data['displacement_fit_error'] = test['restricted']['values']['value12']
                test_data['displacement_curvature'] = test['restricted']['values']['value13']
                test_data['displacement_rel_curvature'] = test['restricted']['values']['value14']
                test_data['displacement_max_error'] = test['restricted']['values']['value15']
                test_data['noise_thermal_lp_x/noise_thermal_lp_y'] =  test_data['noise_thermal_lp_x']/test_data['noise_thermal_lp_y']
        if(test_data):
            internal_result.append(test_data)

print('fixPatternPass rate is {}'.format(fixPatternPass/fixPatternAll))

df = pd.DataFrame(internal_result)
df.to_excel(output_summary, encoding='utf-8')

fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

ax0.hist(df['noise_thermal_lp_x'], bins=20, label='noise_thermal_lp_x')
ax0.set_title('noise_thermal_lp_x')

ax1.hist(df['noise_thermal_lp_y'], bins=20, label='noise_thermal_lp_y')
ax1.set_title('noise_thermal_lp_y')

ax2.hist(df['noise_thermal_lp_x/noise_thermal_lp_y'], bins=20, label='noise_thermal_lp_x/noise_thermal_lp_y')
ax2.set_title('noise_thermal_lp_x/noise_thermal_lp_y')

plt.show()

