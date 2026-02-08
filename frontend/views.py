from django.shortcuts import render
from frontend.models import *
from django.urls import reverse

# Create your views here.
def HomePage(request):
    note_data = []
    quote_text = 'Some notes are meant to be anonymous.'
    try:
        # Get the first 4 notes
        notes = Note.objects.all().order_by('-created_at')[:4]
        for note in notes:
            note_data.append({
                'pk': note.pk,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%B %d, %Y'),
                'image': note.image.url if note.image else 'NONE',
            })
        # Get a random quote
        quotes = Qoute.objects.all()
        quote = quotes.order_by('?').first()
        if quote:
            quote_text = quote.qoute  
    except:
        pass    
       
    return render(request, 'screens/HomeScreen.html' , {
        'notes': note_data, 'quote': quote_text,
        'write_url': reverse('WritePage')
    })


def ViewerPage(request , pk):
    context = {'pk': pk, 'write_url': reverse('WritePage')}
    try:
        note = Note.objects.get(pk=int(pk))
        context['title'] = note.title
        context['content'] = note.content
        context['created_at'] = note.created_at.strftime('%B %d, %Y')
        context['image'] = note.image.url if note.image else None
        context['next_url'] = None
        context['prev_url'] = None
        
        # Get the next note
        notes = Note.objects.all().order_by('-created_at')
        next_note = notes.filter(pk__gt=int(pk)).first()
        if next_note:
            context['next_url'] = reverse('ViewerPage' , args=[next_note.pk])
        
        # Get the previous note
        prev_note = notes.filter(pk__lt=int(pk)).last()
        if prev_note:
            context['prev_url'] = reverse('ViewerPage' , args=[prev_note.pk])

    except:
        pass
    
    return render(request, 'screens/ViewerScreen.html' , context)

def WritePage(request):
    return render(request, 'screens/WriteScreen.html')
