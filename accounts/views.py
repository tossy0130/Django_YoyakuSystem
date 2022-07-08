from re import template
from django.views import View
from accounts.models import CustomUser
from accounts.forms import ProfileForm, SignupUserForm
from django.shortcuts import render, redirect
from allauth.account import views  # 追加
from django.contrib.auth.mixins import LoginRequiredMixin


# サインアップ処理
class SignupView(views.SignupView):
    template_name = 'accounts/singnup.html'
    form_class = SignupUserForm

# ログアウト処理


class LogoutView(views.LogoutView):
    template_name = 'accounts/logout.html'

    def post(self, *args, **kwargs):
        # ユーザーがログインしていたら
        if self.request.user.is_authenticated:
            self.logout()
        return redirect('/')


class LoginView(views.LoginView):
    template_name = 'accounts/login.html'

# プロフィール　get => 編集 , post => 保存


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        try:
            user_data = CustomUser.objects.get(id=request.user.id)
        except self.CustomUser.DoesNotExist:
            return None

        form = ProfileForm(
            request.POST or None,
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

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None)
        if form.is_valid():
            try:
                user_data = CustomUser.objects.get(id=request.user.id)
            except self.CustomUser.DoesNotExist:
                return None
            user_data.first_name = form.cleaned_data['first_name']
            user_data.last_name = form.cleaned_data['last_name']
            user_data.description = form.cleaned_data['description']
            # 画像
            if request.FILES.get('image'):
                user_data.image = request.FILES.get('image')
            user_data.save()
            return redirect('profile')

        return render(request, 'accounts/profile.html', {
            'form': form
        })


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            user_data = CustomUser.objects.get(id=request.user.id)
        except self.CustomUser.DoesNotExist:
            return None

        return render(request, 'accounts/profile.html', {
            'user_data': user_data,
        })
