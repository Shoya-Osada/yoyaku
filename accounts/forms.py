from django import forms
from allauth.account.forms import SignupForm # 追加


#プロフィール編集用のフォーム
class ProfileForm(forms.Form):
    #名前と所属を編集したいから、フォームにフィールドを追加。
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30, label='名')
    description = forms.CharField(label='自己紹介', widget=forms.Textarea(), required=False)
    image = forms.ImageField(required=False, )

#allauthのSignupFormクラスを継承＆上書き。
class SignupUserForm(SignupForm):
    #メアドとパスはallauthですでに設定してるため、必要なし。
    #ここでは名前のみ
    #もし所属など、サインアップ時に入力してほしい場合は、ここに追加。
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30, label='名')

    #サインアップボタンが押されたら、save関数が実行。
    def save(self, request):
        user = super(SignupUserForm, self).save(request)
        #self.cleaned_dataでフォームに記載された内容を取得し、save関数でデーターベースに保存。
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user