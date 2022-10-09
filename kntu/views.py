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

            context = {
                'form'       : form, 
                'seat'       : seat, 
                'paifu_infos': paifu_infos, 
                'score_infos': score_infos,
                'paifu_json' : paifu_json,
            }

            return await async_render(request, 'kntu/paifu_preview.html', context)

    else:
        form = PaifuForm

    return await async_render(request, 'kntu/paifu_preview.html', {'form':form})

