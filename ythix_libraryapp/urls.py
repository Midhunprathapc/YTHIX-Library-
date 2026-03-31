from django.urls import path
from .views import *

urlpatterns = [  

    path('', home, name='home'),
    path('signup/', usersignup, name='signup'),
    path('login/', login_view, name='login_view'),
    path('logout/', logout_user, name='logout'),


    path('admin_approve/', admin_approve_list, name='admin_approve_list'),
    path('approve/<int:k>/', approve_user, name='approve_user'),
    path('delete_user/<int:k>/', delete_user, name='delete_user'),
    path('view-users/', view_users, name='view_users'),
    path('dashboard/rental-history/', admin_rental_history, name='admin_rental_history'),
    path('dashboard/purchase-history/', admin_purchase_history, name='admin_purchase_history'),


    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('inventory/', show_books, name='show_books'),
    path('add_book/', add_book, name='add_book'),
    path('edit-book/<int:id>/', edit_book, name='edit_book'),
    path('delete-book/<int:id>/', delete_book, name='delete_book'),
    
    path('add-author-category/', add_author_category, name='add_author_category'),
    path('delete-author/<int:a_id>/', delete_author, name='delete_author'),
    path('delete-category/<int:bt_id>/', delete_book_category, name='delete_book_category'),
    path('delete-publisher/<int:p_id>/',delete_publisher, name='delete_publisher'),

    
    path('my-rentals/', user_rental_book, name='rental_history'),
    path('rent-book/<int:book_id>/', rent_book, name='rent_book'),
    path('return-book/<int:rental_id>/', return_book, name='return_book'),
    path('report-lost/<int:rental_id>/', report_lost, name='report_lost'),
    path('rental-pay/<int:rental_id>/', rental_payment, name='rental_payment'),

    
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('profile/', user_profile, name='user_profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('reset-password/', reset_password, name='reset_password'),
    path('user_home/', user_home, name='user_home'),
    path('user_base/', user_base, name='user_base'),

    
    path('library-books/', user_showbooks, name='user_showbooks'),
    path('category/<int:cat_id>/', category_filter, name='category_filter'),
    
    
    path('cart/', cart_pg, name='cart_pg'),
    path('add-to-cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('increase-qty/<int:item_id>/', increase_qty, name='increase_qty'),
    path('decrease-qty/<int:item_id>/', decrease_qty, name='decrease_qty'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout_view, name='checkout_view'),

]