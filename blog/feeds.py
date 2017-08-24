#!-*-coding:utf-8-*-
from django.contrib.syndication.views import Feed
from .models import Post

class AllPostsRssFeed(Feed):
    #显示在聚合阅读器上的标题
    title = "Django博客演示项目"
    #通过聚合阅读器跳转到网站的地址
    link = "/"
    #显示在聚合阅读器上的描述信息
    description ="Django博客项目测试文章"
    #需要显示的内容条目
    def items(self):
        return Post.objects.all()
    #聚合阅读器中显示的内容条目标题
    def item_title(self,item):
        return '[%s] %s' % (item.category,item.title)
    #聚合显示器中显示内容条目的描述
    def item_description(self,item):
        return item.body
