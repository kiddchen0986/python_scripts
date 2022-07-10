from LogParser import logParserYieldReport

path = r'D:\Logs\xiaomi\1291\ofilm\20180419\1007-00-MT'
path_yield_xls = 'yield_html.xls'

logParserYieldReport(path, '*.html', path_yield_xls).analyze()

'''
results = list(yield_results)
df = pd.DataFrame(results)
df.sort_values(by='result', ascending=False, inplace=True)
print(df.describe())

test_columns = df.columns
yield_row = pd.DataFrame([df.mean()], columns=test_columns[1:])
new_df = pd.concat([yield_row, df], ignore_index=True)
final_df = new_df[test_columns]
final_df.to_excel(path_yield_xls, encoding='utf-8')

black = generate_mqt_data(path_black)
pink = generate_mqt_data(path_pink)
blue = generate_mqt_data(path_blue)
white = generate_mqt_data(path_white)

total1 = generate_mqt_data(path_blue)
total1['snr'].dropna(inplace=True)
_, axes = plt.subplots(1, 2)
axes[0].hist(total1['snr'], bins=np.arange(0, 15, 0.2), alpha=0.5, label='blue', color='b')
axes[0].set_xticks([0,4, 5 ,6,7,8,9,10,11,12,13])
axes[0].legend(loc='best')
axes[0].set_xlabel('snr')
axes[0].set_ylabel('number of modules')

total2 = generate_mqt_data(path_pink)
total2['snr'].dropna(inplace=True)
axes[1].hist(total2['snr'], bins=np.arange(0, 15, 0.2), alpha=0.5, label='pink', color='r')
axes[1].set_xticks([0,4, 5 ,6,7,8,9,10,11,12,13])
axes[1].legend(loc='best')

axes[1].set_xlabel('snr')
axes[1].set_ylabel('number of modules')

#total['snr'].dropna(inplace=True)
#lower = [i for i in total['snr'] if i <= lower_val]
#print('total', len(lower) / len(total['snr']) * 100)

blue['snr'].dropna(inplace=True)
#lower = [i for i in blue[1]['snr'] if i <= lower_val and i > 0]
#print('blue', len(lower) / len(blue[1]['snr']) * 100)

black['snr'].dropna(inplace=True)
lower = [i for i in black['snr'] if i <= lower_val and i > 0]
print('black', len(lower) / len(black['snr']) * 100)

pink['snr'].dropna(inplace=True)
lower = [i for i in pink['snr'] if i <= lower_val and i > 0]
print('pink', len(lower) / len(pink['snr']) * 100)

blue['snr'].dropna(inplace=True)
lower = [i for i in blue['snr'] if i <= lower_val and i > 0]
print('blue', len(lower) / len(blue['snr']) * 100)

white['snr'].dropna(inplace=True)
lower = [i for i in white['snr'] if i <= lower_val and i > 0]
print('white', len(lower) / len(white['snr']) * 100)

df_list = [black['snr'],
           pink['snr'],
           blue['snr'],
           white['snr']]
colors = ['black', 'pink', 'blue', 'white']

f, axes = plt.subplots(4,1)
for i, value in enumerate(df_list):
    axes[i].hist(value, bins=np.arange(0, 15, 0.2), alpha=0.5, label=colors[i], color=np.random.rand(1, 3))
    axes[i].set_xticks([0,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,12,13])
    axes[i].legend(loc='best')

'''
