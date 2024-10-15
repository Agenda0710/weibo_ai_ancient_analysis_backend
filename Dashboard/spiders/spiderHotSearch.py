import requests


def get_hot_search_data():
    url = 'https://weibo.com/ajax/statuses/mineBand'
    headers = {
        'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzd-UAmI7T_vqc1YHRl2Bdmp_M8tZdv4HGIKRwOVc9d1N_-38koOLeOCm84dGbLOOzA==; ULV=1728978218115:2:2:2:4342820146727.9526.1728978218077:1728390722842; ALF=1731572878; SUB=_2A25KClfcDeRhGeNG7VsV8SbFwz2IHXVpZtUUrDV8PUJbkNAGLUrMkW1NSzm19AyWoBzzmfJy2e6MweeaUz79tXIk; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; PC_TOKEN=5a03a8b4ee; XSRF-TOKEN=Cn-jVsw3EAcNXZKoZJPAxZ2T',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    response = requests.get(url, headers=headers)
    hot_search_list = []
    if response.status_code == 200:
        for item in response.json()['data']['realtime']:
            hot_search_list.append(item['word'])

    return hot_search_list


if __name__ == '__main__':
    print(get_hot_search_data())
