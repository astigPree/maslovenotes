from django.shortcuts import render, redirect
from frontend.models import *
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from xml.sax.saxutils import escape

from frontend.seo import SITE_NAME, build_seo, clean_summary

# Get the base user model and rely on the first name if want to display the creator component
from django.contrib.auth.models import User

# Create your views here.
def HomePage(request):
    note_data = []
    quote_text = 'Some notes are meant to be anonymous.'
    display_creator = False
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
            
        user = User.objects.first()
        if user:
            if user.first_name == 'open':
                display_creator = True
    except:
        # If there are no notes, redirect to HomePage
        pass
       
    return render(request, 'screens/HomeScreen.html' , {
        'notes': note_data, 'quote': quote_text,
        'write_url': reverse('WritePage'),
        'display_creator': display_creator,
        'seo': build_seo(request),
        
    })


def ViewerPage(request , pk):
    context = {'pk': pk, 'write_url': reverse('WritePage')}
    display_creator = False
    try:
        note = Note.objects.get(pk=int(pk))
        context['title'] = note.title
        context['content'] = note.content
        context['created_at'] = note.created_at.strftime('%B %d, %Y')
        context['image'] = note.image.url if note.image else None
        context['next_url'] = None
        context['prev_url'] = None
        
        # Get the next note order by created_at
        notes = Note.objects.all() 
        next_note = notes.filter(pk__gt=int(pk)).order_by('-created_at').last()
        if next_note:
            context['next_url'] = reverse('ViewerPage' , args=[next_note.pk])
        
        # Get the previous note order by created_at 
        prev_note = notes.filter(pk__lt=int(pk)).order_by('-created_at').first()
        if prev_note:
            context['prev_url'] = reverse('ViewerPage' , args=[prev_note.pk])
        print("Next URL : " ,context['next_url'])
        print("Prev URL : " ,context['prev_url'])
        
        user = User.objects.first()
        if user:
            if user.first_name == 'open':
                display_creator = True
        context['display_creator'] = display_creator
        context['seo'] = build_seo(
            request,
            title=f"{clean_summary(note.title, 55)} | {SITE_NAME}",
            description=(
                f"{clean_summary(note.content, 120)} Read this anonymous "
                "MasLove Notes message from Masbate, Philippines."
            ),
            page_type="article",
            robots="noindex,follow",
        )
    except:
        # If the note does not exist, redirect to HomePage
        return redirect('HomePage')
    
    return render(request, 'screens/ViewerScreen.html' , context)

def WritePage(request):
    display_creator = False
    try:
        user = User.objects.first()
        if user:
            if user.first_name == 'open':
                display_creator = True
    except:
        pass
    return render(request, 'screens/WriteScreen.html' , { 
        'display_creator': display_creator,
        'seo': build_seo(
            request,
            title=f"Write an Anonymous Love Note | {SITE_NAME}",
            description=(
                "Create a heartfelt anonymous note for someone special in "
                "Masbate, Philippines, then share it through a QR code."
            ),
        ),
    })


def RobotsTxt(request):
    sitemap_url = request.build_absolute_uri(reverse('SitemapXml'))
    content = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /api/",
        "",
        f"Sitemap: {sitemap_url}",
    ])
    return HttpResponse(content, content_type="text/plain")


def SitemapXml(request):
    today = timezone.localdate().isoformat()
    urls = [
        {
            "loc": request.build_absolute_uri(reverse('HomePage')),
            "lastmod": today,
            "changefreq": "daily",
            "priority": "1.0",
        },
        {
            "loc": request.build_absolute_uri(reverse('WritePage')),
            "lastmod": today,
            "changefreq": "weekly",
            "priority": "0.8",
        },
    ]

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for item in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{escape(item['loc'])}</loc>")
        xml.append(f"    <lastmod>{item['lastmod']}</lastmod>")
        xml.append(f"    <changefreq>{item['changefreq']}</changefreq>")
        xml.append(f"    <priority>{item['priority']}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")

    return HttpResponse("\n".join(xml), content_type="application/xml")
