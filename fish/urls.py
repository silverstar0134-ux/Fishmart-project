"""
URL configuration for fish project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from members import views

urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('', views.intex_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('register/', views.registerview),
    path('seller/register/', views.seller_register, name='seller_register'),
    path('clogin/',views.loginview),
    path('sellerlogin/',views.sellerloginview),
    path('sellerlogin_new/',views.sellerloginview),
    path('cdashboard/', views.dashboard_view),
    path('customer/orders/', views.customer_orders_view, name='customer_orders'),
    path('customer/shopping-cart/', views.shopping_cart_view, name='shopping_cart'),
    
    # Seller Dashboard URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-fish/', views.seller_add_fish, name='seller_add_fish'),
    path('seller/manage-fish/', views.seller_manage_fish, name='seller_manage_fish'),
    path('seller/edit-fish/<int:fish_id>/', views.seller_edit_fish, name='seller_edit_fish'),
    path('seller/delete-fish/<int:fish_id>/', views.seller_delete_fish, name='seller_delete_fish'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/order/<int:order_id>/<str:action>/', views.seller_order_action, name='seller_order_action'),
    
    # Customer Cart and Order URLs
    path('cart/add/<int:fish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_index>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/place/', views.place_order, name='place_order'),
    path('order/confirm/<int:order_id>/', views.customer_confirm_delivery, name='customer_confirm_delivery'),
    
    # Superadmin URLs
    path('superadmin/', views.superadmin_redirect, name='superadmin'),
    path('superadmin/login/', views.superadmin_login, name='superadmin_login'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/manage-users/', views.superadmin_manage_users, name='superadmin_manage_users'),
    path('superadmin/edit-user/<int:user_id>/', views.superadmin_edit_user, name='superadmin_edit_user'),
    path('superadmin/delete-user/<int:user_id>/', views.superadmin_delete_user, name='superadmin_delete_user'),
    path('superadmin/approve-sellers/', views.superadmin_approve_sellers, name='superadmin_approve_sellers'),
    path('superadmin/approve-seller/<int:seller_id>/', views.superadmin_approve_seller, name='superadmin_approve_seller'),
    path('superadmin/reject-seller/<int:seller_id>/', views.superadmin_reject_seller, name='superadmin_reject_seller'),
    path('superadmin/all-orders/', views.superadmin_view_all_orders, name='superadmin_all_orders'),
    path('superadmin/seller-commission/', views.superadmin_seller_commission, name='superadmin_seller_commission'),
    path('superadmin/commission-details/', views.superadmin_commission_details, name='superadmin_commission_details'),
    path('superadmin/manage-categories/', views.superadmin_manage_categories, name='superadmin_manage_categories'),
    path('superadmin/block-user/<int:user_id>/', views.superadmin_block_user, name='superadmin_block_user'),
    path('superadmin/unblock-user/<int:user_id>/', views.superadmin_unblock_user, name='superadmin_unblock_user'),
    path('superadmin/messages/', views.admin_messages, name='admin_messages'),
    path('superadmin/messages/<int:message_id>/reply/', views.admin_reply_message, name='admin_reply_message'),
  
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
