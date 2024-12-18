import requests


def get_hot_search_data():
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        'Cookie': 'ALF=1736942111; SUB=_2A25KZGVPDeRhGeNG7VsV8SbFwz2IHXVpGPiHrDV8PUJbkNANLWrikW1NSzm19IqjANItdpQRJfS6vAZC0X4hCESk; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; PC_TOKEN=4d696b9fec; XSRF-TOKEN=smgh75Ey8z230dyxYS1RNQbL; _s_tentry=weibo.com; Apache=2278260953253.426.1734436246562; SINAGLOBAL=2278260953253.426.1734436246562; ULV=1734436246613:7:1:1:2278260953253.426.1734436246562:1731851135570; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbciA8deGx9L62h1QiAALi5vUAYuuViVmfOLbSFQFqvrv1nlBrNOKqXm7kBWeYGtmqcQKajDB9vpuSpOhL4x2LZ1KLPvIFnvGV0pOR0TFW94Qg==',
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
