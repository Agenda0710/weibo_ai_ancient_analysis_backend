from Dashboard.utils.query import query


def get_all_ai_comments_data():
    comment_list = query('select * from weibo.ai_comments', [])
    return comment_list


def get_all_ai_articles_data():
    article_list = query('select * from weibo.ai_articles', [])
    return article_list
