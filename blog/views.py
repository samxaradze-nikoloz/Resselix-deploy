import os
from collections import OrderedDict

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from .forms import PostForm
from .models import Post, PostImage, CartItem
from users.models import Message, Comment


# --- BLOG VIEWS ---

from django.db.models import Q
from collections import OrderedDict

from django.db.models import Q
from collections import OrderedDict
from django.views.generic import ListView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category')
        subcategory = self.request.GET.get('subcategory')

        queryset = Post.objects.filter(is_sold=False).select_related('author__profile').prefetch_related('images')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).distinct()

        if category:
            queryset = queryset.filter(category=category)

        if subcategory:
            queryset = queryset.filter(subcategory=subcategory)

        return queryset.order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # This is the filtered set of posts based on user search/selection
        filtered_posts = self.get_queryset()

        categories = OrderedDict([
            ('accessories', 'Accessories'),
            ('accounts', 'Accounts'),
            ('sports', 'Sports'),
            ('fashion', 'Fashion'),
            ('electronics', 'Electronics'),
            ('home', 'Home'),
            ('misc', 'Miscellaneous'),
        ])

        categorized_posts = OrderedDict()

        # Grouping the filtered results into sections
        for key, label in categories.items():
            cat_list = filtered_posts.filter(category=key)
            if cat_list.exists():
                categorized_posts[label] = cat_list

        context['categorized_posts'] = categorized_posts
        context['query'] = self.request.GET.get('q', '')
        return context
class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(
            author=user
        ).select_related('author__profile').prefetch_related('images').order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        context['comments'] = Comment.objects.filter(
            post=post
        ).order_by('-date_posted')

        context['images'] = PostImage.objects.filter(post=post)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Handle multiple images
        for f in self.request.FILES.getlist('images'):
            PostImage.objects.create(post=self.object, image=f)

        return response


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = [
        'title',
        'content',
        'price',
        'category',     
        'address',
        'latitude',
        'longitude'
    ]
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)


        for f in self.request.FILES.getlist('images'):
            PostImage.objects.create(post=self.object, image=f)

        return response

    def test_func(self):
        return self.request.user == self.get_object().author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author


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
    items = CartItem.objects.filter(user=request.user).select_related('post')
    total = sum(item.get_total_price() for item in items)

    return render(request, 'blog/cart_detail.html', {
        'items': items,
        'total': total
    })


@login_required
def remove_from_cart(request, pk):
    get_object_or_404(CartItem, pk=pk, user=request.user).delete()
    return redirect('cart-detail')


# --- MESSAGING ---

@login_required
def chat_view(request, post_id, user_id):
    other_user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)

    chat_messages = Message.objects.filter(post=post).filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                post=post,
                content=content
            )
        return redirect('chat-view', post_id=post.id, user_id=other_user.id)

    return render(request, 'blog/chat.html', {
        'chat_messages': chat_messages,
        'other_user': other_user,
        'post': post
    })


@login_required
def inbox(request):
    msgs = Message.objects.filter(
        receiver=request.user
    ).select_related('sender', 'post').order_by('-timestamp')

    return render(request, 'blog/inbox.html', {'messages': msgs})


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )

    return redirect('post-detail', pk=pk)


# --- OTHER PAGES ---

@login_required
def my_purchases(request):
    # Placeholder for future order functionality
    return render(request, 'blog/my_purchases.html', {'orders': []})


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})