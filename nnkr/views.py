from django.views.generic import TemplateView, CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import resolve_url,render,get_object_or_404,redirect,HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count

import random
import requests
from PIL import Image
from io import BytesIO

from .models import Question, Comment, CommentLike, Choice, Tag, Tagging, Voting, Bookmark, Liker, Disliker, Lobbychat, LobbychatLike
from .forms import ChoiceForm, QuestionForm, CommentForm, TagForm, ChoiceFormset, LobbychatForm
from . import twitter


class Top(TemplateView):
    template_name = 'nnkr/top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hot_comments = list(Comment.objects.order_by('posted_at')[:10])
        random.shuffle(hot_comments)
        hot_comments = hot_comments[:1]
        hot_questions = [c.question for c in hot_comments]
        context['questions'] = hot_questions

        lobby_chats = Lobbychat.objects.order_by('-posted_at')
        paginator = Paginator(lobby_chats, 8)
        p = self.request.GET.get('page')
        lobby_chats = paginator.get_page(p)
        context['chats'] = lobby_chats

        context['chat_form'] = LobbychatForm
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
        sort = self.request.GET.get('sort')
        questions = Question.objects.all()
        
        if sort=="r":
            questions = [q for q in questions]
            questions.sort(key=lambda q: q.rating, reverse=True)
        elif sort=="v":
            questions = [q for q in questions]
            questions.sort(key=lambda q: q.votes, reverse=True)
        elif sort=="c":
            questions = [q for q in questions if q.comments.all().count()==0]
            questions.sort(key=lambda q: q.created_datetime, reverse=True)
        elif sort=="o":
            questions = questions.order_by('created_datetime')
        else:
            questions = questions.order_by('-created_datetime')

        paginator = Paginator(questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(Count("questions")).filter(questions__count__gt=0).order_by("-questions__count")[:20]
        sort = self.request.GET.get('sort')
        context[str(sort)]=True
        return context

class TagIndex(ListView):
    template_name = 'nnkr/tag_index.html'
    model = Tag
    context_object_name = 'tags'

    def get_queryset(self):
        tags = Tag.objects.all()
        paginator = Paginator(tags, 50)
        p = self.request.GET.get('page')
        tags = paginator.get_page(p)
        return tags


class TagQuestion(ListView):
    template_name = 'nnkr/tag_question.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        questions = Question.objects.all().filter(tags__in=[tag])
        
        if sort=="r":
            questions = [q for q in questions]
            questions.sort(key=lambda q: q.rating, reverse=True)
        elif sort=="v":
            questions = [q for q in questions]
            questions.sort(key=lambda q: q.votes, reverse=True)
        elif sort=="c":
            questions = [q for q in questions if q.comments.all().count()==0]
            questions.sort(key=lambda q: q.created_datetime, reverse=True)
        elif sort=="o":
            questions = questions.order_by('created_datetime')
        else:
            questions = questions.order_by('-created_datetime')

        paginator = Paginator(questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        context['tag'] = tag
        context['tags'] = Tag.objects.annotate(Count("questions")).filter(questions__count__gt=0).order_by("-questions__count")[:20]
        sort = self.request.GET.get('sort')
        context[str(sort)]=True
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
        if question.no_vote:
            question.author = self.request.user
            question.save()
            self.post_tweet(question)
            return redirect('nnkr:detail',pk=question.id)
        else:
            formset = ChoiceFormset(self.request.POST, instance=question)
            if formset.is_valid():
                question.author = self.request.user
                question.save()
                formset.save()
                self.post_tweet(question)
                return redirect('nnkr:detail',pk=question.id)
        return render(self.request, 'nnkr/create_question.html', {'formset':formset})

    def post_tweet(self, question):
        api = twitter.get_api()
        txts = []
        txts.append(question.author.username + "さんの出題")
        txts.append("『"+question.title+"』")
        txts.append(self.request.build_absolute_uri(reverse('nnkr:detail', args=(question.id,))))
        txts.append("#雀魂何切る")
        status = '\n'.join(txts)

        # # if image is ImageField
        # media_ids = api.media_upload(filename=question.image.file.name)
        
        # else if image is CloudinaryField
        img = requests.get(question.image.url).content
        media_ids = api.media_upload(filename='img.png', file=BytesIO(img))

        params = {'status': status, 'media_ids': [media_ids.media_id_string]}
        tweet = api.update_status(**params)

        question.tweet_id = tweet.id
        question.save()

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

class UpdateComment(UpdateView):
    template_name = 'nnkr/update_comment.html'
    model = Comment
    fields = ['text',]

    def form_valid(self,form):
        redirect = super().form_valid(form)        
        pk = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_updated = True
        comment.save()
        return redirect
 
    def get_success_url(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return resolve_url('nnkr:detail',pk=comment.question.pk)
 
def create_comment_like(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    user = request.user
    if user.is_anonymous:
        messages.warning(request, "ログインが必要です")
        return redirect(request.META['HTTP_REFERER'])
     # check if commnet.likers contain user.
    _liker = comment.likers.filter(pk=user.pk).first()
    if _liker==None and user!=comment.commenter:
        CommentLike.objects.create(liker=user, comment=comment)
        messages.success(request, "コメントを評価しました！")
        
    return redirect(request.META['HTTP_REFERER'])


class CreateTag(FormView):
    form_class = TagForm

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        name = form.cleaned_data.get('name')
        # Create tag if not tag exist.
        tag = Tag.objects.filter(name=name).first()
        if tag==None:
            tag = Tag.objects.create(name=name)
        # Connect tag if not question has it.
        q_tag = question.tags.filter(name=name).first()
        if q_tag==None:
            Tagging.objects.create(question=question, tag=tag, tagging_datetime=timezone.datetime.now())
        return redirect(self.request.META['HTTP_REFERER'])
    
def delete_tag(request, pk, t_pk):
    question = get_object_or_404(Question, pk=pk)
    tag = get_object_or_404(Tag, pk=t_pk)
    question.tags.remove(tag)
    return redirect(request.META['HTTP_REFERER'])


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

def vote(request, pk, c_pk):
    choice = get_object_or_404(Choice, pk=c_pk)
    if not request.user in choice.question.voters.all():
        Voting.objects.create(choice=choice, voter=request.user, voting_datetime=timezone.datetime.now())
        messages.success(request, "投票しました！")
    # return redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id})+"#image")
    return redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id}))

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
        messages.success(request, "投票しました！")
    return response


def create_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user
    if user.is_anonymous:
        messages.warning(request, "ログインが必要です")
        redirect(request.META['HTTP_REFERER'])
    b_question = user.bookmarks.filter(id=question.id).first()
    if b_question==None:
        Bookmark.objects.create(user=user,question=question,bookmark_datetime=timezone.datetime.now())
        messages.success(request, "ブックマークしました！")
    return redirect(request.META['HTTP_REFERER'])

def delete_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user.is_anonymous:
        messages.warning(request, "ログインが必要です")
        redirect(request.META['HTTP_REFERER'])
    else:
        request.user.bookmarks.remove(question)
        messages.success(request, "ブックマークを解除しました")
    return redirect(request.META['HTTP_REFERER'])


class CreateLiker(CreateView):
    model = Liker
    fields = []

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)

        if self.request.user.is_authenticated:
            Liker.objects.create(question=question, user=self.request.user)
            messages.success(self.request, "問題を評価しました！")
        else:
            messages.warning(self.request, "ログインが必要です")
        return redirect(self.request.META['HTTP_REFERER'])

class CreateDisliker(CreateView):
    model = Disliker
    fields = []

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)

        if self.request.user.is_authenticated:
            Disliker.objects.create(question=question, user=self.request.user)
            messages.success(self.request, "問題の評価を下げました")
        else:
            messages.warning(self.request, "ログインが必要です")
        return redirect(self.request.META['HTTP_REFERER'])

def delete_liker(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user.is_authenticated:
        request.user.likes.remove(question)
        messages.success(request, "イイねを解除しました")
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.warning(request, "ログインが必要です")
    return redirect(request.META['HTTP_REFERER'])


class CreateLobbychat(CreateView):
    model = Lobbychat
    form_class = LobbychatForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        if self.request.user.is_authenticated:
            Lobbychat.objects.create(text=text, user=self.request.user)
        else:
            Lobbychat.objects.create(text=text)
        return redirect(self.request.META['HTTP_REFERER'])

def create_lobbychat_like(request, pk):
    lobbychat = get_object_or_404(Lobbychat, pk=pk)
    user = request.user
    if user.is_anonymous:
        messages.warning(request, "ログインが必要です")
        return redirect(request.META['HTTP_REFERER'])
     # check if commnet.likers contain user.
    _liker = lobbychat.likers.filter(pk=user.pk).first()
    if _liker==None and user!=lobbychat.user:
        LobbychatLike.objects.create(liker=user, lobbychat=lobbychat)
        messages.success(request, "イイねしました！")
        
    return redirect(request.META['HTTP_REFERER'])