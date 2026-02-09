from django.shortcuts import render
from django.http import HttpResponse, JsonResponse 
from frontend.models import Note, Qoute, ImageKey
# Create your views here.


def clean_text(text):
    # - no special characters, no emojis, no newlines
    new_text = text
    
    new_text = new_text.replace('\n', ' ')
    new_text = new_text.replace('\r', ' ')
    new_text = new_text.replace('\t', ' ')
    new_text = new_text.replace('\v', ' ')
    # remove special characters and remove emojis
    new_text = ''.join([i for i in new_text if ord(i)<128])
    
    new_text = new_text.strip()
    
    
    return new_text


def api_write_note(request):
    if request.method != 'POST':
        return
    
    # TITLE REQUIREMENTS
    # - 1-20 characters
    # - no special characters, no emojis, no newlines
    
    # CONTENT REQUIREMENTS
    # - 1 - 500 characters
    # - no special characters, no emojis, no newlines
    
    # IMAGE KEY REQUIREMENTS
    # - 1-50 characters
    
    # IMAGE FILE REQUIREMENTS
    # - must be a valid image
    
    title_text = request.POST.get('title' , None)
    content_text = request.POST.get('content' , None)
    image_key = request.POST.get('image_key' , None)
    image_file = request.FILES.get('image' , None)
     
    if not isinstance(title_text , str) or not isinstance(content_text , str) :
        return JsonResponse({
            'message' : 'Please provide a correct title and content.'
        } , status=400)
        
    title_text = clean_text(title_text)
    content_text = clean_text(content_text)
    
    if len(title_text) < 1 or len(title_text) > 20:
        return JsonResponse({
            'message' : 'The title must be between 1 and 20 characters.'
        } , status=400)
        
    if len(content_text) < 1 or len(content_text) > 500:
        return JsonResponse({
            'message' : 'The content must be between 1 and 500 characters.'
        } , status=400)
        
    if isinstance(image_key , str):
        image_key = clean_text(image_key)
        
        if len(image_key) < 1 or len(image_key) > 50:
            return JsonResponse({
                'message' : 'Please provide a correct image key.'
            } , status=400)
    
    
    image_key_obj = None
    
    if isinstance(image_file , object) and image_file is not None:
        
        if not isinstance(image_key , str):
            return JsonResponse({
                'message' : 'The image key is required when uploading an image.'
            } , status=400)
        
        
        valid_extensions = ['.jpg', '.jpeg', '.png']
        filename = image_file.name.lower()

        if not any(filename.endswith(ext) for ext in valid_extensions):
            return JsonResponse({
                'message': 'Please provide a valid image file (.jpg, .jpeg, .png).'
            }, status=400)
             
        # Validate file size (max 1 MB)
        max_size = 1 * 1024 * 1024  # 1 MB in bytes
        if image_file.size > max_size:
            return JsonResponse({
                'message': 'Image file too large. Maximum size is 1 MB.'
            }, status=400)
        
        image_key_obj = ImageKey.objects.filter(key=image_key).first()
        
        if not image_key_obj:
            return JsonResponse({
                'message' : 'Please provide a valid image key.'
            } , status=400)
        
        if image_key_obj.is_used:
            return JsonResponse({
                'message' : 'The image key is already in use. Try another image key.'
            } , status=400)
        
        image_key_obj.is_used = True
        image_key_obj.save()
        
    # save the image
    note_id = None
    if image_key_obj:
        note = Note.objects.create(
            title=title_text , 
            content=content_text ,
            image=image_file , 
            image_key=image_key_obj
        )
        note_id = note.pk
    else:
        note = Note.objects.create(
            title=title_text , 
            content=content_text 
        )
        note_id = note.pk
     
    base_url = request.build_absolute_uri('/')
    qr_code_url = base_url + 'notes/' + str(note_id) 
    
    return JsonResponse({
        'message' : 'You can now download the QR code to share your note with your friends.',
        'note_id' : note_id,
        'qr_code_url' : qr_code_url,
        'title' : 'Maslove Notes'
    } , status=201)


