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
from users.models import Message
from .models import Comment

from rapidfuzz import process, fuzz


from django.db.models import Q
from collections import OrderedDict

from django.db.models import Q
from collections import OrderedDict
from django.views.generic import ListView
from .models import Post


from rapidfuzz import process
from django.db.models import Q
from django.views.generic import ListView
from collections import OrderedDict
from .models import Post

from .models import Comment
from django import forms

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

        if query:
            scored_posts = []

            for post in queryset:
                score = max(
                    fuzz.partial_ratio(query.lower(), post.title.lower()),
                    fuzz.partial_ratio(query.lower(), post.content.lower())
                )
                if score > 40:
                    scored_posts.append((score, post))

            scored_posts.sort(reverse=True, key=lambda x: x[0])
            queryset = [p for _, p in scored_posts]

        if category:
            queryset = [p for p in queryset if p.category == category]

        if subcategory:
            queryset = [p for p in queryset if p.subcategory == subcategory]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get('q', '')

        users = []

        if query:
            all_users = User.objects.select_related('profile').all()

            usernames = [u.username for u in all_users]

            matches = process.extract(
                query,
                usernames,
                limit=10,
                score_cutoff=60
            )

            matched_names = [m[0] for m in matches]

            users = [
                u for u in all_users
                if u.username in matched_names
            ]

        filtered_posts = context['posts']

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

        for key, label in categories.items():
            cat_list = [
                p for p in filtered_posts if p.category == key
            ]
            if cat_list:
                categorized_posts[label] = cat_list

        context['users'] = users
        context['categorized_posts'] = categorized_posts
        context['query'] = query

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
        context['comments'] = Comment.objects.filter(post=post).order_by('-date_posted')

        context['comments'] = Comment.objects.filter(
            post=post
        ).order_by('-date_posted')
        context['comment_form'] = CommentForm()
        context['images'] = PostImage.objects.filter(post=post)



        return context
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('post-detail', pk=self.object.pk)
        
        # If invalid, return the normal get context with the failed form
        context = self.get_context_data()
        context['comment_form'] = form
        return self.render_to_response(context)
    

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

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



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            # Changed 'format' to 'forms'
            'content': forms.TextInput(attrs={
                'placeholder': 'Add a comment...', 
                'class': 'form-control'
            }),
        }