import sys
import pandas as pd
import json
from collections import OrderedDict
from util import gen_find

log_dict = OrderedDict()
unique_sensors_dict = {}

def get_data(json_file):
    with open(json_file, encoding='utf-8', mode='r') as f:
        json_dict = json.load(f)
        sensor_id = ''
        if json_dict['Identity']['SensorIdReadStatus'] == 'FPC_SUCCESS':
            sensor_id = json_dict['Identity']['SensorId']
            if sensor_id not in unique_sensors_dict:
                if json_dict['Success'] == 'Success':
                    unique_sensors_dict[sensor_id] = [1, 1]  #total, success
                else:
                    unique_sensors_dict[sensor_id] = [1, 0]
            else:
                if json_dict['Success'] == 'Success':
                    unique_sensors_dict[sensor_id][1] += 1
                    unique_sensors_dict[sensor_id][0] += 1
        try:
            test_dict = OrderedDict({'sensorid': sensor_id, 'result' : json_dict['Success']})
            for _, item in enumerate(json_dict['TestReportItems']):
                test_dict[item['Name'].lower()] = item['Result']['TestMethodConclusion']

            log_dict[json_file] = test_dict

        except KeyError as e:
            print('KeyError {} happens in {}, no test result'.format(e, json_file))

def parse(path):
    all_jsons = gen_find('*.json' ,path)
    for file in all_jsons:
        get_data(file)

def get_col():
    ordered_col_dict = OrderedDict()
    ordered_col_dict['Log'] = ''
    ordered_col_dict['sensorid'] = ''
    ordered_col_dict['result'] = [0, 0]

    for test_results in log_dict.values():
        for test in test_results.keys():
            if test.lower() not in ordered_col_dict.keys():
                ordered_col_dict[test.lower()] = [0, 0]     #[total, success]

    return ordered_col_dict

def get_csv_data(ordered_col_dict):
    csv_data = []
    for log, test_results in log_dict.items():
        result = [log, test_results['sensorid']]
        for c in list(ordered_col_dict.keys())[2:]:
            if c in test_results.keys():
                if test_results[c] == 'Success':
                    ordered_col_dict[c][1] += 1

                #TODO is NotRun a fail?
                if test_results[c] != 'NotRun':
                    ordered_col_dict[c][0] += 1
                result.append(test_results[c])
            else:
                result.append('NotRun')

        test_results['sensorid']
        csv_data.append(result)

    yields = [float(ordered_col_dict[col][1]) / ordered_col_dict[col][0] * 100 for col in list(ordered_col_dict.keys())[2:] if ordered_col_dict[col][0] != 0]
    yields.insert(0, '')    #Log
    yields.insert(1, '')    #sensorid

    #insert yield to 1st row
    csv_data.insert(0, yields)

    return csv_data

def get_unique_sensor_yield():
    sensor_yield = [(key, value[1] / value[0]) for key, value in unique_sensors_dict.items()]
    print(sensor_yield)

def execute(log_path, csv_file_name):

    parse(log_path)
    print("{} files processed to csv...".format(len(log_dict)))
    print('{} unique sensors'.format(len(unique_sensors_dict)))

    ordered_col_dict = get_col()

    csv_data = get_csv_data(ordered_col_dict)

    get_unique_sensor_yield()

    df = pd.DataFrame(csv_data, columns=list(ordered_col_dict.keys()))
    df.to_csv(csv_file_name, encoding='utf-8', index=False)

    return csv_data

if __name__ == "__main__":
    try:
        execute(sys.argv[1], sys.argv[2])
    except IndexError as e:
        print("python parse_json.py <log_path> <csv_file_name>, error".format(e))
    except Exception as e:
        print("Error {} caught in script".format(e))
