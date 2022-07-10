import sys
import re
import fnmatch
import os
import pandas as pd
from matplotlib import pyplot as plt
import logging

logging.basicConfig(level=logging.ERROR)

def gen_find(log_pattern, log_path):
    for path, _, file_list in os.walk(log_path):
        for name in fnmatch.filter(file_list, log_pattern):
            yield os.path.join(path, name)

def main(file):
    for file in gen_find('*.txt', file):
        with open(file, encoding='utf-8', mode='r') as f:
            count = 0
            for line in f:
                count += 1
                memory = re.search(r'total : (.*)\(max: (.*)\)', line)
                if not memory:
                    continue
                try:
                    yield {'used' :int(memory.group(1)), 'max' :int(memory.group(2))}
                except Exception as e:
                    logging.error('Incorrect format happened in line: {0}, error message: {1}'.format(count, e))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        logging.error(" Script arguments:analyze_memory.py log_path excel_name")
        exit(-1)

    res = main(sys.argv[1])
    df = pd.DataFrame(res)
    df.to_excel(sys.argv[2], encoding='utf-8', index=False)

    df.plot()

    plt.show()