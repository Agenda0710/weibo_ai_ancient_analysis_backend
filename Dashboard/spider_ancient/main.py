import os
from sqlalchemy import create_engine, text
import pandas as pd
from Dashboard.spider_ancient.spider_ancient_search_first import get_ancient_article_ids
from Dashboard.spider_ancient.spider_ancient_content_second import start as get_ancient_articles
from Dashboard.spider_ancient.spider_ancient_comments_third import start as get_ancient_comments

# 数据库连接引擎
engine = create_engine('mysql+pymysql://root:xusong986514@127.0.0.1/weibo?charset=utf8mb4')

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 定义CSV文件路径
content_csv_path = os.path.join(script_dir, 'ancient_weibo_content.csv')
comment_csv_path = os.path.join(script_dir, 'ancient_weibo_comment.csv')


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
            if table_exists('ancient_articles'):
                if not column_exists('ancient_articles', 'id'):
                    print("ancient_articles 表中缺少 id 列，请检查表结构！")
                else:
                    conn.execute(text('ALTER TABLE ancient_articles MODIFY COLUMN id BIGINT NOT NULL PRIMARY KEY;'))
                    print("修改表 ancient_articles 成功")
            else:
                print("表 ancient_articles 不存在，跳过修改")
        except Exception as e:
            print(f"修改 ancient_articles 表时出现错误：{e}")

        try:
            if table_exists('ancient_comments'):
                conn.execute(text('alter table ancient_comments drop column id;'))
                conn.execute(text(
                    'ALTER TABLE ancient_comments ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;'))
                print("ancient_comments 表中已添加 id 列并设置为主键")
            else:
                print("表 ancient_comments 不存在，跳过修改")
        except Exception as e:
            print(f"修改 ancient_comments 表时出现错误：{e}")


def save_to_sql():
    """保存数据到数据库"""
    try:
        # 读取数据库表
        if table_exists('ancient_articles'):
            articleOldPd = pd.read_sql('select * from weibo.ancient_articles', con=engine)
        else:
            articleOldPd = pd.DataFrame()

        if table_exists('ancient_comments'):
            commentOldPd = pd.read_sql('select * from weibo.ancient_comments', con=engine)
        else:
            commentOldPd = pd.DataFrame()

        # 读取本地 CSV 文件（使用动态路径）
        articleNewPd = pd.read_csv(content_csv_path)
        commentNewPd = pd.read_csv(comment_csv_path)

        # 合并数据并去重
        concatArticlePd = pd.concat([articleNewPd, articleOldPd], ignore_index=True)
        concatArticlePd.drop_duplicates(subset='id', keep='last', inplace=True)

        concatCommentPd = pd.concat([commentNewPd, commentOldPd], ignore_index=True)
        concatCommentPd.drop_duplicates(subset='content', keep='last', inplace=True)

        # 将处理后的数据写入数据库
        concatArticlePd.to_sql('ancient_articles', con=engine, if_exists='replace', index=False)
        concatCommentPd.to_sql('ancient_comments', con=engine, if_exists='replace', index=False)

        # 删除本地 CSV 文件（使用动态路径）
        os.remove(content_csv_path)
        os.remove(comment_csv_path)
        print("数据保存成功")
    except Exception as e:
        print(f"保存数据时出现错误：{e}")
        try:
            articleNewPd.to_sql('ancient_articles', con=engine, if_exists='replace', index=False)
            commentNewPd.to_sql('ancient_comments', con=engine, if_exists='replace', index=False)
            print("直接写入新数据成功")
        except Exception as ex:
            print(f"直接写入新数据时也出现错误：{ex}")


def main():
    print('爬取相关的文章id')
    ids = get_ancient_article_ids()
    print('爬取文章相关内容')
    get_ancient_articles(ids)
    print('爬取文章相关评论')
    get_ancient_comments()
    print('正在存储数据...')
    save_to_sql()
    print('正在修改表结构...')
    alter_tables()


if __name__ == '__main__':
    main()
