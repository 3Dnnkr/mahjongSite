from django.views.generic import TemplateView, CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import resolve_url,render,get_object_or_404,redirect,HttpResponseRedirect,HttpResponse

from asgiref.sync import sync_to_async
import json, urllib

from .forms import PaifuForm
from ms import ms_api


async def paifu_preview(request):
    username = "3dnnkr@gmail.com"
    password = "ramanujan1729Ac"
    async_render = sync_to_async(render, thread_sensitive=False)

    if request.method == "POST":
        form = PaifuForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url')
            seat = form.cleaned_data.get('seat')
            paifudata = await ms_api.load_paifu(username, password, url)
            paifudata_json = json.dumps(paifudata)
            if paifudata.get("error"):
                messages.warning(request, "牌譜の読み込みに失敗しました...")
                return await async_render(request, 'kntu/paifu_preview.html', {'form':form})
            
            # url encode
            paifus = []
            names = []
            ju_dict = {  0:"東一局",  1:"東二局",  2:"東三局",  3:"東四局",
                         4:"南一局",  5:"南二局",  6:"南三局",  7:"南四局",
                         8:"西一局",  9:"西二局", 10:"西三局", 11:"西四局",
                        12:"北一局", 13:"北二局", 14:"北三局", 15:"北四局",}
            for log in paifudata["log"]:
                paifu = {}
                paifu["title"] = paifudata["title"]
                paifu["name"]  = paifudata["name"]
                paifu["rule"]  = paifudata["rule"]
                paifu["log"]   = [log]
                paifu = json.dumps(paifu)
                paifu = urllib.parse.quote(paifu)
                paifus.append(paifu)

                ju    = log[0][0]
                chang = log[0][1]
                names.append(ju_dict.get(ju)+" "+str(chang)+"本場")

            messages.success(request, "牌譜{}を読み込みました！".format(paifudata["ref"]))
            return await async_render(request, 'kntu/paifu_preview.html', {'form':form,'paifus':paifus, 'seat':seat ,'names':names, 'paifudata':paifudata_json})

    else:
        form = PaifuForm

    return await async_render(request, 'kntu/paifu_preview.html', {'form':form})

