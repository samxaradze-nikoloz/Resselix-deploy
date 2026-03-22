import os
import stripe
from dotenv import load_dotenv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from rest_framework import generics, permissions, status

from .forms import PostForm
from .models import Post, Order, CartItem
from users.models import Message, Comment
from .serializers import PostSerializer, OrderSerializer, MessageSerializer, CommentSerializer

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

# --- BLOG VIEWS ---

def home(request):
    posts = Post.objects.filter(is_sold=False).select_related('author__profile').order_by('-date_posted')
    return render(request, 'blog/home.html', {'posts': posts})

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Post.objects.filter(is_sold=False).select_related('author__profile')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()
        return queryset.order_by('-date_posted')

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).select_related('author__profile').order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.get_object()).order_by('-date_posted')
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm 
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'price']
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    def test_func(self):
        return self.request.user == self.get_object().author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    def test_func(self):
        return self.request.user == self.get_object().author

# --- STRIPE / PAYMENT VIEWS ---

@login_required
def create_checkout_session(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.price < 0.50:
        messages.error(request, "Price must be at least $0.50 to use card payment.")
        return redirect('post-detail', pk=pk)
    if post.is_sold:
        messages.error(request, "This item has already been sold.")
        return redirect('blog-home')
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': post.title},
                    'unit_amount': int(post.price * 100), 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment-success', args=[post.id])),
            cancel_url=request.build_absolute_uri(post.get_absolute_url()),
        )
        Order.objects.create(
            buyer=request.user,
            post=post,
            amount=post.price,
            stripe_session_id=session.id,
            status='pending'
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('post-detail', pk=pk)

@login_required
def payment_success(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.is_sold = True
    post.save()
    Order.objects.filter(post=post, buyer=request.user).update(status='completed')
    messages.success(request, f"Payment successful! You bought {post.title}.")
    return render(request, 'blog/payment_success.html', {'post': post})

# --- CART VIEWS ---

@login_required
def add_to_cart(request, pk):
    post = get_object_or_404(Post, pk=pk)
    item, created = CartItem.objects.get_or_create(user=request.user, post=post)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart-detail')

@login_required
def cart_detail(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in items)
    return render(request, 'blog/cart_detail.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, pk):
    get_object_or_404(CartItem, pk=pk, user=request.user).delete()
    return redirect('cart-detail')

# --- OTHER VIEWS ---

@login_required
def chat_view(request, post_id, user_id):
    other_user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)
    chat_messages = Message.objects.filter(post=post).filter(
        (Q(sender=request.user) & Q(receiver=other_user)) | (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content: 
            Message.objects.create(sender=request.user, receiver=other_user, post=post, content=content)
        return redirect('chat-view', post_id=post.id, user_id=other_user.id)
    return render(request, 'blog/chat.html', {'chat_messages': chat_messages, 'other_user': other_user, 'post': post})

def my_purchases(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'blog/my_purchases.html', {'orders': orders})

@login_required
def inbox(request):
    msgs = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'blog/inbox.html', {'messages': msgs})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        Comment.objects.create(post=post, author=request.user, content=request.POST.get('content'))
    return redirect('post-detail', pk=pk)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})