from django.urls import include, path
from . import views
from .views import ImageUploadView, PostListView, MyListingsView, PostUpdateView,ImageDeleteView, PostDeleteView

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),

    path('about/', views.about, name='blog-about'),

    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/manage/', views.manage_post, name='post-manage'),
    path('user/<str:username>/', views.UserPostListView.as_view(), name='user-posts'),
 path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post-edit'),
    path('live-search/', views.live_search, name='live-search'),

    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),

    path('chat/<int:post_id>/<int:user_id>/', views.chat_view, name='chat-view'),
    path('inbox/', views.inbox, name='inbox'),

    path('my-purchases/', views.my_purchases, name='my-purchases'),
    path('my-listings/', MyListingsView.as_view(), name='my-listings'),

    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),

    path('forum/', views.forum_home, name='forum_home'),
    path('forum/create/', views.create_post, name='create_post'),
    path('forum/post/<int:pk>/', views.post_detail, name='forum-post-detail'),
    path('forum/like/<int:pk>/', views.like_post, name='like_post'),
    path('forum/search/', views.forum_search, name='forum_search'),
    path('forum/post/<int:pk>/delete/', views.delete_forum_post, name='delete_forum_post'),
    path('my-listings/', MyListingsView.as_view(), name='my-listings'),
    path('how-to-sell/', views.how_to_sell, name='how_to_sell'),
    path('contact/', views.contact_us, name='contact'),
    path('help/buying/', views.buying_help, name='buying-help'),
    path('company-info/', views.company_info, name='company-info'),
    path('news/', views.news_updates, name='news'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
path('image/<int:pk>/delete/', ImageDeleteView.as_view(), name='image-delete'),
path('post/<int:pk>/image-upload/', ImageUploadView.as_view(), name='image-upload'),

    path('forum/comment/<int:pk>/delete/', views.delete_forum_comment, name='delete-forum-comment'),

    path('i18n/', include('django.conf.urls.i18n')),
]