import json
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from util import gen_find

style.use('ggplot')

test_dict = {
    'Module Quality Test 2': ['Log', 'snr', 'blob', 'udr']
}

def analyze(json_file, test):
    with open(json_file, encoding='utf-8', mode='r') as f:
        json_dict = json.load(f)
        test_data = (json_file, -1, -1, -1)
        try:
            for item in json_dict['TestReportItems']:
                if item['Name'] == test:
                    snr = item['Result']['TestLog']['Steps']['analysis']['Items']['result']['Snr']['SnrDb']
                    blob = item['Result']['TestLog']['Steps']['analysis']['Items']['result']['Blob']['BlobCount']
                    udr = item['Result']['TestLog']['Steps']['analysis']['Items']['result']['Uniformity']['Udr']

                    test_data = (json_file, snr, blob, udr)
                    break

        except KeyError as e:
            print('KeyError {} happens in {}, might be no {} test result, regard all -1 of {}'.format(e, json_file, test, test_dict[test][1:]))
            #test_data = (json_file, -1, -1, -1)

        else:
            return test_data

def execute(path, test):
    all_jsons = gen_find('*.json', path)
    for file in all_jsons:
        yield analyze(file, test)

def summary(generator, csv_path, test):
    df = pd.DataFrame(generator, columns=test_dict[test])
    df.to_csv(csv_path, encoding='utf-8', index=False)

    print(df.describe())

    fig = plt.figure()
    ax_list = []
    for i, v in enumerate(test_dict[test][1:]):
        ax_list.append(fig.add_subplot(len(test_dict[test][1:]), 1, i + 1))

    for i, ax in enumerate(ax_list):
        ax.hist(df[test_dict[test][i + 1]], rwidth=0.5, bins=100, label=test_dict[test][i + 1], color='b')
        ax.legend()

    plt.show()

if __name__ == "__main__":
    try:
        generator = execute(sys.argv[1], 'Module Quality Test 2')
        summary(generator, sys.argv[2], 'Module Quality Test 2')
    except IndexError as e:
        print("python analyze_data.py <log_path> <csv_file_name>")
    except Exception as e:
        print("Error {} caught in script".format(e))