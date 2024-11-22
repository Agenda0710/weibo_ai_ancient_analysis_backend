# def classify_news(news_text):
#     # 加载已训练好的模型
#     classifier = joblib.load(r'D:\PythonProjects\weibo_django\Dashboard\learning_model\logistic_regression_model.pkl')
#     # 加载 TF-IDF 向量化模型
#     tfidf_model = joblib.load(r'D:\PythonProjects\weibo_django\Dashboard\learning_model\tfidf_vectorizer.pkl')
#     # 加载标签编码器
#     le = joblib.load(r'D:\PythonProjects\weibo_django\Dashboard\learning_model\label_encoder.pkl')
#
#     # 清理文本
#     def clear_character(sentence):
#         pattern1 = '\[.*?\]'
#         pattern2 = re.compile('[^\u4e00-\u9fa5^a-z^A-Z^0-9]')
#         line1 = re.sub(pattern1, '', sentence)
#         line2 = re.sub(pattern2, '', line1)
#         new_sentence = ''.join(line2.split())  # 去除空白
#         return new_sentence
#
#     # 分词并去除停用词
#     def preprocess_text(text, stopwords):
#         clean_text = clear_character(text)
#         seg_text = jieba.lcut(clean_text)
#         final_text = [word for word in seg_text if word not in stopwords]
#         return ' '.join(final_text)  # 转换为字符串
#
#     # 加载停用词
#     stop_words_path = r"D:\PythonProjects\weibo_django\Dashboard\learning_model\cn_stopwords.txt"
#
#     def get_stop_words():
#         file = open(stop_words_path, 'rb').read().decode('utf-8').split('\r\n')
#         return set(file)
#
#     stopwords = get_stop_words()
#
#     # 对新文本进行预处理
#     preprocessed_text = preprocess_text(news_text, stopwords)
#
#     # 将预处理的文本转换为 TF-IDF 向量
#     text_vector = tfidf_model.transform([preprocessed_text])
#
#     # 预测新文本的类别
#     predicted_label_id = classifier.predict(text_vector)
#
#     # 将预测的标签 ID 转换回类别名称
#     predicted_label = le.inverse_transform(predicted_label_id)
#
#     return predicted_label[0]


import requests
import torch
from transformers import BertTokenizer
from torch import nn
from transformers import BertModel


# 定义标签字典
def get_label_string(label):
    labels = {
        '民生': 0, '文化': 1, '娱乐': 2, '体育': 3, '财经': 4, '家具': 5,
        '汽车': 6, '教育': 7, '科技': 8, '军事': 9, '旅游': 10, '时政': 11,
        '股票': 12, '农业': 13, '电竞': 14
    }
    for key, value in labels.items():
        if value == label:
            return key
    return None


# 定义BERT分类模型
class BertClassifier(nn.Module):
    def __init__(self, dropout=0.5):
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese',
                                              num_labels=15)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 15)
        self.relu = nn.ReLU()

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(input_ids=input_id, attention_mask=mask, return_dict=False)
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)
        return final_layer


# 加载已训练的模型和分词器
model = BertClassifier()
model.load_state_dict(torch.load(r'D:\PythonProjects\weibo_django\Dashboard\BERT-toutiao.pt'))
model.eval()
tokenizer = BertTokenizer.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese')
if torch.cuda.is_available():
    model.cuda()


# 定义 classify_news 函数
def classify_news(news_data):
    # 对新闻数据进行分词和编码
    text_input = tokenizer(news_data, padding='max_length', max_length=512, truncation=True, return_tensors="pt")
    if torch.cuda.is_available():
        text_input = {key: value.cuda() for key, value in text_input.items()}
    mask = text_input['attention_mask']
    input_id = text_input['input_ids']

    # 预测新闻分类

    with torch.no_grad():
        output = model(input_id, mask)
        label_index = output.argmax(dim=1).item()

    # 获取标签名称
    label_string = get_label_string(label_index)

    torch.cuda.empty_cache()  # 清理未使用的显存
    return label_string


# 获取微博内容并分类
def getContentData():
    news_data_analysis = []
    for i in (1, 3):
        url = 'https://weibo.com/ajax/statuses/mymblog'
        headers = {
            'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; ULV=1731851135570:6:1:1:4133330521076.9653.1731851135541:1730175311306; PC_TOKEN=3c4cfa8430; ALF=1734835068; SUB=_2A25KO54rDeRhGeNG7VsV8SbFwz2IHXVpOJ_jrDV8PUJbkNAGLRLgkW1NSzm19AAQfOYvAklpwz-zq6wZDjZg0GBo; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; XSRF-TOKEN=ixlYZJNGg_8AJDYGL0VaKIrf; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzdpXwP0B53Nvrd8o70HP3CtrmmgHVXxhcx0XOadspJxnzCfUF03Ov4drtasAozuZdw==',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        }
        params = {
            'uid': 2656274875,
            'page': i,
            'feature': 0
        }
        response = requests.get(url, headers=headers, params=params)

        # 获取微博数据并分类
        for j in range(1, 20):
            news_data = response.json()['data']['list'][j]['text_raw'].strip()
            label = classify_news(news_data)
            news_data_dict = {news_data: label}
            news_data_analysis.append(news_data_dict)

    # # 打印分类结果
    # for item in news_data_analysis:
    #     for key, value in item.items():
    #         print(f"新闻内容: {key}\t分类: {value}\n")

    return news_data_analysis


if __name__ == '__main__':
    getContentData()
