import requests
from Dashboard.config import WEIBO_COOKIE


def get_hot_search_data():
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        'Cookie': WEIBO_COOKIE,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    response = requests.get(url, headers=headers)
    hot_search_list = []
    if response.status_code == 200:
        for item in response.json()['data']['realtime']:
            word = item.get('word')  # 安全获取字段
            description = item.get('num', '无描述')  # 默认描述
            hot_search_list.append({'content': word, 'description': description})

    return hot_search_list


if __name__ == '__main__':
    print(get_hot_search_data())
