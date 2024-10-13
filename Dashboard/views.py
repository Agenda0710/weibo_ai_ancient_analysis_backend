from django.core.paginator import Paginator
from django.db.models.functions import Cast
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.db.models import Count, Max
from collections import Counter
import jieba
from snownlp import SnowNLP


# Create your views here.
def get_article_statistics(request):
    # 获取文章总数
    total_articles = Article.objects.count()

    # 获取点赞量最高的文章的作者
    top_liked_article = Article.objects.order_by('-likenum').first()
    top_liked_author = top_liked_article.authorname if top_liked_article else None

    # 获取发表文章最多的城市，跳过 region 为 null 的值
    top_cities = Article.objects.exclude(region__isnull=True).values('region').annotate(
        article_count=Count('id')).order_by('-article_count')[:2]

    # 将 create_at 转换为日期，假设你的日期格式为 'YYYY-MM-DD'
    article_counts = Article.objects.annotate(
        date=Cast('create_at', output_field=models.DateField())  # Cast 只能用于格式化正确的日期
    ).values('date').annotate(count=Count('id')).order_by('date')

    # 获取不同文章类型的占比
    article_type_data = Article.objects.values('type').annotate(type_count=Count('id'))

    # 获取评论区的用户名
    usernames = Comments.objects.values_list('authorname', flat=True)

    # 定义要删除的高频词列表
    stop_words = ['我', '你', '他', '的', '是', '啊']

    # 对用户名进行分词并统计词频
    words = []
    for username in usernames:
        for word in jieba.cut(username):
            if word not in stop_words:
                words.append(word)

    # 对词语进行统计
    word_counts = Counter(words)

    # 只取前十五条数据
    top_fifteen = dict(word_counts.most_common(15))

    # 准备词云图数据，转换成字典数据
    wordcloud_data = [{'name': word, 'value': count} for word, count in top_fifteen.items()]

    # 准备数据
    dates = [item['date'].strftime('%Y-%m-%d') for item in article_counts]
    counts = [item['count'] for item in article_counts]
    article_type_list = [{'value': entry['type_count'], 'name': entry['type']} for entry in article_type_data]

    if top_cities:
        top_city_name = top_cities[0]['region']
    else:
        top_city_name = None

    # 如果第一名是 null，取第二名
    if top_city_name is None and len(top_cities) > 1:
        top_city_name = top_cities[1]['region']

    # 获取点赞量最多的前四条评论
    top_comments_list = Comments.objects.order_by('-like_counts')[:4].values('authorname', 'content', 'like_counts')

    # 将 QuerySet 转换为列表
    top_comments_list = list(top_comments_list)

    data = {
        'total_articles': total_articles,
        'top_liked_author': top_liked_author,
        'top_city': top_city_name,
        'top_comments_list': top_comments_list,
        'dates': dates,
        'counts': counts,
        'article_type_data': article_type_list,
        'wordcloud_data': wordcloud_data,
    }

    return JsonResponse(data)


def get_hot_words_statistics(request):
    # 获取所有词频数据
    word_frequency_data = WordFrequency.objects.all()

    # 处理词频数据并进行情感分析
    hot_words_list = []
    for word_frequency in word_frequency_data:
        word = word_frequency.word
        frequency = word_frequency.frequency
        sentiment_score = SnowNLP(word).sentiments

        # 确定情感类型
        if sentiment_score > 0.5:
            sentiment = "正面"
        elif sentiment_score < 0.5:
            sentiment = "负面"
        else:
            sentiment = "中性"

        hot_words_list.append({
            'word': word,
            'frequency': frequency,
            'sentiment': sentiment,
        })

        # 处理分页查询
        selected_word = request.GET.get('selectedWord', '')
        page = request.GET.get('page', 1)  # 获取当前页码，默认第1页
        page_size = request.GET.get('pageSize', 10)  # 每页显示多少数据，默认10条

        # 查询评论内容中包含 selectedWord 的评论
        comments_query = Comments.objects.filter(content__icontains=selected_word)
        # 分页处理
        paginator = Paginator(comments_query, page_size)
        comments_page = paginator.get_page(page)

        # 将查询结果转换为字典列表，方便返回前端
        comments_list = [{
            'articleId': comment.articleid_id,
            'authorName': comment.authorname,
            'authorGender': comment.authorgender,
            'authorAddress': comment.authoraddress,
            'content': comment.content,
            'like_counts': comment.like_counts,
        } for comment in comments_page]

    # 返回 JSON 响应
    return JsonResponse({'hot_words_data': hot_words_list,
                         'total': paginator.count,
                         'currentPage': comments_page.number,
                         'pageSize': paginator.per_page,
                         'allComments': comments_list
                         })
