import sys
import re
import pandas as pd
import time
from util import gen_find

test_result_dict = {}

csv_cols = ["Log", "Result"]
csv_data = []
mtt_yield = {}

def get_cols(log):

    with open(log, encoding="utf-8") as f:
        text = f.read()
        test_name = re.findall(r"\n*.*\n*-> Test (.*) \(", text)

        for name in test_name:
            if name.lower() not in csv_cols:
                csv_cols.append(name.lower())
                mtt_yield[name.lower()] = [0, 0]    #[total, success]

    return csv_cols

def get_results(log):
    result = []
    result.append(log)

    with open(log, encoding="utf-8") as f:
        text = f.read()
        success = re.findall(r"==> Module Test: Success", text)

        result.append("Success") if success else result.append("Fail")
        if success:
            mtt_yield['Result'][1] += 1

        for name in csv_cols[2:]:
            pattern = re.findall(r"\n*.*\n*"+ name + r": (.*) \(", text)
            result.append(pattern[0]) if pattern else result.append("NotRun")
            if pattern:
                mtt_yield[name][0] += 1
                if pattern[0] == 'Success':
                    mtt_yield[name][1] += 1


    csv_data.append(result)

def extract_logs(path):
    all_logs = gen_find('*_log.txt', path)

    for i, file in enumerate(all_logs):
        get_cols(file)
        get_results(file)

    return i + 1

def execute(path, csv_path):
    begin = time.time()

    mtt_yield["Result"] = [0, 0]

    logs = extract_logs(path)
    print("{} files processed to csv...".format(logs))

    mtt_yield['Result'][0] = logs

    yields = [float(mtt_yield[col][1]) / mtt_yield[col][0] * 100 for col in csv_cols[1:]]
    yields.insert(0, '')

    csv_data.insert(0, yields)

    df = pd.DataFrame(csv_data, columns=csv_cols)
    df.to_csv(csv_path, encoding='utf-8', index=False)

    print("Finish {}s".format(time.time() - begin))

if __name__ == "__main__":
    try:
        execute(sys.argv[1], sys.argv[2])
    except IndexError as e:
        print("python parse_txt.py <log_path> <csv_file_name>")
    except Exception as e:
        print("Error {} caught in script".format(e))