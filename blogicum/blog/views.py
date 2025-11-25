from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.generic import CreateView, DeleteView, UpdateView
from .forms import PostForm, UserForm, CommentForm
from .models import Category, Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q


def get_page_obj(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page') or 1
    return paginator.get_page(page_number)

def index(request):
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    template = "blog/index.html"

    page_obj = get_page_obj(request, posts)

    context = {"page_obj": page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    if request.user.is_authenticated:

        query = Q(pk=post_id) & (
            Q(author=request.user)
            | Q(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )
    else:

        query = Q(pk=post_id) & Q(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        query
    )

    comments = post.comments.filter(is_published=True).select_related(
        'author').order_by('created_at')
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    posts = category.posts.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now(),
    ).select_related(
        'author', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    page_obj = get_page_obj(request, posts)

    template = 'blog/category.html'
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)

    post_list = Post.objects.filter(
        author=user
    ).select_related(
        'author', 'location', 'category'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    if request.user != user:
        post_list = post_list.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    page_obj = get_page_obj(request, post_list)

    context = {
        'profile': user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        if isinstance(self.get_object(), Post):
            return redirect('blog:post_detail', post_id=self.get_object().id)
        elif isinstance(self.get_object(), Comment):
            return redirect('blog:post_detail',
                            post_id=self.get_object().post.id)
        return redirect('blog:index')


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.pk})


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.id})


class CommentUpdateView(AuthorRequiredMixin, UpdateView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.id})


class CommentDeleteView(AuthorRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.id})
