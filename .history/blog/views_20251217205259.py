from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer

# Create your views here.
class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user) or request.user.is_staff
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        # Public read
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Admin/staff for write
        return [permissions.IsAdminUser()]
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    


# --- Posts ---
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "tags", "author", "is_published"]
    search_fields = ["title", "content", "category__name", "tags__name"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Public users: only published posts
        if not self.request.user.is_authenticated:
            return Post.objects.filter(is_published=True).order_by("-created_at")
        # Logged-in users: see all (you can adjust this rule later)
        return Post.objects.all().order_by("-created_at")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        # update/delete requires author or admin
        return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]

    def perform_create(self, serializer):
        # Automatically assign logged-in user as author
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        post = self.get_object()

        # Only author or admin can publish
        if not ((post.author == request.user) or request.user.is_staff):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        post.is_published = True
        post.save()
        return Response({"detail": "Post published successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unpublish(self, request, pk=None):
        post = self.get_object()

        if not ((post.author == request.user) or request.user.is_staff):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        post.is_published = False
        post.save()
        return Response({"detail": "Post unpublished successfully."}, status=status.HTTP_200_OK)


# --- Comments ---
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["post"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        # Public: only approved comments
        if not self.request.user.is_authenticated:
            return Comment.objects.filter(is_approved=True).order_by("-created_at")

        # Admin/staff: see all
        if self.request.user.is_staff:
            return Comment.objects.all().order_by("-created_at")

        # Authenticated users: see approved + their own unapproved comments
        return Comment.objects.filter(
            models.Q(is_approved=True) | models.Q(user=self.request.user)
        ).order_by("-created_at")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ["approve", "reject"]:
            return [permissions.IsAdminUser()]
        # update/delete: comment owner OR admin
        return [permissions.IsAuthenticated(), IsCommentOwnerOrAdmin()]


    def perform_create(self, serializer):
        # Normal users create comments as pending approval
        serializer.save(user=self.request.user, is_approved=False)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({"detail": "Comment approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        comment = self.get_object()
        comment.is_approved = False
        comment.save()
        return Response({"detail": "Comment rejected."}, status=status.HTTP_200_OK)
    
    

class IsCommentOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.user == request.user) or request.user.is_staff
