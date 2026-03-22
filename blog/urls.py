from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),  # <-- add this
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('user/<str:username>', views.UserPostListView.as_view(), name='user-posts'),
    
    # CART & PAYMENT
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('post/<int:pk>/buy/', views.create_checkout_session, name='buy-now'),
    path('payment-success/<int:pk>/', views.payment_success, name='payment-success'),
    
    # MESSAGING & OTHERS
    path('chat/<int:post_id>/<int:user_id>/', views.chat_view, name='chat-view'),
    path('inbox/', views.inbox, name='inbox'),
    path('my-purchases/', views.my_purchases, name='my-purchases'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),
]