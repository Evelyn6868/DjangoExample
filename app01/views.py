import io

from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from reportlab.pdfgen import canvas

from app01 import models
from app01.form.form import UserModelForm, PrettyModelForm, PrettyEditModelForm
from app01.utils.modelform import BootStrapModelForm,BootStrapForm
from app01.utils.pagination import Pagination
from django import forms


# Create your views here.


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


def admin_list(request):
    """管理员列表"""

    data_dict = {}
    # 不加后面的 "", 首次访问浏览器,搜索框中不会显示前端页面中的 placeholder="Search for..." 属性
    search_data = request.GET.get('query', "")
    if search_data:
        data_dict["username__contains"] = search_data

    queryset = models.Admin.objects.filter(**data_dict).order_by("id")

    # queryset = Admin.objects.all()
    page_object = Pagination(request, queryset, page_size=2)
    page_queryset = page_object.page_queryset
    page_object.html()
    page_string = page_object.page_string

    context = {
        "page_queryset": page_queryset,
        "page_string": page_string,
        "search_data": search_data,
    }

    return render(request, "admin_list.html", context)


import hashlib
from django.conf import settings


def md5(data_string):
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()





class AdminModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput
        }

    # 钩子函数
    # clean_字段名
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        # return什么.password字段保存什么
        return md5(pwd)

    # 钩子函数
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        if md5(confirm) != pwd:
            raise ValidationError("密码不一致!")

        # return返回什么,字段 confirm_password 保存至数据库的值就是什么
        return md5(confirm)


def admin_add(request):
    """添加管理员"""

    title = "新建管理员"

    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "change.html", {"form": form, "title": title})

    # 如果是POST请求
    form = AdminModelForm(data=request.POST)

    context = {
        "form": form,
        "title": title,
    }

    if form.is_valid():
        form.save()
        return redirect("/admin/list")

    return render(request, "change.html", context)


# 如果不想让用户修改密码,只能修改用户名,那么使用下面这个AdminEditModelForm
# 如果都可以修改,直接用上面的AdminModelForm即可
class AdminEditModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin
        fields = ["username","password"]


def admin_edit(request, nid):
    # 判断 nid 是否存在
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {"msg": "数据不存在!"})

    """编辑管理员"""

    title = "编辑管理员"

    if request.method == "GET":
        form = AdminEditModelForm(instance=row_object)
        return render(request, "change.html", {"form": form, "title": title})

    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')

    return render(request, "change.html", {"form": form, "title": title})


def admin_delete(request, nid):
    """删除管理员"""
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list/")


class AdminResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True),
    )

    class Meta:
        model = models.Admin
        fields = ["password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    # clean_字段名
    def clean_password(self):
        pwd = self.cleaned_data.get("password")

        # 校验当前数据库中的密码与用户输入的新密码是否一致
        exists = models.Admin.objects.filter(id=self.instance.pk, password=md5(pwd))
        if exists:
            raise ValidationError("密码不能与当前密码一致!")

        # return什么.password字段保存什么
        return md5(pwd)

    # 钩子函数
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        if md5(confirm) != pwd:
            raise ValidationError("密码不一致!")

        # return返回什么,字段 confirm_password 保存至数据库的值就是什么
        return md5(confirm)


def admin_reset(request, nid):
    """重置管理员密码"""

    # 判断 nid 是否存在
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {"msg": "数据不存在!"})

    title = "重置密码 - {}".format(row_object.username)

    if request.method == "GET":
        form = AdminResetModelForm(instance=row_object)

        return render(request, "change.html", {"title": title, "form": form})

    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")

    return render(request, "change.html", {"title": title, "form": form})


# 这一次不使用ModelForm,使用Form来实现
class LoginForm(BootStrapForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    password = forms.CharField(
        label="用户名",
        # render_value=True 表示当提交后,如果密码输入错误,不会自动清空密码输入框的内容
        widget=forms.PasswordInput(attrs={"class": "form-control"}, ),
        required=True,
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


def login(request):
    """登录"""
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 验证成功, 获取到的用户名和密码
        print(form.cleaned_data)
        # {'username': '123', 'password': '123'}
        # {'username': '456', 'password': '0f54af32f41a5ba8ef3a2d40cd6ccf25'}

        # 去数据库校验用户名和密码是否正确
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})

        # 如果用户名密码正确
        # 网站生成随机字符创,写到用户浏览器的cookie中,再写入到服务器的session中
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}
        return redirect("/admin/list/")

    return render(request, 'login.html', {"form": form})

def logout(request):
    """ 注销 """

    # 清楚当前session
    request.session.clear()

    return redirect("/login/")


