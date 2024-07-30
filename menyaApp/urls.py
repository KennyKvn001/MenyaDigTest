from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("profile/<str:pk>/", views.userProfile, name="user-profile"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
    path("update-user/", views.updateUser, name="update-user"),
    path("topics/", views.topicsPage, name="topics"),
    path("activity/", views.activityPage, name="activity"),
    path("video/<int:pk>/", views.video_post_detail, name="video_post_detail"),
    path("video/new/", views.video_post_create, name="video_post_create"),
    path("video/<int:pk>/edit/", views.video_post_update, name="video_post_update"),
    path(
        "video/<int:pk>/delete/",
        views.video_post_delete,
        name="video_post_delete",
    ),
    path("video/", views.video_post_list, name="video_post_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
