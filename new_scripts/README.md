#Prerequisites
The scripts work in Python3 32bit, and might not be compatible with Python2;
Anaconda3 package is preferred to set up Python dev environment, which can be downloaded from https://www.anaconda.com/download/ or https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

#parse_logs
    MTT yield in one script
        **generate_report.py** generates all the yield analysis reports (including excel files and distribution images)
        
    General MTT yield report
        **parse_json.py** is using MTT **json** & **html**(ofilm) logs to generate excel yield report (preferred);
            xx_yield.xls shows all the yield based on the logs
            xx_yield_sensor.xls shows all the yield based on modules
            
        **parse_txt.py** is using MTT **txt** logs to generate csv yield report;
		
    MTT test data analysis
        **analyze_xxx.py** is using MTT **json** or txt logs to analyze MQT, MQT2, Cap 1&2, CTL detective pixels, 
        including CB/ICB, swing CB/ICB, image drive and image constant, adf_cal;
        Wafer and host information can be got to compare the data between different hosts and lots;
        Refer to LogParser.py for key implementation;
        		
	Module House log clean up
		**util/format_ofilm_json** is to convert incorrect json from ofilm to correct one;
		**util/split_truly_json** is to split merged txt & json logs from Truly;
		
	MTT dash
	    Play with mtt_dash.py & mtt_dropdown_dash.py to generate html based on dash table report;
	    
    Known issues
        Only support MTT15+ due to different log formats in different MTT releases

#run_tests
    Dead pixels, image_constant and blob tests are supported

#run_spi
    access spi via hal layer



