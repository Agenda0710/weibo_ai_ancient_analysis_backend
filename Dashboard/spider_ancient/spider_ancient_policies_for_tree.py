import csv

import requests

url = 'https://sousuo.www.gov.cn/search-gov/data?'

departmental_documents_list = []
official_documents_list = []
other_files_list = []
bulletins_list = []
for i in range(1, 7):
    params = {
        't': 'zhengcelibrary',
        'q': '人工智能',
        'timetype': 'timeqb',
        'sort': 'pubtime',
        'sortType': 1,
        'searchfield': 'title',
        'p': i,
        'n': 5,
        'type': 'gwyzcwjk'
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'cookie': 'wdcid=7b607c355853c386; wdlast=1734966326; arialoadData=false'
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json().get('searchVO').get('catMap')

    departmental_documents = data['bumenfile']['listVO']
    for departmental_document in departmental_documents:
        time = departmental_document['pubtimeStr']
        title = departmental_document['title']
        departmental_documents_list.append({'title': title, 'time': time})

    bulletins = data['gongbao']['listVO']
    for bulletin in bulletins:
        title = bulletin['title']
        time = bulletin['pubtimeStr']
        bulletins_list.append({'title': title, 'time': time})

    official_documents = data['gongwen']['listVO']
    for official_document in official_documents:
        title = official_document['title']
        time = official_document['pubtimeStr']
        official_documents_list.append({'title': title, 'time': time})

    other_files = data['otherfile']['listVO']
    for other_file in other_files:
        title = other_file['title']
        time = other_file['pubtimeStr']
        other_files_list.append({'title': title, 'time': time})

# 合并所有列表
all_items = other_files_list + official_documents_list + departmental_documents_list + bulletins_list

# 去除重复项，以"title"和"time"为唯一标识
unique_items = []
seen = set()
for item in all_items:
    identifier = (item['title'], item['time'])
    if identifier not in seen:
        unique_items.append(item)
        seen.add(identifier)

# 写入CSV文件
filename = 'ai_policies_for_trees.csv'
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['time', 'title'])

    # 写入列标题
    writer.writeheader()

    # 写入数据行
    for item in unique_items:
        writer.writerow({'time': item['time'], 'title': item['title']})

print(f"Data has been written to {filename}")
