from django import forms

class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段,给每个字段的插件设置
        for _, field in self.fields.items():
            # 字段中有属性,保留原来的属性,没有属性,才增加
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs = {
                    "class": "form-control",
                }

from django import forms

class BootStrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootStrapForm, self).__init__(*args, **kwargs)
        # 遍历 Form 中的所有字段
        for field_name, field in self.fields.items():
            # 如果字段已有 class 属性，则添加 'form-control' 类
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                # 如果字段没有 class 属性，则设置为 'form-control'
                field.widget.attrs['class'] = 'form-control'
