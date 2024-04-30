from app01.utils.modelform import BootStrapModelForm
from app01.models import UserInfo, PrettyNum
from django.core.exceptions import ValidationError
from django import forms


class UserModelForm(BootStrapModelForm):
    ### 自定义数据校验
    # 例如: 用户名最小三个字符
    # name = forms.CharField(min_length=3, label="用户名")

    class Meta:
        model = UserInfo
        fields = ["name", "password", "age", "account", "create_time", "gender", "depart"]
        # 逐一控制标签的样式
        # widgets = {
        #     "name": forms.TextInput(attrs={"class": "form-control"}),
        #     "password": forms.PasswordInput(attrs={"class": "form-control"}),
        # }

        # 这里让日期可以手动点击鼠标选择,所以单独拎出来,加上日期插件
        widgets = {
            # "create_time": forms.DateInput(attrs={'class': 'form-control', 'id': 'myDate'}),
            "create_time": forms.DateInput(attrs={'id': 'myDate'}),
        }


class PrettyModelForm(BootStrapModelForm):
    # 数据校验: 验证方式1
    # mobile = forms.CharField(
    #     label="手机号",
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误'),],
    # )

    class Meta:
        model = PrettyNum
        # fields = "__all__"    表示取表中所有的字段
        fields = ['mobile', 'price', 'level', 'status']
        # exclude = ['level']   表示取除了表中的某个字段的所有字段

    # 数据校验: 验证方式2
    def clean_mobile(self):
        txt_mobile = self.cleaned_data['mobile']

        if len(txt_mobile) != 11:
            # 验证不通过
            raise ValidationError('格式错误')

        exists_data = PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists_data:
            raise ValidationError("手机号已存在")

        # 验证通过
        return txt_mobile


class PrettyEditModelForm(BootStrapModelForm):
    # mobile = forms.CharField(disabled=True, label="手机号")

    # 数据校验: 验证方式1
    # mobile = forms.CharField(
    #     label="手机号",
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误'),],
    # )

    class Meta:
        model = PrettyNum
        # fields = "__all__"    表示取表中所有的字段
        fields = ['mobile', 'price', 'level', 'status']
        # exclude = ['level']   表示取除了表中的某个字段的所有字段

    # 数据校验: 验证方式2
    def clean_mobile(self):
        txt_mobile = self.cleaned_data['mobile']

        if len(txt_mobile) != 11:
            # 验证不通过
            raise ValidationError('格式错误')

        # exclude 表示排除哪一个数据
        # self.instance.pk 表示当前编辑的哪一行 id
        exists_data = PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists_data:
            raise ValidationError("手机号已存在")

        # 验证通过
        return txt_mobile
