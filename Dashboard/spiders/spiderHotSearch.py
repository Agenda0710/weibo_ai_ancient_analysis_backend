import requests


def get_hot_search_data():
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; ULV=1731851135570:6:1:1:4133330521076.9653.1731851135541:1730175311306; PC_TOKEN=3c4cfa8430; ALF=1734835068; SUB=_2A25KO54rDeRhGeNG7VsV8SbFwz2IHXVpOJ_jrDV8PUJbkNAGLRLgkW1NSzm19AAQfOYvAklpwz-zq6wZDjZg0GBo; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; XSRF-TOKEN=ixlYZJNGg_8AJDYGL0VaKIrf; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzdpXwP0B53Nvrd8o70HP3CtrmmgHVXxhcx0XOadspJxnzCfUF03Ov4drtasAozuZdw==',
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
