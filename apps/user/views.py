from django.shortcuts import render,redirect
from  django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from user.models import User, Address
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from utils.mixin import LoginRequiredMixin
import re
from django.views.generic import View
from  django_redis import get_redis_connection
# Create your views here.


#user/register
def register(request):
    """注册"""
    if request.method == 'GET':
        #显示注册页面
        return render(request,'register.html')
    if request.method == 'POST':
        #进行注册处理
        #接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        #进行数据校验
        if not all([username,password,email]):
            #数据不完整
            return render(request,'register.html',{'errmsg':'数据不完整'})
        #校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request,'register.html',{'errmsg':'邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        #校验用户名是否重复
        try:
            user= User.objects.get(username=username)
        except User.DoesNotExist:
            #用户名不存在
            user = None

        if user:
            #用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        #进行业务处理：进行用户注册
        user = User.objects.create_user(username,email,password)
        user.is_active = 0
        user.save()

        #返回应答,跳转到首页
        return redirect(reverse("goods:index"))

def register_handle(request):
    """进行注册的处理"""
    #接收数据
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
    #进行数据校验
    if not all([username,password,email]):
        #数据不完整
        return render(request,'register.html',{'errmsg':'数据不完整'})
    #校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        return render(request,'register.html',{'errmsg':'邮箱格式不正确'})
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请同意协议'})

    #校验用户名是否重复
    try:
        user= User.objects.get(username=username)
    except User.DoesNotExist:
        #用户名不存在
        user = None

    if user:
        #用户名已存在
        return render(request, 'register.html', {'errmsg': '用户名已存在'})
    #进行业务处理：进行用户注册
    user = User.objects.create_user(username,email,password)
    user.is_active = 0
    user.save()

    #返回应答,跳转到首页
    return redirect(reverse("goods:index"))

class RegisterView(View):
    """注册"""
    def get(self,request):
        """显示注册页面"""
        return render(request,'register.html')
    def post(self,request):
        """进行注册"""
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 1
        user.save()

        # 返回应答,跳转到首页
        return redirect(reverse("goods:index"))

#/user/login
class LoginView(View):
    """登录"""
    def get(self,request):
        """显示登录页面"""
        #判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request,'login.html',{"username":username,'checked':checked})

    def post(self,request):
        """登录处理"""
        #接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")

        #校验处理
        if not all([username,password]):
            #数据不完整
            return render(request,'login.html',{"errmsg":"数据不完整"})

        #业务处理：登陆校验
        user = authenticate(username=username,password=password)
        if user is not None:
            #用户名密码正确
            if user.is_active ==1:
                #用户已激活
                #记录用户的登录状态
                login(request,user)

                #获取登陆后所要跳转到的地址
                # #当直接访问登陆页面是，就没有next，拿到的是None,这是要设置一个默认值，是首页
                #如果获取到next的值，跳转到next的值，否则默认跳转到首页
                next_url = request.GET.get('next',reverse("goods:index"))

                response = redirect(next_url)

                #判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)

                else:
                    response.delete_cookie('username')

                #返回response
                return response

            else:
                return render(request, 'login.html', {"errmsg": "用户未激活"})

            pass
        else:
            #用户名或者密码错误
            return render(request, 'login.html', {"errmsg": "用户名或密码错误"})

#/user/logout
class LogoutView(View):
    '''退出登录'''
    def get(self,request):
        #清楚用户的session信息
        logout(request)
        #跳转到首页
        # return  render(request,'index.html')
        return redirect(reverse("goods:index"))

#/user  用户登录之后才能访问
class UserInfoView(LoginRequiredMixin,View):
    """用户中心信息页"""
    def get(self,request):
        #page:'user'
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        con = get_redis_connection('default')
        history_key = 'history_%d'%user.id
        # 获取用户最新浏览器5个商品的id
        sku_ids = con.lrange(history_key,0,4)

        # 从数据库中查询，用户浏览商品信息
        #goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        # 遍历获取用户浏览商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        #组织上下文
        context = {"page":"user","address":address,'goods_li':goods_li}

        # 获取用户的个人信息
        return render(request,'user_center_info.html',context)
#/user/order  用户登录之后才能访问
class UserOrderView(LoginRequiredMixin,View):
    """用户中心信息页"""
    def get(self,request, page):
        '''显示'''
        # page:'order'
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品信息
        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算每个商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount= order_sku.price*order_sku.count
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount = amount
            # 动态增加属性，保存订单状态
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给订单order增加属性，保存订单中商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders,2)

        # 获取第page页的内容
        # 如果用户输入的页数不能转化为数字
        try:
            page = int(page)
        except Exception as e:
            page = 1

        # 如果用户输入的页数超过数据有的页数
        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # 进行页码控制，页面上最多显示5个页码
        # 1、总页数小于5页，页面上显示所有页码
        # 2、如果当前页是前三页的时候，显示前五页的页码
        # 3、如果当前页是后三页，显示后5页的页码
        # 4、显示当前页的前两页，当前页，当前页的后两页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)


        # 组织上下文
        context = {
            'order_page':order_page,
            'pages':pages,
            "page": "order",
        }
        # 使用模板
        return render(request,'user_center_order.html',context)
#/user/address  用户登录之后才能访问
class AddressView(LoginRequiredMixin,View):
    """用户中心信息页"""
    def get(self,request):
        """显示"""
        # page:'address'
        # 获取登陆的user对象
        user = request.user
        # 获取用户的默认收货地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        #     print(address)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request,'user_center_site.html',{"page":"address",'address':address})
    def post(self,request):
        """地址添加"""
        #接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        #校验数据
        if not all([receiver,addr,phone]):
            """数据不完整"""
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        #校验手机号
        reg = '1([38][0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|9[89])\d{8}'
        if not re.match(reg,phone):
            return render(request,'user_center_site.html',{'errmsg':'手机号格式不正确！'})
        #业务处理：地址添加
        # 如果已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        #获取登陆的user对象
        user= request.user
        # try:
        #     address = Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     #不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        #添加地址
        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,
                               phone=phone,is_default=is_default)
        #返回应答,刷新地址页面
        return redirect(reverse('user:address'))

