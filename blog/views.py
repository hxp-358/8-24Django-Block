#!-*-coding:utf-8-*-
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Post,Category,Tag
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q
#from django.core.paginator,EmptyPage,pageNotAnInteger

# Create your views here.
'''
def index(request):
    return HttpResponse("欢迎访问我的博客首页！！！")

def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request,'blog/index.html',context={
       # 'title':'我的博客首页',
       # 'welcome':'欢迎访问我的博客首页',
       'post_list':post_list
        })
'''
class IndexView(ListView):
    #IndexView 的功能是从数据库中获取文章（Post）列表，ListView 就是从数据库中
    #获取某个模型列表数据的，所以 IndexView 继承 ListView
    model = Post
    template_name = 'blog/index.html'
    context_object_name ='post_list'
    paginate_by =3
    def get_context_data(self,**kwargs):
        #在视图函数中将模板变量传递给render函数的context参数传递一个字典实现的
        #例如render(request,'blog/index.html',context={'post_list':post_list})
        #这里传递了一个{'post_list':post_list}字典给模板
        #在类视图中这个需要传递的模板变量字典是通过get_context_data获得的，
        #所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去
        #首先生成父类生成的传递给模板的字典
        context =super().get_context_data(**kwargs)
        #父类生成的字典中已有paginator,page_obj,paginated 这三个模板变量
        #paginator 是Paginator的一个实例
        #page_obj是Page的一个实例
        #is_paginated 是一个布尔变量，用于指示是否已分页
        #例如如果规定每页10个数据，而本身只有5个数据，其实就用不着分页，此时
        #is_paginated=False,关于什么是Paginator,Page,类在Django Pagination 简单分页：
        #http://zmrenwu.com/post/34/ 中已有详细说明。
        #由于context是一个字典，所以调用get方法从中取出某个键对应的值
        paginator =context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        #调用自己写的pagination_data方法获得显示分页导航条需要的数据，见下方
        pagination_data = self.pagination_data(paginator,page,is_paginated)
        #将分页导航条的模板变量更新到context中，注意pagination_data方法返回的也是一个字典
        context.update(pagination_data)
        #将更新后的context返回，以便ListView使用这个字典中的模板变量去渲染模板
        #注意此时的context字典中已经有显示分页导航条所需要的数据
        return context
    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            #如果梅雨分页，则无需显示分页导航条，不用显示任何分页导航条数据，因此返回一个空字典
            return {}
        #当前页左边的页码号，初始值为空
        left = []
        #当前页右边的页码号，初始值为空
        right =[]
        #标识第一页页码后是否需要显示省略号
        left_has_more =False
        #标识最后一页页码前是否需要显示省略号
        right_has_more=False
        #标示是否需要显示第一页的页码号
        #因为如果当前页左边的连续页码号中已经包含第一页的页码号，此时就无需显示第一页的页码号
        #其他情况第一页的页码号始终要显示
        first =False
        #标示是否要显示最后一页的页码号
        #需要指示变量的理由和上面相同
        last = False
        #获取用户当前请求的页码号
        page_number =page.number
        #获取分页后的总页数
        total_pages =paginator.num_pages
        #获取整个分页列表，比如分了四页，那末就是[1,2,3,4]
        page_range = paginator.page_range
        if page_number ==1:
            #如果用户请求的是第一页数据，那末当前页左边不需要数据，因此left=[](已默认)
            #此时只要获取当前页右边的连续页码号
            #比如分页列表是[1,2,3,4],那么获取的就是right=[2,3]
            #注意这里只获取了当前页后两个页码，你可以更改这个数字获取更多页码
            right =page_range[page_number:page_number+2]
            #如果右边的页码号比最后一页的页码号减1还要小
            #说明右边页码号和最后一页的页码号之间还有其他页码，因此需要显示省略号，通过
            if right[-1]< total_pages - 1:
                right_has_more =True
            #如果最右边的页码号比最后一页的页码号小，说明当前页的连续号码中不包含最后一页
            #所以需要显示最后一页的页码号，通过last来指示
            if right[-1]< total_pages:
                last =True
        elif page_number == total_pages:
            #如果用户请求的是最后一页的数据，那末当前页右边不需要数据因此right =[](已默认)
            #此时只需要获取当前页左边的连续页码号
            #比如分页列表号是[1,2,3,4],那么获取的就是left =[2,3]
            #这里只获取当前页码前两个页码，你可以更改这个数字获取更多页码
            left = page_range[(page_number - 3) if (page_number - 3) >0 else 0:page_number-1]
            #如果左边的页码比第二页页码还大
            #说明左边的页码和第一页的页码之间还有其他页码，因此需要显示省略号
            if left[0]>2:
                left_has_more = True
            #如果左边的页码号比第一页的页码号大，说明当前页左边连续页码号中不包含第一页的页码
            #所以需要显示第一页的页码号，通过firstt来指示
            if left[0]>1:
                first =True
        else:
            #用户请求的既不是最后一页也不是第一页，则需要获取当前页左右两边的连续页码号
            #这里只获取了当前页前后连续两个页码，你可以更改数字以获取更多页码
            left = page_range[(page_number - 3) if (page_number -3)>0 else 0:page_number-1]  
            right =page_range[page_number:page_number + 2]
            #是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last =True
            #是否需要显示第一页和第一页后的省略号
            if left[0] >2:
                left_has_more =True
            if left[0] >1:
                first = True
        
        data ={
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }
        return data
            
class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags=tag)
'''
def detail(request,pk):
    #从django.shortcuts 中导入get_object_or_404
    #其作用就是当传入的 pk 对应的 Post 在数据库存在时，
    #就返回对应的 post，如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。
    post = get_object_or_404(Post,pk=pk)
    #阅读量+1
    post.increase_views()
    #支持markdown语法，代码高亮显示
    #安装并引入markdown,Pygments模块Pygments 的工作原理是把代码切分成一个个单词，然后为这些单词添加 
    #css样式，不同的词应用不同的样式，这样就实现了代码颜色的区分，即高亮了语法。
    #最后引入引入一个样式文件来给这些被添加了样式的单词定义颜色
    post.body = markdown.markdown(post.body,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ])
    #记得导入CommentForm
    form =CommentForm()
    #获取评论列表
    comment_list = post.comment_set.all()
    #将文章、表单、评论列表作为模板变量传给详情页，以便渲染
    return render(request,'blog/detail.html',context={'post':post,'form':form,'comment_list':comment_list})
'''
class PostDetailView(DetailView):
    #这些类属性和ListView一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    def get(self,request,*args,**kwargs):
        #复写get方法是以为每当文章被访问一次，就将文章的访问量+1
        #get方法返回的是一个HttpResponse实例
        #之所以需要先调用父类的get方法，是因为只有当get方法被调用后，
        #才有 self.object属性，其值为Post模型实例，即被访问的文章post
        response = super(PostDetailView,self).get(request,*args,**kwargs)
        #文章阅读量+1
        #注意self.object的值就是被访问的文章post
        self.object.increase_views()
        #视图必须返回一个response对象
        return response
    def get_object(self,queryset=None):
        #复写get_object方法的目的是因为需要对post的body值进行渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        #get_object 方法中我们没有直接用 markdown.markdown() 方法来渲染 post.body 中的内容，而是先实例化了一个 markdown.Markdown 类 md，和 
        #markdown.markdown() 方法一样，也传入了 extensions 参数。接着我们便使用该实例的 convert 方法将 post.body 中的 Markdown 文本渲染成 HTML 
        #文本。而一旦调用该方法后，实例 md 就会多出一个 toc 属性，这个属性的值就是内容的目录，我们把 md.toc 的值赋给 post.toc 属性（要注意这个 post 
        #实例本身是没有 md 属性的，我们给它动态添加了 md 属性，这就是 Python 动态语言的好处，不然这里还真不知道该怎么把 toc 的值传给模板）。
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
#            'markdown.extensions.toc',
            TocExtension(slugify=slugify),
            ])
        #和之前不同的是，extensions 中的 toc 拓展不再是字符串 markdown.extensions.toc ，而是 TocExtension 的实例。TocExtension 在实例化时其 slugify 
        #参数可以接受一个函数作为参数，这个函数将被用于处理标题的锚点值。Markdown 内置的处理方法不能处理中文标题，所以我们使用了 django.utils.text 
        #中的 slugify 方法，该方法可以很好地处理中文
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post
    def get_context_data(self,**kwargs):
        #复写get_context_data的目的是因为除了将post传给模板外（DetailView已经榜我们完成）,
        #还要把评论表单、post、下的评论列表传递给模板
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form =CommentForm
        comment_list =self.object.comment_set.all()
        context.update({ 'form':form,
                                 'comment_list':comment_list
                                 })
        return context
'''
def archives(request,year,month):
    #使用了模型管理器（objects）的 filter 函数来过滤文章。由于是按照日期归档，因此这里根据文章发表的年和月来过滤
    #根据 created_time 的 year 和 month 属性过滤，筛选出文章发表在对应的 year 年和 month 月的文章
    # created_time 是 Python 的 date 对象，其有一个 year 和 month 属性，我们在 页面侧边栏：使用自定义模板标签
    #使用过这个属性。Python中类实例调用属性的方法通常是 created_time.year，
    #但是由于这里作为函数的参数列表，所以 Django 要求我们把点替换成了两个下划线，即 created_time__year。
    #同时和 index 视图中一样，我们对返回的文章列表进行了排序
    post_list =Post.objects.filter(created_time__year=year,created_time__month=month).order_by('-created_time')
    return render(request,'blog/index.html',context={'post_list':post_list})
'''
class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super (ArchivesView,self).get_queryset().filter(created_time__year=year,created_time__month=month)
'''
def category(request,pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request,'blog/index.html',context={'post_list':post_list}) 
'''
class CategoryView(ListView):
    model =Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    #我们覆写了父类的 get_queryset 方法。该方法默认获取指定模型的全部列表数据。
    #为了获取指定分类下的文章列表数据，我们覆写该方法，改变它的默认行为。
    def get_queryset(self):
        #在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，非命名组参数值保存在实例的 args 
        #属性（是一个列表）里。所以我们使了 self.kwargs.get('pk') 来获取从 URL 捕获的分类 id 值。然后我们调用父类的 get_queryset 
        #方法获得全部文章列表，紧接着就对返回的结果调用了 filter 方法来筛选该分类下的全部文章并返回。
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category=cate)
#在开头django.db.models import Q
def search(request):
    q=request.GET.get('q')
    error_msg = ''
    if not q:
        error_msg = "请输入关键词"
        return render(request,'blog/index.html',{'error_msg':error_msg})
        
    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render (request,'blog/index.html',{'error_msg':error_msg,'post_list':post_list})
    
