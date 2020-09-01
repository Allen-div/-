from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin

# Create your views here.
# /cart/add
# 参数传递商品id(sku_id)，商品数量(count)
class CartAddView(View):
    """购物车记录添加"""
    def post(self,request):
        """购物车记录添加"""
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'msg':0,'errmsg':'请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        # 校验数据的完整性
        if not all([sku_id,count]):
            return JsonResponse({'res':1,'errmsg':'数据不完整'})
        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res':2,'msg':"商品数目出错"})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res':3,'errmsg':'商品不存在'})


        # 业务处理：添加购物车记录
        # 如果已经有这个商品，数目进行累加，没有该商品进行添加
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # 现尝试获取sku_id商品的数据 -> hget cart_key 属性
        # 如果sku_id 在hash中不存在返回的是None
        cart_count = conn.hget(cart_key,sku_id)
        if cart_count:
            # 累加购物车中商品数目
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res':4,'errmsg':'商品库存不足'})
        # 设置hash中sku_id对应的值
        # hset -> 如果sku_id已经存在就覆盖掉原来的，如果不存在就添加
        conn.hset(cart_key,sku_id,count)

        # 计算用户车中商品的条目数
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res':5,'total_count':total_count,'errmsg':'添加成功'})

# /cart/
class CartInfoView(LoginRequiredMixin, View):
    """购物车页面显示"""
    def get(self,request):
        """显示"""
        #获取登陆的用户
        user = request.user
        # 获取用户购物车中商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # {'商品id'：商品数目}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品中数目的总数目和总价格
        total_count = 0
        total_price = 0
        # 遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price*int(count)
            # 动态给sku属性属性amount，保存商品的小计
            sku.amount = amount
            # 动态给sku属性属性count，保存商品的数量
            sku.count = count
            # 添加
            skus.append(sku)

            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {'total_count':total_count,
                   'total_price':total_price,
                   'skus':skus}

        # 使用模板
        return render(request,'cart.html',context)

# 更新购物车记录
# 使用ajax post
# 前端需要传递过来的是商品的id（sku_id），商品的数量（count）
# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""
    def post(self,request):
        """购物车记录更新"""
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'msg': 0, 'errmsg': '请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        # 校验数据的完整性
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'msg': "商品数目出错"})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理：更新redis数据库购物车数据
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # 校验商品库存
        if count > sku.stock:
            return JsonResponse({'res': 3, 'errmsg': '商品库存不足'})
        # 更新
        conn.hset(cart_key,sku_id,count)

        # 计算用户购物车中商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res': 5, 'total_count':total_count, 'errmsg': '更新成功'})


# 删除购物车记录
# 采用ajax post请求
# 前端要传过来的数据：商品id（sku_id）
# /cart/delete
class CartDeleteView(View):
    """删除购物车记录"""
    def post(self,request):
        """购物车记录删除"""
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 数据校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品数据'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        # 业务处理：删除用户车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # 删除
        conn.hdel(cart_key,sku_id)

        # 计算用户购物车中商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res': 3, 'total_count' : total_count, 'errmsg': '删除成功'})
