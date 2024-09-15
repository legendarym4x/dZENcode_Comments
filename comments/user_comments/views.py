import json
from datetime import datetime
from io import BytesIO

from PIL import Image
from bleach import clean
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from lxml import etree
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CommentForm
from .models import Post, Comment, UserInfo
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

from .serializers import CommentSerializer, PostSerializer


# Set allowed tags and attributes for cleaning the text
BLEACH_ALLOWED_TAGS = settings.BLEACH_ALLOWED_TAGS
BLEACH_ALLOWED_ATTRIBUTES = settings.BLEACH_ALLOWED_ATTRIBUTES


# When creating a comment or post
def save_user_info(user_name, email):
    # Check if such a user exists in the database
    user_info, created = UserInfo.objects.get_or_create(
        user_name=user_name,
        email=email
    )
    return user_info


def get_captcha(request):
    if request.method == 'GET':
        captcha = CaptchaStore.generate_key()
        image_url = captcha_image_url(captcha)
        request.session['expected_captcha'] = captcha
        response_data = {
            'key': captcha,
            'image_url': image_url
        }
        return JsonResponse(response_data)


class CommentAPIView(APIView):
    # GET method to retrieve comments for a post
    def get(self, request, year, month, day, post_id):
        post = get_object_or_404(Post, id=post_id, status='published', publish__year=year, publish__month=month,
                                 publish__day=day)

        # Extract sorting and ordering parameters
        sort_by = request.GET.get('sort_by')
        order = request.GET.get('order', 'asc')

        # Choose sorting based on sort_by parameter
        if sort_by == 'user_name':
            if order == 'desc':
                comments = Comment.objects.filter(post=post).order_by('-user_name')
            else:
                comments = Comment.objects.filter(post=post).order_by('user_name')
        elif sort_by == 'email':
            if order == 'desc':
                comments = Comment.objects.filter(post=post).order_by('-email')
            else:
                comments = Comment.objects.filter(post=post).order_by('email')
        elif sort_by == 'date_added':
            if order == 'desc':
                comments = Comment.objects.filter(post=post).order_by('-created_at')
            else:
                comments = Comment.objects.filter(post=post).order_by('created_at')
        else:
            comments = Comment.objects.filter(post=post).select_related('post', 'parent').order_by(
                '-created_at')

        # Convert comments to a dictionary
        comments_dict = {comment.id: CommentSerializer(comment).data for comment in comments}

        # Group child comments according to parent comments
        parent_to_children = {}
        for comment in comments_dict.values():
            comment['created_at'] = datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%H:%M %d.%m.%Y")
            parent_comment = comment.get('parent_comment')
            if parent_comment:
                parent_id = parent_comment
                parent_to_children.setdefault(parent_id, []).append(comment)

        # Select root comments and add child comments to them
        root_comments = [comment for comment in comments_dict.values() if not comment.get('parent_comment')]

        def add_children_to_parent(comment):
            children = parent_to_children.get(comment['id'], [])
            comment['children'] = children
            for child in children:
                add_children_to_parent(child)

        for comment in root_comments:
            add_children_to_parent(comment)

        # Pagination of the results
        paginator = pagination.PageNumberPagination()
        paginator.page_size = 25
        page = paginator.paginate_queryset(root_comments, request)

        # Serialize post and return the result
        post_serializer = PostSerializer(post)
        result = {
            'post': post_serializer.data,
            'comments': page,
            'page': request.GET.get('page', 1),
            'total_pages': paginator.page.paginator.num_pages,
        }
        return Response(result)

    # POST method to create a new comment
    def post(self, request, year, month, day, post_id):
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Method not supported'}, status=405)
        try:
            data = request.data
            print(data)
            c_key = data.get('captcha_key', '')
            captcha_stores = CaptchaStore.objects.filter(hashkey=c_key)
            captcha_store = captcha_stores.first()
            c_value = data.get('captcha_value', '')
            print(c_key + ' value: ' + c_value + ' expected: ' + captcha_store.response)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error parsing JSON'}, status=400)

        # Create a comment form
        form = CommentForm(data, request.FILES)

        if form.is_valid():
            # CAPTCHA validation
            if captcha_store.response != c_value:
                return JsonResponse({'success': False, 'message': 'Incorrect CAPTCHA'}, status=400)

            parent_id = data.get('parent_comment')
            post = get_object_or_404(Post, id=post_id)
            parent_comment = get_object_or_404(Comment, id=parent_id) if parent_id else None

            comment = form.save(commit=False)
            comment.post = post
            comment.parent_comment = parent_comment

            # Add a CAPTCHA value to the comment
            comment.captcha = c_value

            # Clean the comment text from unwanted tags
            cleaned_text = clean(comment.text, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRIBUTES)
            comment.text = cleaned_text

            # Validate XHTML markup
            if not validate_xhtml(comment.text):
                return JsonResponse({'success': False, 'message': 'Invalid XHTML markup'}, status=400)

            # Handle image processing
            try:
                image_tmp_file = request.FILES.get('image')
                if image_tmp_file:

                    valid_formats = ['image/jpeg', 'image/png', 'image/gif']
                    if image_tmp_file.content_type not in valid_formats:
                        return JsonResponse({'success': False, 'message': 'Invalid image format'},
                                            status=400)

                    img = Image.open(image_tmp_file)
                    width, height = img.size
                    max_size = (320, 240)
                    if width > max_size[0] or height > max_size[1]:
                        img = img.resize(max_size)
                        output_buffer = BytesIO()

                        img.save(output_buffer, format=image_tmp_file.content_type.split('/')[-1].upper())

                        image_tmp_file = InMemoryUploadedFile(output_buffer, 'ImageField', f'{image_tmp_file.name}',
                                                              image_tmp_file.content_type, output_buffer.tell, None)

                    comment.image = image_tmp_file

            except Exception as e:
                print(f"Error saving image: {e}")

            # Handle text file processing
            try:
                file_tmp_file = request.FILES.get('file')
                if file_tmp_file:
                    if not file_tmp_file.name.endswith('.txt'):
                        return JsonResponse(
                            {'success': False, 'message': 'Invalid file format. Only .txt files are allowed.'},
                            status=400)
                    if file_tmp_file.size > 102400:  # 100 KB
                        return JsonResponse({'success': False, 'message': 'File is too large'}, status=400)

                    comment.text_file = file_tmp_file
                    new_name = comment.text_file.name.split('/')[-1]
                    comment.text_file.name = new_name
            except Exception as e:
                print(f"Error saving file: {e}")

            # Save user information before saving the comment
            save_user_info(comment.user_name, comment.email)

            comment.save()
            return JsonResponse({'success': True, 'comment_id': comment.id})
        else:
            errors = form.errors.as_json()
            errors_dict = json.loads(errors)  # Convert JSON string to a dictionary

            # Check if the 'image' key is in the dictionary
            if "image" in errors_dict:
                message = errors_dict["image"][0]["message"]
            else:
                # If the 'image' field has no errors, display a general message or another field
                message = list(errors_dict.values())[0][0][
                    "message"]  # Get the message from the first field with an error

            return JsonResponse({'success': False, 'message': message}, status=400)


class PostListView(View):
    def get(self, request):
        posts = Post.objects.all()
        for post in posts:
            post.formatted_date = post.publish.strftime('%Y/%m/%d')
        return render(request, 'user_comments/index.html', {'posts': posts})


class PostDetailView(View):
    def get(self, request, year, month, day, post_id):
        post = get_object_or_404(Post, id=post_id, status='published', publish__year=year, publish__month=month,
                                 publish__day=day)
        return render(request, 'user_comments/detail.html', {
            'post': post,
            'comment_form': CommentForm(),
            'post_id': post.id,
            'year': post.publish.year,
            'month': post.publish.month,
            'day': post.publish.day
        })


# Функция для валидации XHTML разметки
def validate_xhtml(text):
    try:
        etree.fromstring("<root>" + text + "</root>")
        return True
    except etree.XMLSyntaxError:
        return False


