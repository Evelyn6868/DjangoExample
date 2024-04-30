from django.shortcuts import render, redirect
from app01 import models
from app01.form.form import UserModelForm, PrettyModelForm, PrettyEditModelForm
from app01.utils.pagination import Pagination

import reportlab

# Create your views here.

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# 输入http://localhost:8000/generate-pdf/ 则自动下载hello.pdf pdf内有Hello World.
def some_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


# 部门管理
def depart_list(request):
    queryset = models.Department.objects.all()

    page_object = Pagination(request, queryset, page_size=2)

    page_object.html()

    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.page_string,
    }

    return render(request, 'depart_list.html', context)


def depart_add(request):
    if request.method == "GET":
        return render(request, 'depart_add.html')

    title = request.POST.get('title')

    models.Department.objects.create(title=title)

    return redirect("/depart/list")


def depart_delete(request):
    nid = request.GET.get('nid')
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/list")


def depart_edit(request, nid):
    if request.method == "GET":
        row_object = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {'row_object': row_object})
    title = request.POST.get('title')
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list")


# 用户管理
def user_list(request):
    queryset = models.UserInfo.objects.all()

    page_object = Pagination(request, queryset, page_size=2)

    """
    for obj in queryset:
        print(obj.id, obj.name, obj.password, obj.age, obj.account, obj.get_gender_display(), obj.depart.title,
              obj.create_time.strftime("%Y-%m-%d"))
    """
    page_object.html()
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.page_string
    }

    return render(request, 'user_list.html', context)


def user_add(request):
    return render(request, 'user_add.html')


def user_model_form_add(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'user_model_form_add.html', {'form': form})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        # 直接保存至数据库
        form.save()
        return redirect("/user/list/")

    # 校验失败(在页面上显示错误信息)
    return render(request, "user_model_form_add.html", {"form": form})


def user_edit(request, nid):
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        form = UserModelForm(instance=row_object)
        return render(request, 'user_edit.html', {'form': form})

    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/user/list/")

    return render(request, "user_edit.html", {"form": form})


def user_delete(request, nid):
    """用户删除"""
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list/")


# 靓号管理
def pretty_list(request):
    """靓号列表"""

    data_dict = {}
    # 如果是空字典,表示获取所有
    # 不加后面的 "", 首次访问浏览器,搜索框中不会显示前端页面中的 placeholder="Search for..." 属性
    search_data = request.GET.get('query', "")
    if search_data:
        data_dict["mobile__contains"] = search_data

    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level")

    # 引入封装的 Pagination 类并初始化
    # 初始化
    page_object = Pagination(request, queryset, page_size=10, page_param="page")
    page_queryset = page_object.page_queryset

    # 调用对象的html方法,生成页码
    page_object.html()

    page_string = page_object.page_string
    head_page = page_object.head_page
    end_page = page_object.end_page

    context = {
        "pretty_data": page_queryset,  # 分页的数据
        "search_data": search_data,  # 搜索的内容
        "page_string": page_string,  # 页码
        "head_page": head_page,  # 首页
        "end_page": end_page,  # 尾页
    }

    return render(request, "pretty_list.html", context)


def pretty_add(request):
    """添加靓号"""

    if request.method == "GET":
        form = PrettyModelForm()
        return render(request, "pretty_add.html", {"form": form})

    # 用户POST请求提交数据,需要进行数据校验
    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        # 直接保存至数据库
        form.save()
        return redirect("/pretty/list/")

    # 校验失败(在页面上显示错误信息)
    return render(request, "pretty_add.html", {"form": form})


def pretty_edit(request, nid):
    """编辑靓号"""
    row_obj = models.PrettyNum.objects.filter(id=nid).first()

    # GET请求
    if request.method == "GET":
        form = PrettyEditModelForm(instance=row_obj)
        return render(request, "pretty_edit.html", {"form": form})

    # POST请求
    form = PrettyEditModelForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        return redirect("/pretty/list/")

    return render(request, "pretty_edit.html", {"form": form})


def pretty_delete(request, nid):
    """删除靓号"""
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect('/pretty/list/')
