from django.contrib import admin
from .models import *
from django.core.cache import cache

class BaseModeAdmin(admin.ModelAdmin):
    # 清除缓存
    #如果后台管理改变数据,或者删除数据，就要清除缓存
    def save_model(self, request, obj, form, change):
        """新增或者更新表中的数据时调用"""
        super().save_model(request, obj, form, change)
        cache.delete("index_page_data")

    def delete_model(self, request, obj):
        """删除表中的数据时调用"""
        super().delete_model(request, obj)
        cache.delete("index_page_data")

class GoodsTypeAdmin(BaseModeAdmin):
    pass

# class GoodsSKUAdmin(BaseModeAdmin):
#     pass
#
# class GoodsAdmin(BaseModeAdmin):
#     pass

# class GoodsImageAdmin(BaseModeAdmin):
#     pass

class IndexGoodsBannerAdmin(BaseModeAdmin):
    pass

class IndexTypeGoodsBannerAdmin(BaseModeAdmin):
    pass

class IndexPromotionBannerAdmin(BaseModeAdmin):
    pass

admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(GoodsSKU)
admin.site.register(Goods)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
