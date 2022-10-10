from django.views.generic import TemplateView, CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import resolve_url,render,get_object_or_404,redirect,HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator

from asgiref.sync import sync_to_async
import json, urllib

from kntu.models import Examination, Kyoku, Comment, CommentLike

from .forms import PaifuForm, ExamForm, CommentForm, UpdateExamForm
from ms import ms_api


async def paifu_preview(request):
    username = "3dnnkr@gmail.com"
    password = "ramanujan1729Ac"
    async_render = sync_to_async(render, thread_sensitive=False)

    if request.method == "POST":
        form = PaifuForm(request.POST)
        if form.is_valid():
            
            # get paifudata
            url = form.cleaned_data.get('url')
            seat = form.cleaned_data.get('seat')
            paifudata = await ms_api.load_paifu(username, password, url)
            
            # error message
            if paifudata.get("error"):
                messages.warning(request, "牌譜の読み込みに失敗しました...")
                return await async_render(request, 'kntu/paifu_preview.html', {'form':form})
            else:
                messages.success(request, "牌譜{}を読み込みました！".format(paifudata["ref"]))

            # process paifudata
            paifu_infos = ms_api.get_paifuinfos_from(paifudata)
            score_infos = json.dumps(ms_api.get_scoreinfos_from(paifudata))
            paifu_json  = json.dumps(paifudata)

            # exam form
            exam_form = ExamForm(initial={'paifudata': paifudata})

            context = {
                'form'       : form, 
                'seat'       : seat, 
                'paifu_infos': paifu_infos, 
                'score_infos': score_infos,
                'paifu_json' : paifu_json,
                'exam_form'  : exam_form,
            }

            return await async_render(request, 'kntu/paifu_preview.html', context)

    else:
        form = PaifuForm

    return await async_render(request, 'kntu/paifu_preview.html', {'form':form})

class CreateExam(LoginRequiredMixin, CreateView):
    model = Examination
    form_class = ExamForm

    def form_valid(self, form):
        exam = form.save(commit=False)
        exam.author = self.request.user
        exam.save()

        # create kyokus
        paifu_infos = exam.paifu_infos
        for paifu,name in paifu_infos:
            Kyoku.objects.create(exam=exam, name=name, paifu=paifu)
        
        return redirect('kntu:detail', pk=exam.pk)

class UpdateExam(UpdateView):
    model = Examination
    fields = ['release',]

    def form_valid(self,form):
        redirect = super().form_valid(form)
        return redirect
 
    def get_success_url(self):
        exam = get_object_or_404(Examination, pk=self.kwargs['pk'])
        return resolve_url('kntu:detail', pk=exam.pk)

def delete_exam(request, pk):
    exam = get_object_or_404(Examination, pk=pk)
    delete_title = request.POST.get("delete_title")
    if request.user != exam.author or exam.title!=delete_title:
        return redirect(request.META['HTTP_REFERER'])
    
    # delete exam
    exam.delete()
    return redirect('kntu:index')

class Index(ListView):
    template_name = 'kntu/exam_index.html'
    model = Examination
    context_object_name = 'exams'

    def get_queryset(self):
        exams = Examination.objects.all().order_by('-created_datetime')
        exams = exams.filter(release=0)
        paginator = Paginator(exams, 6)
        p = self.request.GET.get('page')
        exams = paginator.get_page(p)
        return exams

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class Detail(DetailView):
    template_name = 'kntu/exam_detail.html'
    model = Examination
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm
        context['exam_form'] = UpdateExamForm(initial={'release':context['exam'].release})
        return context

class CreateComment(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        kyoku_id = self.kwargs.get('pk')
        kyoku = get_object_or_404(Kyoku, pk=kyoku_id)
        text = form.cleaned_data.get('text')
        comment_id = kyoku.comments.count() + 1
        if self.request.user.is_authenticated:
            Comment.objects.create(kyoku=kyoku, text=text, commenter=self.request.user, comment_id=comment_id)
        else:
            Comment.objects.create(kyoku=kyoku, text=text, comment_id=comment_id)
        return redirect(self.request.META['HTTP_REFERER'])

class UpdateComment(UpdateView):
    template_name = 'kntu/update_comment.html'
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
        return resolve_url('kntu:detail', pk=comment.kyoku.exam.pk)

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
