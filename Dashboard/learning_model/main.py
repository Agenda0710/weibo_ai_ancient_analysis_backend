from sqlalchemy import create_engine
import pandas as pd
from Dashboard.learning_model.cipingTotal import main as get_word_frequency
from Dashboard.learning_model.yuqing import main as get_yuqing

engine = create_engine('mysql+pymysql://root:xusong986514@127.0.0.1/weibo?charset=utf8mb4')

# 生成ciping.csv文件
get_word_frequency()
get_yuqing()
print('文件生成完成')
# 读取 csv 文件
cipingTotalFile = pd.read_csv('cipingTotal.csv', header=0, names=['word', 'frequency'])
yuqingFile = pd.read_csv('target.csv', header=0, names=['comment', 'judge'])

# 如果数据库中不存在表，表已存在则替换
try:
    # 如果表已存在，先读取数据库中的表
    word_frequency_old = pd.read_sql_table('word_frequency', con=engine)
    public_sentiment_old = pd.read_sql_table('public_sentiment', con=engine)
    # 基于 'word', 'comment' 列去除重复行，保留最后出现的重复行
    word_frequency_new = pd.concat([word_frequency_old, cipingTotalFile]).drop_duplicates(subset='word', keep='last')
    public_sentiment_new = pd.concat([public_sentiment_old, yuqingFile]).drop_duplicates(subset='comment', keep='last')
    # 将处理后的数据写回数据库
    word_frequency_new.to_sql('word_frequency', con=engine, if_exists='replace', index=False)
    public_sentiment_new.to_sql('public_sentiment', con=engine, if_exists='replace', index=False)
except ValueError:
    frequencyNewPd = pd.read_csv('cipingTotal.csv')
    sentimentNewPd = pd.read_csv('target.csv')
    frequencyNewPd.to_sql('word_frequency', con=engine, if_exists='replace', index=False)
    sentimentNewPd.to_sql('public_sentiment', con=engine, if_exists='replace', index=False)
