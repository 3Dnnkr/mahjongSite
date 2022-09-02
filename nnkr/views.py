from django.views.generic import TemplateView, CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import resolve_url,render,get_object_or_404,redirect,HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count

import os
import random
import requests
from PIL import Image
from io import BytesIO

from .models import Question, Comment, CommentLike, Choice, Tag, Tagging, Voting, Bookmark
from .forms import ChoiceForm, QuestionForm, CommentForm, TagForm, ChoiceFormset
from . import twitter
from django.conf import settings


class Top(TemplateView):
    template_name = 'nnkr/top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(Count("questions")).filter(questions__count__gt=0).order_by("-questions__count")[:10]
        hot_comments = list(Comment.objects.order_by('posted_at')[:10])
        random.shuffle(hot_comments)
        hot_comments = hot_comments[:1]
        hot_questions = [c.question for c in hot_comments]
        context['questions'] = hot_questions
        return context

class FAQ(TemplateView):
    template_name = 'nnkr/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class Index(ListView):
    template_name = 'nnkr/index.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        all_questions = Question.objects.all().order_by('-created_datetime')
        paginator = Paginator(all_questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(Count("questions")).filter(questions__count__gt=0).order_by("-questions__count")[:20]
        return context

class Detail(DetailView):
    template_name = 'nnkr/detail.html'
    model = Question
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm
        context['tag_form'] = TagForm
        context['choice_form'] = ChoiceForm
        return context


class CreateQuestion(LoginRequiredMixin, CreateView):
    template_name = 'nnkr/create_question.html'
    model = Question
    form_class = QuestionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset']=ChoiceFormset()
        return context

    def form_valid(self, form):
        question = form.save(commit=False)
        formset = ChoiceFormset(self.request.POST, instance=question)
        if formset.is_valid():
            question.author = self.request.user
            question.save()
            formset.save()

            # Tweet Question Info
            txts = []
            txts.append(question.author.username + "さんの出題")
            txts.append("『"+question.title+"』")
            txts.append(self.request.build_absolute_uri(reverse('nnkr:detail', args=(question.id,))))
            txts.append("#雀魂何切る")
            status = '\n'.join(txts)
            api = twitter.get_api()

            # # if image is ImageField
            # media_ids = api.media_upload(filename=question.image.file.name)
            
            # else if image is CloudinaryField
            img = requests.get(question.image.url).content
            media_ids = api.media_upload(filename='img.png', file=BytesIO(img))

            params = {'status': status, 'media_ids': [media_ids.media_id_string]}
            tweet = api.update_status(**params)

            question.tweet_id = tweet.id
            question.save()
            print(question.image.url)
            
            return redirect('nnkr:detail',pk=question.id)
        return render(self.request, 'nnkr/create_question.html', {'formset':formset})

@require_POST
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    delete_title = request.POST.get("delete_title")
    if request.user != question.author or question.title!=delete_title:
        return redirect(request.META['HTTP_REFERER'])
    
    # delete tweet
    tweet_id = question.tweet_id
    try:
        api = twitter.get_api()
        api.destroy_status(int(tweet_id))
    except:
        print("The status has been successfully deleted.")
    
    # delete question
    question.delete()
    return redirect('nnkr:index')

class CreateChoice(CreateView):
    model = Choice
    form_class = ChoiceForm

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        text = form.cleaned_data.get('text')
        choice = Choice.objects.create(question=question, text=text)
        if self.request.user.is_authenticated:
            return redirect(reverse('nnkr:vote',kwargs={'pk':question_id, 'c_pk':choice.id}))
        else:
            return redirect(reverse('nnkr:secret_vote',kwargs={'pk':question_id, 'c_pk':choice.id}))

class CreateComment(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        text = form.cleaned_data.get('text')
        comment_id = question.comments.count() + 1
        if self.request.user.is_authenticated:
            Comment.objects.create(question=question, text=text, commenter=self.request.user, comment_id=comment_id)
        else:
            Comment.objects.create(question=question, text=text, comment_id=comment_id)
        return redirect(self.request.META['HTTP_REFERER'])

@require_POST
def create_comment_like(request, pk, c_pk):
    comment = get_object_or_404(Comment, pk=c_pk)
    user = request.user
    if user.is_anonymous:
        return redirect(request.META['HTTP_REFERER'])
     # check if commnet.likers contain user.
    _liker = comment.likers.filter(pk=user.pk).first()
    if _liker==None and user!=comment.commenter:
        CommentLike.objects.create(liker=user, comment=comment)
    return redirect(request.META['HTTP_REFERER'])


class TagQuestion(ListView):
    template_name = 'nnkr/tag_question.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        all_questions = Question.objects.all().filter(tags__in=[tag]).order_by('-created_datetime')
        paginator = Paginator(all_questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        context['tag'] = tag
        return context

class CreateTag(CreateView):
    model = Tag
    form_class = TagForm

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        name = form.cleaned_data.get('name')
        tag = Tag.objects.filter(name=name).first()
        if tag==None:
            tag = form.save()
        q_tag = question.tags.filter(name=name).first()
        if q_tag==None:
            Tagging.objects.create(question=question, tag=tag, tagging_datetime=timezone.datetime.now())
        return redirect(self.request.META['HTTP_REFERER'])

@require_POST
def delete_tag(request, pk, t_pk):
    question = get_object_or_404(Question, pk=pk)
    tag = get_object_or_404(Tag, pk=t_pk)
    question.tags.remove(tag)
    return redirect(request.META['HTTP_REFERER'])

@login_required
@require_POST
def vote(request, pk, c_pk):
    choice = get_object_or_404(Choice, pk=c_pk)
    if not request.user in choice.question.voters.all():
        Voting.objects.create(choice=choice, voter=request.user, voting_datetime=timezone.datetime.now())
    # return redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id})+"#image")
    return redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id}))

@require_POST
def secret_vote(request, pk, c_pk):
    choice = get_object_or_404(Choice, pk=c_pk)
    response = redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id}))
    key = 'voted_{}'.format(choice.question.id)
    voted = request.COOKIES.get(key,False)
    if not voted:
        response.set_cookie(key,True)
        response.set_cookie('voted_choice_{}'.format(choice.id),True)
        choice.secret_votes+=1
        choice.save()
    return response

@require_POST
def create_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user
    if user.is_anonymous:
        redirect(request.META['HTTP_REFERER'])
    b_question = user.bookmarks.filter(id=question.id).first()
    if b_question==None:
        Bookmark.objects.create(user=user,question=question,bookmark_datetime=timezone.datetime.now())
    return redirect(request.META['HTTP_REFERER'])

@require_POST
def delete_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user.is_anonymous:
        redirect(request.META['HTTP_REFERER'])
    request.user.bookmarks.remove(question)
    return redirect(request.META['HTTP_REFERER'])


