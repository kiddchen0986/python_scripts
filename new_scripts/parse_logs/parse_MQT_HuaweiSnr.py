#https://fpc-jira.fingerprint.local/jira/browse/CET-9
#Analyze MQT and Huawei SNR test

import sys
import re
import pandas as pd
from util import gen_find
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

csv_data = []

def get_results(log:str):
    result = []
    result.append(log)

    with open(log, encoding="utf-8") as f:
        text = f.read()
        res = re.findall(r"snr: (.*) \(limit: >=", text)
        if len(res) > 0:
            result.append(float(res[0]))

        res = re.findall(r"SNRUGnewresult(.*) signalnew", text)
        if len(res):
            result.append(float(res[0]))

        res = re.findall(r"signalnew (.*) noisenew", text)
        if len(res) > 0:
            result.append(float(res[0]))

        res = re.findall(r"noisenew (.*) activeArea", text)
        if len(res):
            result.append(float(res[0]))

    if len(result) == 5:
        csv_data.append(result)

def extract_logs(path):
    all_logs = gen_find('*_log.txt', path)
    for i, file in enumerate(all_logs):
        get_results(file)

    return i + 1

def execute(path, csv_path):
    logs = extract_logs(path)
    df = pd.DataFrame(csv_data, columns=['Log', 'MQT', 'Huawei_SNR', 'Huawei_Signal_Strength', 'Huawei_Noise'])

    print(df.describe())

    df.to_csv(csv_path, encoding='utf-8', index=False)

    fig = plt.figure()

    ax1 = fig.add_subplot(4, 1, 1)
    ax1.hist(df['Huawei_SNR'], label='Huawei_SNR', bins=20)
    ax1.hist(df['MQT'], label='MQT', bins=20, alpha=0.5)

    ax2 = fig.add_subplot(4, 1, 2)
    ax2.hist(df['Huawei_Signal_Strength'], label='Huawei_Signal_Strength', bins=20)

    ax3 = fig.add_subplot(4, 1, 3)
    ax3.hist(df['Huawei_Noise'], label='Huawei_Noise', bins=20)

    ax4 = fig.add_subplot(4, 1, 4)
    ax4.scatter(range(len(df['MQT'])), df['MQT'], label='MQT SNR', c='r')
    ax4.scatter(range(len(df['Huawei_SNR'])), df['Huawei_SNR'], label='Huawei SNR', c='b')
    ax4.set_ylim(0)
    ax4.set_title('MQT SNR vs Huawei SNR')
    ax4.set_ylabel('SNR value')

    ax1.legend(loc=2)
    ax2.legend(loc=2)
    ax3.legend(loc=2)
    ax4.legend(loc=2)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python parse_snr.py <log_path> <csv_file_name>")
        sys.exit(1)

    execute(sys.argv[1], sys.argv[2])