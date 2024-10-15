import jieba
from snownlp import SnowNLP
from collections import Counter
import re


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
