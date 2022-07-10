#Prerequisites
The scripts work in Python3 32bit, and might not be compatible with Python2;
Anaconda3 package is preferred to set up Python dev environment, which can be downloaded from https://www.anaconda.com/download/ or https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

#parse_logs
    MTT yield report
        **parse_json.py** is using MTT **json** logs to generate csv yield report (preferred);
        **parse_txt.py** is using MTT **txt** logs to generate csv yield report;

    MTT test data analysis
        **analyze_mqt2.py** is using MTT **json** logs to collect udr, blob, snr data;

#run_tests
    Dead pixels, image_constant and blob tests are supported

#run_spi
    access spi via hal layer



