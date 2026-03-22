from django.urls import path
from . import views
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView, 
    PostDeleteView, 
    UserPostListView
)

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    # Stripe Payments
    path('post/<int:pk>/buy/', views.create_checkout_session, name='buy-now'),
    path('post/<int:pk>/success/', views.payment_success, name='payment-success'),
    
    # Cart & Purchases
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('my-purchases/', views.my_purchases, name='my-purchases'),
    
    # Messages & Chat
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:post_id>/<int:user_id>/', views.chat_view, name='chat-view'),
    
    # Misc
    path('about/', views.about, name='blog-about'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),
]