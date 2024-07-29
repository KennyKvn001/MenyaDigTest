from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, VideoPost
from .forms import RoomForm, UserForm, MyUserCreationForm, VideoPostForm


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username OR password does not exit")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")

    return render(request, "base/login_register.html", {"form": form})


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    ).select_related("host")

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:3]

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


@login_required(login_url="login")
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    return render(request, "base/update-user.html", {"form": form})


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topics.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, "base/activity.html", {"room_messages": room_messages})


# List view
def video_post_list(request):
    video_posts = VideoPost.objects.all()
    post_count = video_posts.count()
    topics = Topic.objects.all()[0:5]

    context = {
        "video_posts": video_posts,
        "topics": topics,
        "post_count": post_count,
    }
    return render(request, "base/video_post_list.html", context)


# Detail view
def video_post_detail(request, pk):
    video_post = get_object_or_404(VideoPost, pk=pk)
    return render(request, "base/video_post_detail.html", {"video_post": video_post})


# Create view
@login_required(login_url="login")
def video_post_create(request):
    if request.method == "POST":
        form = VideoPostForm(request.POST, request.FILES)
        if form.is_valid():
            video_post = form.save(commit=False)
            video_post.creator = request.user
            video_post.save()
            return redirect("video_post_list")
    else:
        form = VideoPostForm()
    return render(request, "base/video_post_form.html", {"form": form})


# Update view
@login_required(login_url="login")
def video_post_update(request, pk):
    video_post = get_object_or_404(VideoPost, pk=pk)
    if request.user != video_post.creator:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = VideoPostForm(request.POST, request.FILES, instance=video_post)
        if form.is_valid():
            form.save()
            return redirect("video_post_detail", pk=video_post.pk)
    else:
        form = VideoPostForm(instance=video_post)
    return render(request, "base/video_post_form.html", {"form": form})


# Delete view
@login_required(login_url="login")
def video_post_delete(request, pk):
    video_post = get_object_or_404(VideoPost, pk=pk)
    if request.user != video_post.creator:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == "POST":
        video_post.delete()
        return redirect("video_post_list")
    return render(
        request, "base/video_post_confirm_delete.html", {"video_post": video_post}
    )


def like_video(request, pk):
    video = get_object_or_404(VideoPost, pk=pk)
    if request.method == "POST":
        video.toggle_like(request.user)
        return JsonResponse(
            {
                "likes_count": video.likes.count(),
                "liked": request.user in video.likes.all(),
            }
        )
    return JsonResponse({"error": "Invalid request"}, status=400)
