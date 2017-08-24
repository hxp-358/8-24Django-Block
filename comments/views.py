#!-*-coding:utf-8-*-
from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post
from .models import Comment
from .forms import CommentForm

# Create your views here.

def post_comment(request,post_pk):
    #先获取评论的文章，后面要把文章和评论关联起来
    #这里我们使用了django提供的一个快捷函数get_object_or_404
    #这个函数的作用是获取文章(Post)存在时，则获取，不存在时返回404页面给用户
    post = get_object_or_404(Post,pk=post_pk)
    #http请求有两种，一般用户通过表单提交数据都是通过post请求
    #因此当用户请求是post时才处理表单数据
    if request.method == 'POST':
        #用户提交的数据在request.POST中，这是一个类字典
        #我们利用这些数据构造了CommentForm的实例，这样Django的表单就生成了
        form = CommentForm(request.POST)
        #调用form.is_valid()，检测表单数据是否符合格式要求
        if form.is_valid():
            #数据是合法的，调用表单的save()方法保存数据到数据库
            #commit = False的作用是仅利用表单数据生成Comment模型类的实例，但不保存评论数据到数据库
            comment = form.save(commit=False)
            #将评论和评论的文章关联起来
            comment.post =post
            #将评论数据保存到数据库，调用模型实例的save方法
            comment.save()
            #重定向到post的详情页，实际上当redirect函数接收一个模型的实例，它会调用这个模型实例的
            #get_absolute_url()方法，然后重定向到get_absolute_url()方法返回的URL
            return redirect(post)
        else:
            #检查数据不合法，重新渲染详情页和表单错误
            #我们传了3个模板变量给detail.html
            #一个是文章(Post),一个是评论列表，一个是表单form
            #我们这里调用了post.comment_set.all()方法
            #这个方法有点类似Post.object.all()
            #其作用是获取这篇文章下的所有评论
            #因为Post和Comment是ForeignKey关联的
            #因此使用post.comment_set.all()反向查询全部评论
            comment_list = post.comment_set.all()
            context= {'post':post,
                                 'form':form,
                                 'comment_list':comment_list,
                                 }
            return render(request,'blog/detail.html',context=context)
            #不是post请求，说明没有提交数据，重定向到文章详情页
    return redirect(post)
