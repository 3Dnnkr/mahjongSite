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

from .models import Article
from .forms import ArticleForm
from ms import ms_api


class Index(ListView):
    template_name = "wiki/index.html"
    model = Article
    context_object_name = 'articles'

class Detail(DetailView):
    template_name = "wiki/detail.html"
    model = Article
    context_object_name = 'article'

class CreateArticle(CreateView):
    template_name = "wiki/create_article.html"
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('wiki:index')

async def load_paifu(request):
    username = "3dnnkr@gmail.com"
    password = "ramanujan1729Ac"
    #uuid = "191117-5c090817-4837-4760-8c3e-420af823832a" # ～2019/12/31
    #uuid = "210716-8c69db69-0ce0-4a93-b263-441335581091" # 2020/01/01～2021/07/28
    uuid = "220714-faa69c2d-8321-4748-b027-0b13edfeb704"  # 2021/07/28～
    paifu = await ms_api.load_paifu(username, password, uuid)


    # url encode
    # paifudata = json.dumps(paifu)
    # paifudata = urllib.parse.quote(paifudata)
    # fw = codecs.open('tensoul.txt', 'w', 'utf-8')
    # fw.write(paifudata)
    # fw.close()
    messages.success(request, "牌譜{}を読み込みました！".format(paifu["ref"]))
    return redirect(request.META['HTTP_REFERER'])