from sqlalchemy import create_engine, text
import pandas as pd
from Dashboard.separate_sentences.word_frequency_total import main as get_word_frequency
from Dashboard.separate_sentences.cut_comments import write_ai_articles_cuts

engine = create_engine('mysql+pymysql://root:xusong986514@127.0.0.1/weibo?charset=utf8mb4')


def second_step():
    """生成分词结果和词频文件"""
    write_ai_articles_cuts()
    get_word_frequency()
    print('文件生成完成')
    return pd.read_csv('./word_frequency_total.csv')


def update_database(word_frequency_file):
    """更新数据库中的词频表"""
    try:
        # 读取已有的词频表
        word_frequency_old = pd.read_sql_table('word_frequency', con=engine)

        # 合并新旧数据，去重后写回
        word_frequency_new = pd.concat([word_frequency_old, word_frequency_file]).drop_duplicates(subset='word',
                                                                                                  keep='last')
        word_frequency_new.to_sql('word_frequency', con=engine, if_exists='replace', index=False)
    except ValueError:
        # 如果表不存在，直接写入
        word_frequency_file.to_sql('word_frequency', con=engine, if_exists='replace', index=False)


def ensure_table_primary_key():
    """确保数据库表有主键"""
    with engine.connect() as conn:
        result = conn.execute(text("SHOW COLUMNS FROM word_frequency LIKE 'id';")).fetchall()
        if not result:
            conn.execute(
                text('ALTER TABLE word_frequency ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;')
            )


def first_step():
    """执行完整的流程"""
    word_frequency_file = second_step()
    update_database(word_frequency_file)
    ensure_table_primary_key()


if __name__ == '__main__':
    first_step()
