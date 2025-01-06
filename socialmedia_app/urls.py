from django.urls import path
from .views import get_user_profile_data, CustomTokenObtainPairView, CustomTokenRefreshView, register, authenticated, toggleFollow, get_users_posts, toggleLike, create_post, get_posts, search_user, update_user, logout, update_post, check_username


urlpatterns = [
    path('user_data/<str:pk>/', get_user_profile_data),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register),
    path('authenticated/', authenticated),
    path('toggleFollow/', toggleFollow),
    path('posts/<str:pk>/', get_users_posts),
    path('toggleLike/', toggleLike),
    path('create_post/', create_post),
    path('get_posts/', get_posts),
    path('search_user/', search_user),
    path('update_user/', update_user),
    path('logout/', logout),
    path('update_post/<int:id>/', update_post),
    path('check-username/', check_username),
]