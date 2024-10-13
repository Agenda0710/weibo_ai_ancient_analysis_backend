from spiderComment import start as spiderCommentStart
from spiderContent import start as spiderContentStart
import os
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:xusong986514@127.0.0.1/weibo?charset=utf8mb4')


def save_to_sql():
    try:
        # 从数据库中读取名为 weibo.article 的表数据到 articleOldPd
        articleOldPd = pd.read_sql('select * from weibo.article', con=engine)
        # 从本地 CSV 文件 contentData.csv 读取数据到 articleNewPd
        articleNewPd = pd.read_csv('contentData.csv')
        # 从数据库中读取名为 weibo.comments 的表数据到 commentOldPd
        commentOldPd = pd.read_sql('select * from weibo.comments', con=engine)
        # 从本地 CSV 文件 commentData.csv 读取数据到 commentNewPd
        commentNewPd = pd.read_csv('commentData.csv')

        # 将 articleNewPd 和 articleOldPd 进行纵向合并，取交集
        concatArticlePd = pd.concat([articleNewPd, articleOldPd], join='inner')
        # 将 commentNewPd 和 commentOldPd 进行纵向合并，取交集
        concatCommentPd = pd.concat([commentNewPd, commentOldPd], join='inner')

        # 基于 'id' 列去除 concatArticlePd 中的重复行，保留最后出现的重复行
        concatArticlePd.drop_duplicates(subset='id', keep='last', inplace=True)
        # 基于 'content' 列去除 concatCommentPd 中的重复行，保留最后出现的重复行
        concatCommentPd.drop_duplicates(subset='content', keep='last', inplace=True)

        # 将处理后的 concatArticlePd 数据写入数据库表 article，如果表已存在则替换
        concatArticlePd.to_sql('article', con=engine, if_exists='replace', index=False)
        # 将处理后的 concatCommentPd 数据写入数据库表 comments，如果表已存在则替换
        concatCommentPd.to_sql('comments', con=engine, if_exists='replace', index=False)
    except ConnectionError as e:
        print(f"连接错误: {e}")
        # 重试保存数据
        save_to_sql()
    except Exception as e:
        print(f"出现错误: {e}")
        # 如果出现其他错误，将 CSV 数据直接写入数据库表
        articleNewPd = pd.read_csv('contentData.csv')
        commentNewPd = pd.read_csv('commentData.csv')
        # 将 articleNewPd 数据写入数据库表 article，如果表已存在则替换
        articleNewPd.to_sql('article', con=engine, if_exists='replace', index=False)
        # 将 commentNewPd 数据写入数据库表 comments，如果表已存在则替换
        commentNewPd.to_sql('comments', con=engine, if_exists='replace', index=False)



def main():
    print('正在爬取文章数据')
    spiderContentStart(typeNum=3,pageNum=2)
    print('正在爬取评论数据')
    spiderCommentStart()
    print('正在存储数据')
    save_to_sql()


if __name__ == '__main__':
    main()
