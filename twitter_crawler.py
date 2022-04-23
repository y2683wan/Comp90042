import json
import requests
import time
import os

url = "https://api.twitter.com/2/tweets?ids="
param = {'tweet.fields': 'created_at,entities,source', 'expansions': 'in_reply_to_user_id'}
header = {'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAIxRbgEAAAAADvbPSYRAKI04Jjvgn%2BPgNPs36a0%3D3nz80k7S0FuiC47LCnU686DLY4Sot6n71Mlj7aaqL9bFXOIJB2'}

file = './project-data/dev.data.txt'
folder = './project-data/dev-tweet-objects/'
f = open(file, 'r')
lines = f.readlines()
f.close()

with open('./project-data/logs.txt', 'r') as f:
    lists = f.readlines()

non_tweets = []
for line in lists:
    non_tweets += line.strip('\n').split(',')

for line in lines:

    temp = line.strip('\n').split(',')
    # check if already exists
    waiting = []
    for unit in temp:
        if os.path.exists(folder+unit+'.json'):
            print(unit+'.json', 'already exists')
        elif unit in non_tweets:
            pass
        else:
            waiting.append(unit)
    if len(waiting) == 0:
        continue
    else:
        temp_url = url + ','.join(waiting)
    print('Crawling from', temp_url)
    res = requests.get(url=temp_url,params=param, headers=header)

    if res.status_code == 200:       
        items = json.loads(res.content)
        if 'errors' in items.keys():
            print('Error Message', items)
            with open('./project-data/logs.txt', 'a+') as f:
                f.write(','.join(waiting)+'\n')
            continue

        for item in items['data']:
            with open(folder+item['id']+'.json', 'w+', encoding='utf-8') as f:
                print('downloading', item['id']+'.json')
                f.write(json.dumps(item, indent=4, ensure_ascii=False))
    else:
        print(res.status_code)
        print(res.content)
        time.sleep(5)