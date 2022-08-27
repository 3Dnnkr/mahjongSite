from django.views.generic import CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import resolve_url,render,get_object_or_404,redirect,HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator

from .models import Question, Comment, Choice, Tag, Tagging, Bookmark
from .forms import QuestionForm, CommentForm, TagForm, ChoiceFormset
import os

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


class Detail(DetailView):
    template_name = 'nnkr/detail.html'
    model = Question
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm
        context['tag_form'] = TagForm
        context['secret_key'] = os.environ.get('SECRET_KEY',"no_key")
        context['time'] = os.environ.get('TIME',0) 
        return context

class CreateComment(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        text = form.cleaned_data.get('text')
        comment_id = question.comment_set.count() + 1
        Comment.objects.create(target=question, text=text, commenter=self.request.user, comment_id=comment_id)
        return redirect('nnkr:detail',pk=question_id)

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
        return redirect('nnkr:detail',pk=question_id)

def delete_tag(request, pk, t_pk):
    question = get_object_or_404(Question, pk=pk)
    tag = get_object_or_404(Tag, pk=t_pk)
    question.tags.remove(tag)
    return redirect(reverse('nnkr:detail',kwargs={'pk':question.id}))

def vote(request, pk):
    choice = get_object_or_404(Choice, pk=pk)
    response = redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id}))
    # you can set anchor.
    # response = redirect(reverse('nnkr:detail',kwargs={'pk':choice.question.id})+"#image")
    key = 'voted_{}'.format(choice.question.id)
    voted = request.COOKIES.get(key,False)
    if not voted:
        response.set_cookie(key,True)
        choice.votes+=1
        choice.save()
    return response

def create_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user
    if user.is_anonymous:
        return redirect(reverse('nnkr:detail',kwargs={'pk':question.id}))
    b_question = user.bookmarks.filter(id=question.id).first()
    if b_question==None:
        Bookmark.objects.create(user=user,question=question,bookmark_datetime=timezone.datetime.now())
    return redirect(request.META['HTTP_REFERER'])

def delete_bookmark(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user.is_anonymous:
        return redirect(reverse('nnkr:detail',kwargs={'pk':question.id}))
    request.user.bookmarks.remove(question)
    return redirect(request.META['HTTP_REFERER'])

@login_required
def create_question(request):
    """ use QuestionForm and ChoiceFormset """
    form = QuestionForm(request.POST or None, files=request.FILES)
    context = {'form':form}
    if request.method=='POST' and form.is_valid():
        question = form.save(commit=False)
        formset = ChoiceFormset(request.POST, instance=question)
        if formset.is_valid():
            question.save()
            formset.save()
            return redirect('nnkr:detail',pk=question.id)
        else:
            context['formset']=formset
    else:
        context['form']=QuestionForm()
        context['formset']=ChoiceFormset()
    return render(request, 'nnkr/create_question.html', context)

class CreateQuestion(FormView):
    template_name = 'nnkr/create_question.html'
    model = Question
    form_class = QuestionForm
    success_url = reverse_lazy('nnkr:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset']=ChoiceFormset()
        return context

    def form_valid(self, form):
        """ When Form is valid, create question. """
        response = super().form_valid(form)
        question = form.save(commit=False)
        formset = ChoiceFormset(self.request.POST, instance=question)
        if formset.is_valid():
            question.author = self.request.user
            question.save()
            formset.save()
        # title = form.cleaned_data.get('title')
        # image = form.cleaned_data.get('image')
        # description = form.cleaned_data.get('description')
        # Question.objects.create(title=title, image=image, description=description, author=self.request.user)
        return response

