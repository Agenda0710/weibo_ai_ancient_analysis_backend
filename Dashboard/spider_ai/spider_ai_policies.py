import csv
import requests
from Dashboard.spiders.spiderNews import classify_news

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'athenaappname': '%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2',
    'athenaappkey': 'gnFvwq4i4EdIs6HsXe%2FNUNgmsf%2Fqf8AfCR5FsTfrxPzKnTnNJfaNqgxscibjY8aOG5mTCwXelZ9QWhFofNklU5Gbj0jAtIIsvKZDJy2YPXr8FfGQ%2BC%2B%2FaL6J%2F7ehImM1ZW97aVVqJO8XnoD0e4NUzeL1cQogXInl46PbGB7AJrs%3D'
}

url = 'https://sousuoht.www.gov.cn/athena/forward/2A40CF891850CF7ED2F0FA6369ECBB88?t=zhengce&timetype=timeqb&mintime=&maxtime=&sort=score&searchfield=&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&n=5&inpro='

policies_information = []


def get_ai_policies_information():
    for j in range(1, 5):
        params = {
            'sortType': 1,
            'p': j,
            'q': '人工智能',
        }

        response = requests.get(url, headers=headers, params=params)
        response.encoding = 'utf-8'
        data_list = response.json()['result']['data']['searchVO']['catMap']['zhongyangfile']['listVO']

        for i in range(len(data_list)):
            time = data_list[i]['pubtimeStr']
            title = data_list[i]['title']
            category = classify_news(title)
            policies_information.append({'time': time, 'title': title, 'category': category})

    return policies_information


def write_to_csv(policies_information):
    # 将政策名称保存到CSV文件
    with open('policies.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['time', 'title', 'category'])
        for policy_information in policies_information:
            writer.writerow([policy_information['time'], policy_information['title'], policy_information['category']])
