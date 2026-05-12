from django.urls import path
from app import views, shop3_views
from django.conf import settings  
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('product/', views.product, name='product'),
    path('checkout/', views.checkout, name='checkout'),
    path('blank/', views.blank, name='blank'),
    path('categories/', views.categories, name='categories'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('shop/quick_view/', views.quick_view, name='quick_view'),
    path('cart/',views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('book_table/', shop3_views.book_table, name='book_table'),
    path('custom_admin/', shop3_views.dashboard, name='dashboard'),
    path('custom_admin/login/', shop3_views.custom_admin_login, name='custom_admin_login'),
    path('custom_admin/product_view/', shop3_views.product_view, name='product_view'),
    path('bulk-delete-products/', shop3_views.bulk_delete_products, name='bulk_delete_products'),
    path('product-preview/<int:product_id>/', shop3_views.product_preview, name='product_preview'),
    path('product-delete/<int:product_id>/', shop3_views.product_delete_view, name='product_delete'),
    path('add-product/', shop3_views.add_product, name='add_product'),
    path('send-whatsapp/', views.send_whatsapp_message, name='send_whatsapp'),
    # path('send-whatsapp/', views.send_buttons, name='send_whatsapp'),
    # path('webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
     

]




if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
