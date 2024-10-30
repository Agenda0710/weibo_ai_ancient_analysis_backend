import requests


def get_hot_search_data():
    url = 'https://weibo.com/ajax/statuses/mineBand'
    headers = {
        'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; ULV=1730175311306:5:5:1:4321409565696.8564.1730175311246:1729781733548; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzTKemW_V4HvEdt04g_WBDoqxZ-V4m7FgjYKqOKtag01MrhBvS3tqRtbB8xNwFOmkxA==; PC_TOKEN=2b0b6853dc; ALF=1732869297; SUB=_2A25KJZ_hDeRhGeNG7VsV8SbFwz2IHXVpWp0prDV8PUJbkNANLRbAkW1NSzm19JDIpR8uObJ80qV3uRnjJawVYfHt; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; XSRF-TOKEN=WJlFLUvyRLqDe6Vtq2QCmE1v',
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
