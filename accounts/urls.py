from django.urls import path
from accounts import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='account_signup'), # サインアップ
    path('login/', views.LoginView.as_view(), name='account_login'), # ログイン 
    path('logout/', views.LogoutView.as_view(), name="account_logout"), # ログアウト 
    path('profile/', views.ProfileView.as_view(), name='profile'),  # ユーザー作成
    path('profile/edit/', views.ProfileEditView.as_view(), name="profile_edit"),  #　ユーザー編集
]




