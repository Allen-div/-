from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from user.views import RegisterView, LoginView, LogoutView, UserInfoView, UserOrderView, AddressView

urlpatterns = [
    #url(r'^register$',views.register,name='register'),#注册页面
    #url(r'^register_handle$',views.register_handle,name='register'),#注册处理

    url('^register$',RegisterView.as_view(),name='register'), #注册
    url('^login$',LoginView.as_view(),name='login'), #登录
    url('^logout$',LogoutView.as_view(),name='logout'),#退出登录

    # url('^$',login_required(UserInfoView.as_view()),name='user'), #用户中心-信息页
    # url('^order$',login_required(UserOrderView.as_view()),name='order'), #用户中心-订单页面
    # url('^address$',login_required(AddressView.as_view()),name='address'), #用户中心-地址页面

    url('^$',UserInfoView.as_view(),name='user'), #用户中心-信息页
    url('^order/(?P<page>\d+)$',UserOrderView.as_view(),name='order'), #用户中心-订单页面
    url('^address$',AddressView.as_view(),name='address'), #用户中心-地址页面
]
