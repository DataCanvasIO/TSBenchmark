import re
import pandas as pd

log = r"D:\workspace\DAT\benchmark-ts\log\dl_multi40_03091910.log"
file = open(log)

current_trial_no = ""
results = []
params = {}
data_name = ""

for line in file:

    if re.match('Trial No:', line):
        current_trail_no = line.split(":")[1][:-1]
        params['trial_no'] = current_trail_no

        if params['trial_no'] in ['34', '36']:
            print('')

    elif line[0:1] == '(' and line[2:3] == ')':
        key = line.split(":")[0][4:]
        value = line.split(":")[1].replace(' ', '')[:-1]
        params[key] = value
    elif re.match('========== data_name', line):
        data_name = line.split(':')[1].replace(' ', '')[:-1]
    elif re.match('.*best_trial_no:.*', line):
        params['reward'] = line.split('reward:')[1].split(',')[0]
        params['data_name'] = data_name
        results.append(params)
        params = {}
        current_trail_no = ""
for result in results:
    print(result)

file.close()

df = pd.DataFrame(results)
print(df.head().T)
df.to_csv(r'result_log\dl_multi40_03091910.csv', index=False)
