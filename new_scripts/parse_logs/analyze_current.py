from LogParser import logParserCurrent
import sys
import pandas as pd

path = r'C:\project\Aggassi\DM1PBBM0'

if __name__ == "__main__":
    try:
        parser = logParserCurrent(path)
        out = parser.yield_results()
        df = pd.DataFrame(out)
        df.to_excel('C:\\project\\Aggassi\\DM1PBBM0\\summary_current.xls', encoding='utf-8')

        fig, axes = plt.subplots(nrows=1, ncols=2)
        ax0, ax1 = axes.flatten()

        ax0.hist(df['IDDD_Active'].dropna(), bins=20, label='IDDD_Active')
        ax0.set_title('IDDD_Active')

        ax1.hist(df['IDDD_AFDSleep'].dropna(), bins=20, label='IDDD_AFDSleep')
        ax1.set_title('IDDD_AFDSleep')

        plt.show()

        '''
        df.dropna(inplace=True)
        print(df.describe())

        if len(df.columns) == 24:
            _, axes = plt.subplots(4, 5)
            for i in range(4):
                for j in range(5):
                    c = df.columns[4+j+i*5]
                    axes[i, j].hist(df[c], label=c, color=np.random.rand(3))
                    axes[i, j].legend(loc='best')

        elif len(df.columns) == 14:
            _, axes = plt.subplots(2, 5)
            for i in range(2):
                for j in range(5):
                    c = df.columns[4 + j + i * 5]
                    axes[i, j].hist(df[c], label=c, color=np.random.rand(3))
                    axes[i, j].legend(loc='best')

        plt.show()
        '''

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))