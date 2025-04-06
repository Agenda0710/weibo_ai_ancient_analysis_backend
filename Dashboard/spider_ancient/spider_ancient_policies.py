import requests
import json
import re
import os
from html import unescape
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
# 定义BERT模型路径
bert_model_path = os.path.join(parent_dir, 'bert-policy-category')

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
tokenizer = BertTokenizer.from_pretrained(bert_model_path)
model = BertForSequenceClassification.from_pretrained(bert_model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# 以下函数保持不变...
def predict_category(text):
    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=256, return_tensors='pt').to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits, dim=1).item()
    return category_map.get(predicted_class_id, '未知')


def get_ancient_policies_information():
    url = "https://sousuoht.www.gov.cn/athena/forward/2B22E8E39E850E17F95A016A74FCB6B673336FA8B6FEC0E2955907EF9AEE06BE"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "athenaappkey": "Ij5L46bQ58IcxCxEe1JKr4p%2Fi29s8fMG%2F8u81yzHrHebMSWvbgJ3glQyn2mimSXUMIZnIRgo4PnLM6M%2FVfsXU5%2FHbE9%2F3KWhUY5pFmgHe84%2FWfdlHpKzRmy%2BNYwb35VAPJf0%2BpoPo1yEvtOhF7jJK2l8DvYL28NTxV5QLbHrub0%3D",
        "athenaappname": "%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2",
    }
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

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        try:
            data = response.json()
            policies_information = []
            for item in data["result"]["data"]["middle"]["list"]:
                cleaned_title = re.sub(r"<[^>]+>", "", unescape(item["title"]))
                date = item["time"].split()[0]
                category = predict_category(cleaned_title)
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
