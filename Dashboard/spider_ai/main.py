import os
from sqlalchemy import create_engine, text
import pandas as pd
from Dashboard.spider_ai.spider_ai_search_first import get_ai_article_ids
from Dashboard.spider_ai.spider_ai_content_second import start as get_ai_articles
from Dashboard.spider_ai.spider_ai_comments_third import start as get_ai_comments

# 数据库连接引擎
engine = create_engine('mysql+pymysql://root:xusong986514@127.0.0.1/weibo?charset=utf8mb4')


def table_exists(table_name):
    """检查表是否存在"""
    query = text(f"SHOW TABLES LIKE '{table_name}';")
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return len(result) > 0


def column_exists(table_name, column_name):
    """检查表中列是否存在"""
    query = text(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}';")
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return len(result) > 0


def alter_tables():
    """修改数据库表结构"""
    with engine.connect() as conn:
        try:
            # 如果 ai_articles 表存在，则设置 article_id 为主键
            if table_exists('ai_articles'):
                if not column_exists('ai_articles', 'id'):
                    print("ai_articles 表中缺少 id 列，请检查表结构！")
                else:
                    conn.execute(text('ALTER TABLE ai_articles MODIFY COLUMN id BIGINT NOT NULL PRIMARY KEY;'))
                    print("修改表 ai_articles 成功")
            else:
                print("表 ai_articles 不存在，跳过修改")
        except Exception as e:
            print(f"修改 ai_articles 表时出现错误：{e}")

        try:
            # 如果 ai_comments 表存在，则增加 id 列为自增主键（如果不存在）
            if table_exists('ai_comments'):
                if not column_exists('ai_comments', 'id'):
                    conn.execute(
                        text('ALTER TABLE ai_comments ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;'))
                    print("修改表 ai_comments 成功")
                else:
                    print("ai_comments 表中已存在 id 列，无需修改")
            else:
                print("表 ai_comments 不存在，跳过修改")
        except Exception as e:
            print(f"修改 ai_comments 表时出现错误：{e}")


def save_to_sql():
    """保存数据到数据库"""
    try:
        # 读取数据库表 ai_articles 和 ai_comments，如果不存在直接跳过
        if table_exists('ai_articles'):
            articleOldPd = pd.read_sql('select * from weibo.ai_articles', con=engine)
        else:
            articleOldPd = pd.DataFrame()  # 表不存在时使用空 DataFrame

        if table_exists('ai_comments'):
            commentOldPd = pd.read_sql('select * from weibo.ai_comments', con=engine)
        else:
            commentOldPd = pd.DataFrame()  # 表不存在时使用空 DataFrame

        # 读取本地 CSV 文件
        articleNewPd = pd.read_csv(r'D:\PythonProjects\weibo_django\Dashboard\spider_ai\ai_weibo_content.csv')
        commentNewPd = pd.read_csv(r'D:\PythonProjects\weibo_django\Dashboard\spider_ai\ai_weibo_comment.csv')

        # 合并数据并去重
        concatArticlePd = pd.concat([articleNewPd, articleOldPd], ignore_index=True)
        concatArticlePd.drop_duplicates(subset='id', keep='last', inplace=True)  # 去重基于 article_id

        concatCommentPd = pd.concat([commentNewPd, commentOldPd], ignore_index=True)
        concatCommentPd.drop_duplicates(subset='content', keep='last', inplace=True)  # 去重基于 content

        # 将处理后的数据写入数据库
        concatArticlePd.to_sql('ai_articles', con=engine, if_exists='replace', index=False)
        concatCommentPd.to_sql('ai_comments', con=engine, if_exists='replace', index=False)

        # 删除本地 CSV 文件
        os.remove(r'D:\PythonProjects\weibo_django\Dashboard\spider_ai\ai_weibo_content.csv')
        os.remove(r'D:\PythonProjects\weibo_django\Dashboard\spider_ai\ai_weibo_comment.csv')
        print("数据保存成功")
    except Exception as e:
        print(f"保存数据时出现错误：{e}")
        # 出现错误时尝试直接写入新数据
        try:
            articleNewPd.to_sql('ai_articles', con=engine, if_exists='replace', index=False)
            commentNewPd.to_sql('ai_comments', con=engine, if_exists='replace', index=False)
            print("直接写入新数据成功")
        except Exception as ex:
            print(f"直接写入新数据时也出现错误：{ex}")


def main():
    print('爬取相关的文章id')
    ids = get_ai_article_ids()
    print('爬取文章相关内容')
    get_ai_articles(ids)
    print('爬取文章相关评论')
    get_ai_comments()
    print('正在存储数据...')
    save_to_sql()
    print('正在修改表结构...')
    alter_tables()


if __name__ == '__main__':
    main()
