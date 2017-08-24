#!-*-coding:utf-8-*-
from django import template
from ..models import Post,Category,Tag
from django.db.models.aggregates import Count
#导入template模块，实例化template.Library类，并将函数get_recent_posts装饰成register.simple_tag
#这样就可以在模板中使用语法{% get_recent_posts %}调用这个函数

register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]
    
@register.simple_tag
def archives():
    #dates 方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间，且是 Python 的 date 对象，精确到月份，降序排列。
    #created_time ，即 Post 的创建时间，month 是精度，order='DESC' 表明降序排列
    #按月归档
    return Post.objects.dates('created_time','month',order='DESC')


@register.simple_tag
def get_categories():
    #记得在顶部导入count函数
    #Count计算分类下的文章数，其接收的参数为需要计算的模型名称
    #Category.objects.annotate 方法和 Category.objects.all 有点类似，它会返回数据库中全部 Category 
    #的记录，但同时它还会做一些额外的事情，在这里我们希望它做的额外事情就是去统计返回的 Category 记录的集合中每条记录下的文章数。代码中的 Count 
    #方法为我们做了这个事，它接收一个和 Categoty 相关联的模型参数名（这里是 Post，通过 ForeignKey 关联的），然后它便会统计 Category 
    #记录的集合中每条记录下的与之关联的 Post 记录的行数，也就是文章数，最后把这个值保存到 num_posts 属性中
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

@register.simple_tag
def get_tags():
    #记得在顶部引入Tag模型
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
