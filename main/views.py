from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Event, Story, NewsItem, AIoTProject
from .forms import ContactForm


def home(request):
    featured_events = Event.objects.filter(is_featured=True)[:3]
    latest_events = Event.objects.all()[:6]
    featured_stories = Story.objects.filter(is_featured=True)[:3]
    latest_news = NewsItem.objects.all()[:3]
    context = {
        'featured_events': featured_events,
        'latest_events': latest_events,
        'featured_stories': featured_stories,
        'latest_news': latest_news,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def event_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    events = Event.objects.all()

    if query:
        events = events.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category:
        events = events.filter(category=category)

    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Event.CATEGORY_CHOICES
    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'categories': categories,
    }
    return render(request, 'main/event_list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    related_events = Event.objects.filter(category=event.category).exclude(pk=pk)[:3]
    context = {
        'event': event,
        'related_events': related_events,
    }
    return render(request, 'main/event_detail.html', context)


def contact(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm()
    else:
        form = ContactForm()
    return render(request, 'main/contact.html', {'form': form, 'success': success})


def story(request):
    stories = Story.objects.all()
    paginator = Paginator(stories, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/story.html', {'page_obj': page_obj})


def story_detail(request, pk):
    story_obj = get_object_or_404(Story, pk=pk)
    return render(request, 'main/story_detail.html', {'story': story_obj})


def usr(request):
    news_items = NewsItem.objects.all()[:6]
    return render(request, 'main/usr.html', {'news_items': news_items})


def aiot(request):
    projects = AIoTProject.objects.all()
    return render(request, 'main/aiot.html', {'projects': projects})


def activities(request):
    activity_events = Event.objects.filter(category='activity')
    paginator = Paginator(activity_events, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/activities.html', {'page_obj': page_obj})


def gallery(request):
    return render(request, 'main/gallery.html')


def ar(request):
    return render(request, 'main/ar.html')
