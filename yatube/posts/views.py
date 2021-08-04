from datetime import datetime as dt

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_page(request, paginator):
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    return paginator.get_page(page_number)


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, settings.POSTS_IN_PAGE)
    page = get_page(request, paginator)
    return render(request, "posts/index.html", {"page": page, })


def group_posts(request, slug="example"):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_IN_PAGE)
    page = get_page(request, paginator)
    return render(request, "posts/group.html",
                  {"group": group, "page": page, })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.POSTS_IN_PAGE)
    page = get_page(request, paginator)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author__username=username).exists()
    return render(request, "posts/profile.html",
                  {"author": author, "page": page,
                   "count": author.posts.count,
                   "following": following, })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    count = post.author.posts.count
    form = CommentForm(request.POST)
    comments = post.comments.all()
    return render(request, "posts/post.html",
                  {"author": post.author, "post": post,
                   "count": count,
                   "form": form,
                   "comments": comments})


@login_required()
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, "posts/new.html",
                      {"form": form, "operation": "Добавить запись",
                       "add_or_save": "Добавить"})
    form = PostForm(request.POST, files=request.FILES)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect(index)
    return render(request, "posts/new.html",
                  {"form": form, "operation": "Добавить запись",
                   "add_or_save": "Добавить", })


@login_required()
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.user != post.author:
        return redirect(post_view, post.author, post_id)

    if request.method != 'POST':
        form = PostForm(instance=post)
        return render(request, "posts/new.html",
                      {"form": form, "operation": "Редактировать запись",
                       "add_or_save": "Сохранить", "post": post, })
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.pub_date = dt.today()
        post.save()
        return redirect(post_view, post.author, post.id)
    return render(request, "posts/new.html",
                  {"form": form, "operation": "Редактировать запись",
                   "add_or_save": "Сохранить", "post": post})


def page_not_found(request, exception):
    return render(request, "misc/404.html",
                  {"path": request.path},
                  status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method != 'POST':
        form = CommentForm()
        return render(request, 'posts/comments.html', {'form': form})
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(post_view, username, post_id)
    return render(request, 'posts/comments.html', {'form': form})


@login_required
def follow_index(request):
    # так красиво, как магия)))
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.POSTS_IN_PAGE)
    page = get_page(request, paginator)
    return render(request, "posts/follow.html", {"page": page, })


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect(follow_index)
    Follow.objects.get_or_create(user=request.user,
                                 author=user)
    return redirect(follow_index)


@login_required
def profile_unfollow(request, username):
    request.user.follower.get(author__username=username).delete()
    return redirect(follow_index)
