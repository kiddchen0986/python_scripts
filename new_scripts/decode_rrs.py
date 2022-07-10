import json
import os

path = "/media/minchao/ext/code/gerrit/rec_setting/rec_settings/json/rrs/fpc1023/fpc1229_g175_smic_ss_rrs.json"
save_file = os.path.join(os.path.dirname(path), os.path.basename(path).split('.json')[0])

table = ""
groupName = []
with open(path) as fh:
    f = json.load(fh)
    for group in f['root']['doc']['data']['registerGroups']:
        groupName = ' '*4 + "." + group['groupName'].split('#')[1] + "="
        #print(groupName)
        table = table + groupName + '\n'
        for register in group['registers']:
            addr = "\"" + register['address'].split("0x ")[1]
            data = register['data'].split("0x ")[1]
            name = register['name']
            value = ' '*8 + addr + ' ' + data + ";" + "\""
            remainLen = 59 - len(value)
            record = value + ' '*remainLen + '// ' + name
            table = table + record + '\n'
            #print(record)
        table = table + 8*' ' + ',\n'
    print(table)



