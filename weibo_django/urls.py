"""
URL configuration for weibo_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from Dashboard import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    # 获取首页数据
    path('articleStatistics/', views.get_article_statistics, name='get_article_statistics'),
    # 获取评论热词数据
    path('hotWords/', views.get_hot_words_statistics, name='get_hot_words_statistics'),
    # 获取相关的微博文章展示
    path('articles/', views.get_articles_with_comments, name='articles_list'),
    # 获取相关的微博文章，包含点赞量区间统计，评论量统计，转发量统计
    path('articleAnalysis/', views.article_analysis, name='article_analysis'),
    # 获取相关的微博和评论的IP地址分析
    path('regionAnalysis/', views.region_analysis, name='region_analysis'),
    # 获取评论分析，点赞区间的评论数统计图，性别比例，词云图
    path('commentsAnalysis/', views.comments_analysis, name='comments_analysis'),
    # 舆情分析（异步任务接口）
    path('sentimentAnalysis/', views.sentiment_analysis, name='sentiment_analysis'),
    path('sentimentAnalysis/<str:task_id>/', views.check_sentiment_analysis_status, name='check_sentiment_status'),
    # 获取文章词云图
    path('articleContentWordCloud/', views.article_content_word_cloud, name='article_content_word_cloud'),
    # 获取当前热搜+ai模型解读热搜
    path('getHotSearchData/', views.get_hot_search_data, name='get_hot_search_data'),
    # 获取第大模型数据（央视新闻）+新闻类别分类
    path('getCurrentNews/', views.get_current_news, name='get_current_news'),
    # 新增大屏数据展示
    path('getDataViews/', views.get_data_views, name='get_data_views'),
    # 新增虚假文章内容分析（谣言分析）
    path('predictFakeOrReal/', views.predict_fake_or_real, name="predict_fake_or_real"),
    # 判断垃圾信息+垃圾信息分类
    path('predictJunkInformation/', views.predict_junk_information, name='predict_junk_information'),
    # 指定词分析+ai模型解读
    path('weiboSearchAnalysis/', views.weibo_search_analysis, name='weibo_search_analysis'),
    # 政策分析
    path('analyzeAiPolicies/', views.analyze_ancient_policies, name='analyze_ai_policies'),
    # 热点图谱
    path('techHotspotGraph/', views.get_tech_hotspot_graph, name='tech_hotspot_graph'),
]
