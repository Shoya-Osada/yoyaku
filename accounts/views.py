from django.views import View
from accounts.models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account import views 
from accounts.forms import ProfileForm, SignupUserForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        #モデルで作成した、CustomUserクラスからログイン中のユーザー情報を取得。
        user_data = CustomUser.objects.get(id=request.user.id)

        return render(request, 'accounts/profile.html', {
            'user_data': user_data,
        })

class ProfileEditView(LoginRequiredMixin, View):
    #getが最初に呼ばれる。
    def get(self, request, *args, **kwargs):
        user_data = CustomUser.objects.get(id=request.user.id)
        #テンプレートでフォームを表示するため、ProfileFormクラスを呼び出す。
        form = ProfileForm(
            request.POST or None,
            #フォームに初期値を与えるために、initialにデーターベースの情報を設定。
            #こうすることで、フォームに初期値を設定することができる。
            initial={
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'description': user_data.description,
                'image': user_data.image
            }
        )

        return render(request, 'accounts/profile_edit.html', {
            'form': form,
            'user_data': user_data
        })

    #post関数は、フォーム画面で登録ボタンを押したときに呼ばれる関数。
    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None)
        #formの内容をバリデーションして、問題がなければ、データーベースの値を置き換える。
        if form.is_valid():
            user_data = CustomUser.objects.get(id=request.user.id)
            user_data.first_name = form.cleaned_data['first_name']
            user_data.last_name = form.cleaned_data['last_name']
            user_data.description = form.cleaned_data['description']
            if request.FILES.get('image'):
                user_data.image = request.FILES.get('image')
            #save()を使うことで、保存。
            user_data.save()
            #保存後はプロフィール画面に画面遷移。
            return redirect('profile')
        
        #バリデーションに問題があれば、プロフィール画面に遷移。
        return render(request, 'accounts/profile.html', {
            'form': form
        })

#allauthのLoginViewクラスを継承させて、使用するテンプレートを上書きする。
#デフォルトでもlogin.htmlとなってるけど、すぐに拡張できるようにビューを作成。
class LoginView(views.LoginView):
    template_name = 'accounts/login.html'

#allauthのLogoutViewクラスを継承して上書き。
class LogoutView(views.LogoutView):
    template_name = 'accounts/logout.html'

    #ログアウトボタンを押すと、post関数が実行。
    def post(self, *args, **kwargs):
        #もしログイン状態であれば、self.logout()でログアウト。
        if self.request.user.is_authenticated:
            self.logout()
        #そして、トップページに画面遷移。
        return redirect('/')

#allauthのSignupViewクラスを継承して上書き。
class SignupView(views.SignupView):
    template_name = 'accounts/signup.html'
    #form_class変数に先ほど作成したSignupUserFormクラスを設定.
    #こうすることで、サインアップにオリジナルのフォームを使用可能になる。
    form_class = SignupUserForm