import os
from collections import OrderedDict
from rapidfuzz import process, fuzz
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from .models import (
    Post,
    ForumPost,
    PostImage,
    CartItem,
    Like,
    PostComment,
    ForumComment,
    Comment
)

from .forms import PostForm, PostCommentForm, ForumCommentForm

from users.models import Message
from django.db import models
from django.views.generic import ListView
from rapidfuzz import fuzz

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category')
        subcategory = self.request.GET.get('subcategory')

        queryset = Post.objects.filter(is_sold=False).select_related(
            'author__profile'
        ).prefetch_related('images')

        if category:
            queryset = queryset.filter(category=category)

        if subcategory:
            queryset = queryset.filter(subcategory=subcategory)

        if query:
            scored = []
            for post in queryset:
                score = max(
                    fuzz.partial_ratio(query.lower(), post.title.lower()),
                    fuzz.partial_ratio(query.lower(), post.content.lower())
                )
                if score > 40:
                    scored.append((score, post))

            scored.sort(reverse=True, key=lambda x: x[0])
            queryset = [p for _, p in scored]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = context['posts']

        categorized = OrderedDict()
        for post in posts:
            label = post.category if post.category else "Other"
            categorized.setdefault(label, []).append(post)

        context['categorized_posts'] = categorized

        base_queryset = Post.objects.filter(is_sold=False).select_related(
            'author__profile'
        ).prefetch_related('images')

        context['popular_posts'] = base_queryset.order_by('-views')[:5]

        context['electronics_posts'] = base_queryset.filter(category='electronics').order_by('-views')[:5]
        context['fashion_posts'] = base_queryset.filter(category='fashion').order_by('-views')[:5]
        context['sports_posts'] = base_queryset.filter(category='sports').order_by('-views')[:5]

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        session_key = f"viewed_post_{self.object.id}"

        if not request.session.get(session_key):
            self.object.views += 1
            self.object.save(update_fields=['views'])
            request.session[session_key] = True

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object

        context['comments'] = post.post_comments.select_related('author').order_by('-created')
        context['comment_form'] = PostCommentForm()
        context['images'] = PostImage.objects.filter(post=post)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('login')

        form = PostCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()

        return redirect('post-detail', pk=self.object.pk)
from django.urls import reverse

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post-manage', kwargs={'pk': self.object.pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        print("FORM VALID TRIGGERED")

        form.instance.author = self.request.user
        self.object = form.save()

        print("CREATED POST ID:", self.object.id)

        main_image = self.request.FILES.get('main_image')
        if main_image:
            PostImage.objects.create(post=self.object, image=main_image)

        for f in self.request.FILES.getlist('images'):
            PostImage.objects.create(post=self.object, image=f)

        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        print("FORM INVALID:", form.errors)
        return super().form_invalid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Post
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Post

class MyListingsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/profile.html"   
    context_object_name = "listings"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).select_related(
            'author__profile'
        ).prefetch_related('images').order_by('-date_posted')

@login_required
def manage_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return redirect('blog-home')

    return render(request, 'blog/manage_post.html', {'post': post})


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




@login_required
def my_purchases(request):

    return render(request, 'blog/my_purchases.html', {'orders': []})


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})






def live_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"users": [], "posts": []})

    users = User.objects.filter(username__icontains=query)[:5]
    posts = Post.objects.filter(title__icontains=query)[:5]

    return JsonResponse({
        "users": [
            {
                "username": u.username,
                "image": u.profile.image.url if hasattr(u, "profile") and u.profile.image else "/static/users/default.jpg"
            }
            for u in users
        ],
        "posts": [
            {"id": p.id, "title": p.title}
            for p in posts
        ]
    })


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Post

class MyListingsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/my_listings.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user,
            is_sold=False
        ).select_related('author__profile').prefetch_related('images').order_by('-date_posted')




from django.db import models
from django.contrib.auth.models import User



def forum_home(request):
    posts = ForumPost.objects.filter(id__isnull=False).order_by('-created')
    return render(request, 'forum/home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == "POST":
        ForumPost.objects.create(
            author=request.user,
            title=request.POST.get('title'),
            content=request.POST.get('content')
        )
        return redirect('forum_home')
    return render(request, 'forum/create.html')

@login_required
def post_detail(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")

        if content:
            ForumComment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )

        return redirect("forum-post-detail", pk=post.pk)

    comments = post.forum_comments.select_related("author").order_by("-created")

    return render(request, "forum/detail.html", {
        "post": post,
        "comments": comments,
        "form": ForumCommentForm()
    })
@login_required
def like_post(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)

    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', 'forum_home'))

def how_to_sell(request):
    return render(request, 'blog/how_to_sell.html')



from django.shortcuts import render

def contact_us(request):
    return render(request, 'blog/contact.html')

def buying_help(request):
    return render(request, 'blog/buying_help.html')

def company_info(request):
    return render(request, 'blog/company_info.html')

def news_updates(request):

    return render(request, 'blog/news.html')    




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment

@login_required
def delete_forum_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    if comment.author != request.user and not request.user.is_staff:
        return redirect('forum-post-detail', pk=comment.post.pk)
    if request.method == "POST":
        post_pk = comment.post.pk
        comment.delete()
        return redirect('forum-post-detail', pk=post_pk)
    return redirect('forum-post-detail', pk=comment.post.pk)


def forum_search(request):
    query = request.GET.get("q", "").strip()

    posts = ForumPost.objects.all().select_related("author")

    if query:
        posts = posts.filter(title__icontains=query)

    return JsonResponse({
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content[:80],
                "author": p.author.username,
                "likes": p.total_likes() if hasattr(p, "total_likes") else p.likes.count(),
                "comments": p.comments.count() if hasattr(p, "comments") else 0,
                "created": p.created.strftime("%b %d, %Y")
            }
            for p in posts
        ]
    })

@login_required
def delete_forum_post(request, pk):
    post = get_object_or_404(ForumPost, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect('forum_home')
    return redirect('forum-post-detail', pk=pk)
