from util import gen_find
import os
import json
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="input path")
args = parser.parse_args()

path = args.path

FailPath = os.path.join(path, 'Fail')
PassPath = os.path.join(path, 'Pass')

if __name__ == "__main__":
    try:
        if(os.path.exists(path)):
            if(not os.path.exists(FailPath)):
                os.mkdir(FailPath)
            if(not os.path.exists(PassPath)):
                os.mkdir(PassPath)
        else:
            print(path + "does not exists")
            sys.exit(-1);

        output = gen_find("*.json", path)

        for file in output:
            preName = os.path.basename(file).split('_result')[0]
            pattern = preName + "*"
            files = gen_find(pattern, path)
            test_result = 'Success'
            with open(file, mode='r', encoding='utf-8') as fh:
                json_data = json.load(fh)
                test_result = json_data['Success']

            for f in files:
                if(test_result == 'Success'):
                    newFile = os.path.join(PassPath, os.path.basename(f))
                else:
                    newFile = os.path.join(FailPath, os.path.basename(f))
                os.rename(f, newFile)

    except Exception as e:
        sys.exit(-1);
        print(e)

