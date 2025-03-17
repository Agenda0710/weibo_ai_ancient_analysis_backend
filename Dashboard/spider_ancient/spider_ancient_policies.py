import requests
import json
import re
from html import unescape
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 类别映射
category_map = {
    0: '经济',
    1: '国土规划与管理',
    2: '教育',
    3: '民生',
    4: '生态环境',
    5: '政治与行政',
    6: '卫生健康',
    7: '文化与社会',
    8: '科技与创新',
    9: '国防与安全',
    10: '市场监管与法治'
}

# 加载预训练的中文 BERT 分词器和模型
tokenizer = BertTokenizer.from_pretrained(r"D:\PythonProjects\weibo_django\Dashboard\bert-policy-category")
model = BertForSequenceClassification.from_pretrained(r"D:\PythonProjects\weibo_django\Dashboard\bert-policy-category")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def predict_category(text):
    # 对文本进行分词和编码
    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=256, return_tensors='pt').to(device)

    # 进行预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取预测结果
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits, dim=1).item()

    # 返回类别名称
    return category_map.get(predicted_class_id, '未知')


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
        "customFilter": {"operator": "and", "properties": []},
        "dataTypeId": "107",
        "filters": [],
        "granularity": "ALL",
        "isSearchForced": 0,
        "orderBy": "time",
        "pageNo": 1,
        "pageSize": 50,
        "searchBy": "title",
        "searchWord": "非物质文化遗产",
        "trackTotalHits": True
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    # 解析响应
    if response.status_code == 200:
        try:
            data = response.json()
            policies_information = []  # 最终存储结果的列表

            for item in data["result"]["data"]["middle"]["list"]:
                # 1. 清洗标题（去除HTML标签）
                cleaned_title = re.sub(r"<[^>]+>", "", unescape(item["title"]))

                # 2. 提取日期（只保留年月日）
                date = item["time"].split()[0]  # 从"2025-03-17 17:24:00"提取"2025-03-17"

                # 调用bert-policy-category进行预测
                category = predict_category(cleaned_title)

                # 3. 构建字典并添加到列表（分类暂时留空）
                policies_information.append({
                    "time": date,
                    "title": cleaned_title,
                    "category": category
                })

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
