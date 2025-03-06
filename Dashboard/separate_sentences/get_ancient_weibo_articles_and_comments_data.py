from Dashboard.utils.query import query


def get_all_ancient_comments_data():
    comment_list = query('select * from weibo.ancient_comments', [])
    return comment_list


def get_all_ancient_articles_data():
    article_list = query('select * from weibo.ancient_articles', [])
    return article_list
