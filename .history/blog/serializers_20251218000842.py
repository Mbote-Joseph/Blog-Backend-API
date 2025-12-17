# Copyright 2025 josephmbote
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers

from .models import Category, Tag, Post, Comment
import bleach

def validate_content(self, value):
    return bleach.clean(value, tags=["p","b","i","strong","em","ul","ol","li","br","a"], attributes={"a":["href"]})


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        

class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    tags_names = serializers.CharField(
        source = "tags.name",
        read_only = True
    )
    class Meta:
        model = Post
        fields = ["id", "image", "title", "content", "is_published", "created_at", "author", "category", "category_name", "tags", "tags_name"]
        read_only_fields = ["created_at", "author"]
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["created_at", "user"]