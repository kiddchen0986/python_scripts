from LogParser import logParserCtlImageDrive
import sys

if __name__ == "__main__":
    try:

        path = r'D:\Logs\xiaomi\1291\ofilm\20180419'
        path_xls = r'1291_E1_image_drive.xls'

        logParserCtlImageDrive(path, '*.json', path_xls).analyze()

        # compare the difference between lots
        '''wafer_parser = LogParser_wafer_info(path, '')
        out_wafer = wafer_parser.yield_results()
        df_wafer = pd.DataFrame(out_wafer)
        df_wafer.dropna(inplace=True)

        df_image_drive_wafer = df_wafer.merge(df_image_drive)

        lot_ids = list(set(df_wafer['lot_id']))

        df_list = []
        for lot_id in lot_ids:
            df_list.append(df_image_drive_wafer[df_image_drive_wafer['lot_id'] == lot_id])

        for index, item in enumerate(image_drive_parser.data_columns[2:]):
            plt.subplot(3, 6, index + 1)
            for i, df in enumerate(df_list):
                plt.hist(df[item], label='lot_id: ' + df['lot_id'], histtype='stepfilled', alpha=0.5)
            plt.title(item)
            plt.legend(loc='best')

        plt.show()

        # compare the difference between hosts
        host_ids = list(set(df_image_drive['host_id']))
        df_list = []
        for host_id in host_ids:
            df_list.append(df_image_drive_wafer[df_image_drive_wafer['host_id'] == host_id])

        for index, item in enumerate(image_drive_parser.data_columns[2:]):
            plt.subplot(3, 6, index + 1)
            for i, df in enumerate(df_list):
                plt.hist(df[item], label='test station: ' + df['host_id'], histtype='stepfilled', alpha=0.5)
            plt.title(item)
            plt.legend(loc='best')
        '''

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))