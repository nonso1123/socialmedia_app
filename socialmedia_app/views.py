from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import MyUser, Post
from .serializers import MyUserProfileSerializer, UserRegisterSerializer, PostSerializer, UserSerializer, UpdatePostSerializer
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def authenticated(request):
    return Response('Authenticated!')


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

class CustomTokenObtainPairView(TokenObtainPairView):
     def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            username = request.data.get("username")
            try:
                user = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                return Response({'error':'user does not exist'})
            res = Response()
            res.data = {'success': True,
                        "user": {
                            "username": user.username,
                            "bio": user.bio,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name
                            }
                        }

            res.set_cookie(
                key='access_token',
                value=access_token, 
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            res.set_cookie(
                key='refresh_token',
                value=refresh_token, 
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            return res
        except:
             return Response({'success': False})

class CustomTokenRefreshView(TokenRefreshView):
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens['access']
            res = Response()
            res.data = {"success": True}
            res.set_cookie(
                    key='access_token',
                    value=access_token, 
                    httponly=True,
                    secure=True,
                    samesite='None',
                    path='/'
                )
            return res
        except:
            return Response({'success': False})                                                 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_data(request, pk):
    try:
        user = MyUser.objects.get(username=pk)
    except MyUser.DoesNotExist:
        return Response({'error':'user does not exist'})
        
    serializer = MyUserProfileSerializer(user)
    following = False
    if request.user in user.followers.all():
        following = True
    return Response({**serializer.data, 'is_our_profile':request.user.username == user.username, 'following':following})
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggleFollow(request):
    
    try:
        my_user = MyUser.objects.get(username=request.user.username)
        user_to_follow = MyUser.objects.get(username=request.data.get('username'))
   
    except MyUser.DoesNotExist:
        return Response({'error':'user does not exist'})
    
    if my_user in user_to_follow.followers.all():
        user_to_follow.followers.remove(my_user)
        return Response({'now_following': False})
    else:
        user_to_follow.followers.add(my_user)
        return Response({'now_following': True}) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_posts(request, pk):
    try: 
        my_user = MyUser.objects.get(username=request.user.username)
        user = MyUser.objects.get(username=pk)
    except MyUser.DoesNotExist:
        return Response({'error':'user does not exist'})
    
    posts = user.posts.all().order_by('-created_at')
    
    serializer = PostSerializer(posts, many=True)
    data = []
    for post in serializer.data:
        new_post = {}
        if my_user.username in post['likes']:
            new_post = {**post, 'liked':True}
        else:
            new_post = {**post, 'liked':False}
        data.append(new_post)

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggleLike(request):
    try:
        post = Post.objects.get(id=request.data['id'])
    except Post.DoesNotExist:
        return Response({'error': 'post does not exist'}, status=404)

    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return Response({
        'now_liked': liked,
        'like_count': post.likes.count()  # Return the updated like count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    try: 
        try: 
            user = request.user
        except MyUser.DoesNotExist:
            return Response({'error':'user does not exist'})
        
        post = Post.objects.create(user=user, description=request.data.get('description'), post_image = request.data.get('post_image'))

        serializer = PostSerializer(post)
        return Response(serializer.data)

    except:
        return Response({'error': 'error creating post'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):
    try: 
        my_user = MyUser.objects.get(username=request.user.username)
    except MyUser.DoesNotExist:
        return Response({'error':'user does not exist'}) 
    posts = Post.objects.all().order_by('-created_at') 
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    data = []
    for post in serializer.data:
        new_post = {}
        if my_user.username in post['likes']:
            new_post = {**post, 'liked':True}
        else:
            new_post = {**post, 'liked':False}
        data.append(new_post)

    return paginator.get_paginated_response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_user(request):
    query = request.query_params.get("query", "")
    users = MyUser.objects.filter(username__icontains=query)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    try: 
        user = request.user
    except MyUser.DoesNotExist:
        return Response({'error':'user does not exist'})    
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({**serializer.data, "success": True})
    return Response({**serializer.errors, "success": False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        res = Response()
        res.data = {"success": True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except:
        return Response({"success": False})
    
@api_view(['PATCH', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_post(request, id):  # Include `id` as a parameter
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Post does not exist'}, status=404)

    # Handle GET method
    if request.method == 'GET':
        serializer = UpdatePostSerializer(post)
        return Response({
            **serializer.data,
            'like_count': post.likes.count(),  # Include like count
            'liked': request.user in post.likes.all()  # Indicate if the user liked the post
        })

    # Handle PATCH method
    if request.method == 'PATCH':
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({'error': 'Post does not exist'}, status=404)

    if post.user != request.user:
        return Response({'error': 'You are not permitted to update this post'}, status=403)

    description = request.data.get('description', post.description)
    post.description = description

    
    if request.method == 'DELETE':
        post.delete()
        return Response({'message': 'Post deleted successfully'})

    if 'post_image' in request.FILES:  # Update image only if a new file is provided
        post.post_image = request.FILES['post_image']
    post.save()
    return Response({'message': 'Post updated successfully'})

    
    
        