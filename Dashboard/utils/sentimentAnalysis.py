import jieba
from snownlp import SnowNLP
from collections import Counter
import re
from transformers import BertForSequenceClassification, BertTokenizer
import torch


# 加载停用词表
def load_stopwords():
    stopwords_path = 'Dashboard/learning_model/cn_stopwords.txt'
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        for line in f:
            stopwords = set(line.strip())
    return stopwords


# 获取前十个热词及其频率
def get_top_keywords(content_list, stopwords):
    all_words = []

    for content in content_list:
        # 使用jieba进行分词
        words = jieba.cut(content)
        # 过滤掉停用词和单个字的词
        filtered_words = [word for word in words if
                          word not in stopwords and len(word) > 1 and re.match(r'^[\u4e00-\u9fa5]+$', word)]
        all_words.extend(filtered_words)

    # 统计词频
    word_counts = Counter(all_words)
    top_keywords = word_counts.most_common(10)

    return top_keywords


# 情感分析
def analyze_sentiment(content_list):
    sentiment_data = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }

    for content in content_list:
        s = SnowNLP(content)
        sentiment = s.sentiments  # 获取情感评分

        # 情感分类：大于0.5为正面，小于0.5为负面，等于0.5为中性
        if sentiment > 0.5:
            sentiment_data['positive'] += 1
        elif sentiment == 0.5:
            sentiment_data['neutral'] += 1
        else:
            sentiment_data['negative'] += 1

    return sentiment_data


# 1. 加载模型和分词器
tokenizer = BertTokenizer.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese')
model = BertForSequenceClassification.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese',
                                                      num_labels=3)
if torch.cuda.is_available():
    model.cuda()

# 2. 加载状态字典
model.load_state_dict(torch.load(r'D:\PythonProjects\weibo_django\Dashboard\weibo_articles_content_analysis.pt'))

# 3. 设置模型为评估模式
model.eval()


def analyze_article_sentiment(texts, batch_size=16):
    sentiment_labels = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=128)
        if torch.cuda.is_available():
            inputs = {key: value.cuda() for key, value in inputs.items()}

        with torch.no_grad(), torch.cuda.amp.autocast():
            outputs = model(**inputs)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=1)

        for pred in predictions:
            if pred.item() == 2:
                sentiment_labels.append("正面")
            elif pred.item() == 0:
                sentiment_labels.append("中性")
            elif pred.item() == 1:
                sentiment_labels.append("负面")

        torch.cuda.empty_cache()  # 清理未使用的显存

    return sentiment_labels  # 返回情感标签的列表

