import json

from django.core.paginator import Paginator
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_exempt

from .models import *
from django.http import JsonResponse
from django.db.models import Count, Max
from collections import Counter, defaultdict
import jieba
from snownlp import SnowNLP
from Dashboard.utils.sentimentAnalysis import *
from Dashboard.spiders.spiderNews import *
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from Dashboard.spiders.main import main as CollectData
from Dashboard.learning_model.main import first_step as GetWordFrequency
from Dashboard.spiders.spiderHotSearch import get_hot_search_data as HotSearchData


# Create your views here.
def get_article_statistics(request):
    """
    首页数据
    :param request:
    :return:
    """
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
    stop_words = load_stopwords()

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
    """
    获取评论热词数据
    :param request:
    :return:
    """
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


def get_articles_with_comments(request):
    """
    文章数据展示
    :param request:
    :return:
    """
    # 获取分页参数
    page = request.GET.get('page', 1)  # 默认为第一页
    page_size = request.GET.get('page_size', 6)  # 默认为每页6条数据

    # 获取所有文章并计算评论量
    articles = Article.objects.annotate(comment_count=Count('comments'))

    # 使用Paginator进行分页
    paginator = Paginator(articles, page_size)
    paginated_articles = paginator.get_page(page)

    # 创建一个结果列表，包含文章信息和评论量
    results = []
    for article in paginated_articles:
        results.append({
            'articleId': article.id,
            'region': article.region,
            'reposts_count': article.reposts_count,
            'comment_count': article.comment_count,  # 评论量
            'like_count': article.likenum,
            'type': article.type,
            'content': article.content,
            'create_at': article.create_at,
            'detailUrl': article.detailurl,  # 文章详情页
        })

    words = [item['content'] for item in results]
    sentiments = analyze_article_sentiment(words)

    for index, sentiment in enumerate(sentiments):
        results[index]['judge'] = sentiment

    # 返回分页结果和总条数
    return JsonResponse({
        'data': results,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': paginated_articles.number
    })


def article_analysis(request):
    """
    文章内容分析
    :param request:
    :return:
    """
    # 查询所有文章的类型并去重
    article_types = Article.objects.values_list('type', flat=True).distinct()
    selected_type = request.GET.get('type', None)

    # 查询筛选后的文章
    if selected_type:
        articles = Article.objects.filter(type=selected_type)
    else:
        articles = Article.objects.all()

    # 定义统计区间
    like_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, 10000), (10000, float('inf'))]
    comment_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, float('inf'))]
    repost_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, float('inf'))]

    # 统计点赞量、评论量、转发量
    def get_interval_count(articles, field, intervals):
        interval_count = defaultdict(int)
        for article in articles:
            value = getattr(article, field)
            for start, end in intervals:
                if start <= value < end:
                    interval_count[f"{start}-{end}"] += 1
                    break
        return interval_count

    like_counts = get_interval_count(articles, 'likenum', like_intervals)
    comment_counts = get_interval_count(articles, 'commentnum', comment_intervals)
    repost_counts = get_interval_count(articles, 'reposts_count', repost_intervals)

    # 返回类型列表
    return JsonResponse({'types': list(article_types),
                         'like_counts': like_counts,
                         'comment_counts': comment_counts,
                         'repost_counts': repost_counts})


def region_analysis(request):
    """
    ip地址分析
    :param request:
    :return:
    """
    # 统计每个地区的文章数
    article_counts = (
        Article.objects.values('region')  # 以地区分组
        .annotate(article_count=Count('id'))  # 统计每个地区的文章数
        .order_by('region')  # 排序
    )

    # 统计每个地区的评论数
    comment_counts = (
        Comments.objects.values('region')  # 以地区分组
        .annotate(comment_count=Count('articleid'))  # 统计每个地区的评论数
        .order_by('region')  # 排序
    )

    # 将结果组合成一个列表，以便返回给前端
    article_data_list = [
        {'region': item['region'], 'article_count': item['article_count']}
        for item in article_counts
    ]

    comment_data_list = [
        {'region': item['region'], 'comment_count': item['comment_count']}
        for item in comment_counts
    ]

    # 返回给前端的 JSON 数据
    return JsonResponse({
        'articleDataList': article_data_list,
        'commentDataList': comment_data_list
    })


def comments_analysis(request):
    """
    评论分析
    :param request:
    :return:
    """
    # 定义点赞数区间为每 20 个一组
    interval = 20

    # 统计每个区间的评论数
    like_bins = Comments.objects.values('like_counts').annotate(count=Count('id'))

    # 整理数据到区间中
    bins = {}
    for item in like_bins:
        like_count = item['like_counts'] if item['like_counts'] is not None else 0
        bin_index = (like_count // interval) * interval
        if bin_index in bins:
            bins[bin_index] += item['count']
        else:
            bins[bin_index] = item['count']

    # 构建前端需要的数据格式
    response_data = []
    for bin_start, count in sorted(bins.items()):
        response_data.append({
            'like_range': f"{bin_start}-{bin_start + interval}",
            'comment_count': count
        })

    # 性别数据
    gender_counts = Comments.objects.values_list('authorgender', flat=True)
    gender_counter = Counter(gender_counts)

    # 获取词频数据
    word_frequencies = WordFrequency.objects.all().values('word', 'frequency')
    word_data = [{'name': wf['word'], 'value': wf['frequency']} for wf in word_frequencies[:40]]

    return JsonResponse({
        'data': response_data,
        'gender_data': [{'name': gender, 'value': count} for gender, count in gender_counter.items()],
        'word_data': word_data
    })


def sentiment_analysis(request):
    """
    文章内容+评论的情感分析
    :param request:
    :return:
    """
    # 获取所有文章内容和评论内容
    articles = [article for article in Article.objects.all().values_list('content', flat=True) if
                article and isinstance(article, str)]
    comments = [comment for comment in Comments.objects.all().values_list('content', flat=True) if
                comment and isinstance(comment, str)]

    stopwords = load_stopwords()

    # 1. 获取文章热词分析（前十个词以及它们的频率）
    top_keywords = get_top_keywords(articles, stopwords)

    # 2. 统计文章内容的情感
    article_sentiments = analyze_article_sentiment(list(articles))
    article_positive_count = sum([1 for sentiment in article_sentiments if sentiment == "正面"])
    article_neutral_count = sum([1 for sentiment in article_sentiments if sentiment == "中性"])
    article_negative_count = sum([1 for sentiment in article_sentiments if sentiment == "负面"])

    # 3. 统计评论内容的情感
    comment_sentiments = analyze_article_sentiment(list(comments))
    comment_positive_count = sum([1 for sentiment in comment_sentiments if sentiment == "正面"])
    comment_neutral_count = sum([1 for sentiment in comment_sentiments if sentiment == "中性"])
    comment_negative_count = sum([1 for sentiment in comment_sentiments if sentiment == "负面"])

    # 4.统计热词的情感
    all_words = []
    for content in articles:
        # 使用jieba进行分词
        words = jieba.cut(content)
        # 过滤掉停用词和单个字的词
        filtered_words = [word for word in words if
                          word not in stopwords and len(word) > 1 and re.match(r'^[\u4e00-\u9fa5]+$', word)]
        all_words.extend(filtered_words)

    keywords_sentiment = analyze_sentiment(all_words)

    # 返回结果
    return JsonResponse({
        'top_keywords': top_keywords,
        'article_sentiment': {
            'positive': article_positive_count,
            'neutral': article_neutral_count,
            'negative': article_negative_count
        },
        'comment_sentiment': {
            'positive': comment_positive_count,
            'neutral': comment_neutral_count,
            'negative': comment_negative_count
        },
        'keywords_sentiment': keywords_sentiment
    })


def article_content_word_cloud(request):
    """
    微博内容词云图的分析
    :param request:
    :return:
    """
    stopwords = load_stopwords()

    # 获取文章内容 (假设文章存在数据库中)
    articles = Article.objects.values_list('content', flat=True)
    full_text = ' '.join(articles)  # 将所有文章合并为一个字符串

    # 使用jieba进行分词
    words = jieba.lcut(full_text)

    # 只保留中文词语，并去掉停用词
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1 and word.isalpha() and all(
        '\u4e00' <= char <= '\u9fff' for char in word)]

    # 统计词频
    word_freq = Counter(filtered_words).most_common(100)  # 取前100个词语

    # 返回词语和词频数据
    return JsonResponse({'word_cloud': word_freq})


def get_hot_search_data(request):
    """
    热搜数据展示and热搜的情感分析
    :param request:
    :return:
    """
    hot_search_list = HotSearchData()

    # 批量分析情感
    words = [item['content'] for item in hot_search_list]
    sentiments = analyze_article_sentiment(words)

    # 将情感结果添加到列表中
    for i, sentiment in enumerate(sentiments):
        hot_search_list[i]['sentiment'] = sentiment

    # 统计情感数量
    sentiment_count = {
        '正面': sum(1 for item in hot_search_list if item['sentiment'] == '正面'),
        '中性': sum(1 for item in hot_search_list if item['sentiment'] == '中性'),
        '负面': sum(1 for item in hot_search_list if item['sentiment'] == '负面')
    }

    return JsonResponse({
        'total': len(hot_search_list),  # 数据总数
        'hot_search_data': hot_search_list,  # 所有热搜数据
        'sentiment_count': sentiment_count,  # 情感统计数量
    })


def get_current_news(request):
    """
    新闻页面的展示and新闻的分类
    :param request:
    :return:
    """
    news_data_analysis = getContentData()
    # 统计新闻分类
    category_counts = Counter(label for _, label in ((list(item.items())[0]) for item in news_data_analysis))
    return JsonResponse({
        'news_data_analysis': news_data_analysis,
        'category_counts': category_counts
    })


def get_data_views(request):
    """
    数据大屏的数据展示
    :param request:
    :return:
    """
    # 返回表格数据
    comments_content = [
        comment for comment in Comments.objects.all().values_list('content', flat=True).order_by('created_at').reverse()
        if comment and isinstance(comment, str)
    ]
    comments_region = list(
        Comments.objects.all().values_list('region', flat=True).order_by('created_at').reverse()
    )
    comments_sentiments_analysis = analyze_article_sentiment(comments_content)
    comment_list = [
        {
            'comments_content': comment,
            'sentiments_analysis': sentiment,
            'comments_region': region
        }
        for comment, sentiment, region in zip(comments_content, comments_sentiments_analysis, comments_region)
    ]

    # 返回饼图数据
    article_type_data = Article.objects.values('type').annotate(type_count=Count('id'))
    article_type_list = [{'value': entry['type_count'], 'type': entry['type']} for entry in article_type_data]

    # 排名图
    news_data_analysis = getContentData()
    news_category_counts = Counter(label for _, label in ((list(item.items())[0]) for item in news_data_analysis))

    # 统计新闻词云图
    news_contents = [
        key for key, _ in ((list(item.items())[0]) for item in news_data_analysis)
        if key and isinstance(key, str)
    ]
    stop_words = load_stopwords()
    words = []
    for news_content in news_contents:
        for word in jieba.cut(news_content):
            if word not in stop_words and re.match(r'^[\u4e00-\u9fa5]+$', word) and word not in ['了', '是', '在', '的',
                                                                                                 '一个', '有', '又',
                                                                                                 '也']:
                words.append(word)
    word_counts = Counter(words)
    top_fifteen = dict(word_counts.most_common(15))
    news_wordcloud_data = [{'name': word, 'value': count} for word, count in top_fifteen.items()]

    # 返回胶囊图数据，新闻情感
    news_sentiments_analysis = analyze_article_sentiment(news_contents)
    news_sentiments_statistic = Counter(news_sentiments_analysis)

    # 返回翻牌器数据，统计微博文章和评论的数量
    article_count = Article.objects.count()
    comment_count = Comments.objects.count()

    return JsonResponse({
        'comment_list': comment_list,
        'article_type_list': article_type_list,
        'news_category_counts': news_category_counts,
        'news_wordcloud_data': news_wordcloud_data,
        'news_sentiments_statistic': news_sentiments_statistic,
        'article_count': article_count,
        'comment_count': comment_count,
    })


# 加载保存的模型和分词器
model_path = r"D:\PythonProjects\weibo_django\Dashboard\fine_tuned_bert_fake_news"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()  # 设置为评估模式


@csrf_exempt  # 禁用 CSRF 验证
def predict_fake_or_real(request):
    """
    接收前端发送的新闻内容，返回预测结果（真假）。
    """
    if request.method == "POST":
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)
            text = data.get("text", "")
            if not text:
                return JsonResponse({"error": "请输入有效的文本！"}, status=400)

            # 模型预测
            inputs = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=128)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()

            # 映射预测结果
            label_map = {0: "假新闻", 1: "真新闻"}
            prediction = label_map[predicted_class]

            return JsonResponse({"prediction": prediction}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的 JSON 数据！"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "仅支持 POST 请求！"}, status=405)


@csrf_exempt
def auto_data_collection(request):
    """
    爬虫自动化
    :param request:
    :return:
    """
    if request.method == "POST":
        data = json.loads(request.body)
        # 获取爬取类型的数量
        type_num = data.get("type_num", '')
        # 获取爬取文章页面的页数
        page_num = data.get("page_num", '')

        # 进行数据采集
        CollectData(type_num, page_num)
        # 进行词频分析
        GetWordFrequency()

        return JsonResponse({"success": True}, status=200)

    return JsonResponse({"error": "仅支持 POST 请求！"}, status=405)


# 加载模型和 Tokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
fraud_detection_tokenizer = BertTokenizer.from_pretrained('Dashboard/bert-fraud-detection')
fraud_detection_model = BertForSequenceClassification.from_pretrained('Dashboard/bert-fraud-detection').to(device)
fraud_category_tokenizer = BertTokenizer.from_pretrained('Dashboard/bert-fraud-category')
fraud_category_model = BertForSequenceClassification.from_pretrained('Dashboard/bert-fraud-category').to(device)

# 设置模型为评估模式
fraud_detection_model.eval()
fraud_category_model.eval()

# 定义欺诈类别映射
fraud_categories = {
    0: "刷单返利类", 1: "虚假网络投资理财类", 2: "冒充电商物流客服类",
    3: "贷款、代办信用卡类", 4: "网络游戏产品虚假交易类", 5: "虚假购物、服务类",
    6: "冒充公检法及政府机关类", 7: "网黑案件", 8: "虚假征信类",
    9: "冒充领导、熟人类", 10: "冒充军警购物类诈骗", 11: "网络婚恋、交友类（非虚假网络投资理财类）"
}

@csrf_exempt
def predict_junk_information(request):
    """
    接收前端POST请求，进行欺诈信息检测和分类
    """
    if request.method == "POST":
        try:
            # 从请求中获取数据
            data = json.loads(request.body)
            text = data.get("text", "")

            if not text:
                return JsonResponse({"error": "文本不能为空"}, status=400)

            # Step 1: 使用 'bert-fraud-detection' 判断是否是欺诈信息
            detection_encoding = fraud_detection_tokenizer(
                text, padding=True, truncation=True, max_length=128, return_tensors="pt"
            ).to(device)

            with torch.no_grad():
                detection_outputs = fraud_detection_model(**detection_encoding)

            detection_logits = detection_outputs.logits
            is_fraud = torch.argmax(detection_logits, dim=1).item()

            # 如果是正常信息，返回结果
            if is_fraud == 0:
                return JsonResponse({"result": "正常信息"}, status=200)

            # Step 2: 如果是欺诈信息，分类预测
            category_encoding = fraud_category_tokenizer(
                text, padding=True, truncation=True, max_length=256, return_tensors="pt"
            ).to(device)

            with torch.no_grad():
                category_outputs = fraud_category_model(**category_encoding)

            category_logits = category_outputs.logits
            predicted_category = torch.argmax(category_logits, dim=1).item()
            fraud_category = fraud_categories.get(predicted_category, "未知类别")

            # 返回分类结果
            return JsonResponse({
                "result": "欺诈信息",
                "category": fraud_category,
                "reason": f"模型检测到该文本与“{fraud_category}”相关的关键词或特定模式。"
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "仅支持POST请求"}, status=405)
