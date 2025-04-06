import requests
import json
import re
from html import unescape

def get_ancient_policies_information():
    # 目标 URL
    url = "https://sousuoht.www.gov.cn/athena/forward/2B22E8E39E850E17F95A016A74FCB6B673336FA8B6FEC0E2955907EF9AEE06BE"

    # 构造请求头
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "athenaappkey": "Ij5L46bQ58IcxCxEe1JKr4p%2Fi29s8fMG%2F8u81yzHrHebMSWvbgJ3glQyn2mimSXUMIZnIRgo4PnLM6M%2FVfsXU5%2FHbE9%2F3KWhUY5pFmgHe84%2FWfdlHpKzRmy%2BNYwb35VAPJf0%2BpoPo1yEvtOhF7jJK2l8DvYL28NTxV5QLbHrub0%3D",
        "athenaappname": "%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2",
    }

    # 构造请求参数
    payload = {
        "code": "17da70961a7",
        "historySearchWords": ["非物质文化遗产", "非物质文化", "大模型"],
        "dataTypeId": "14",
        "orderBy": "time",
        "searchBy": "title",
        "appendixType": "",
        "granularity": "ALL",
        "trackTotalHits": True,
        "beginDateTime": "",
        "endDateTime": "",
        "isSearchForced": 0,
        "filters": [],
        "pageNo": 1,
        "pageSize": 50,
        "customFilter": {"operator": "and", "properties": []},
        "searchWord": "非物质文化遗产"
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    # 解析响应
    if response.status_code == 200:
        try:
            data = response.json()
            policies_information = []  # 最终存储结果的列表
            seen = set()  # 用于记录已经出现过的信息

            for item in data["result"]["data"]["middle"]["list"]:
                # 1. 清洗标题（去除HTML标签）
                cleaned_title = re.sub(r"<[^>]+>", "", unescape(item["title"]))

                # 2. 提取日期（只保留年月日）
                date = item["time"].split()[0]  # 从"2025-03-17 17:24:00"提取"2025-03-17"

                # 生成唯一标识
                unique_key = (date, cleaned_title)

                if unique_key not in seen:
                    # 3. 构建字典并添加到列表（分类暂时留空）
                    policies_information.append({
                        "time": date,
                        "title": cleaned_title,
                    })
                    seen.add(unique_key)

            for info in policies_information:
                print(f"日期：{info['time']}")
                print(f"标题：{info['title']}")
                print("-" * 40)

            return policies_information

        except (KeyError, json.JSONDecodeError) as e:
            print(f"解析响应失败：{str(e)}")
            print("原始响应内容：")
            print(response.text)
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print(f"响应内容：{response.text}")


if __name__ == '__main__':
    get_ancient_policies_information()