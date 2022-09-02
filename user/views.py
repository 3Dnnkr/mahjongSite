from django.views.generic import TemplateView,CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, authenticate, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import resolve_url, get_object_or_404, render, redirect
from django.core.paginator import Paginator

from social_django.models import UserSocialAuth

from .forms import LoginForm, UserCreateForm, UserUpdateForm
from nnkr.models import Question
from nnkr import twitter
from .models import Icon

class Index(ListView):
    template_name = 'user/user_index.html'
    model = get_user_model()
    context_object_name = 'users'

    def get_queryset(self):
        all_users = get_user_model().objects.all().order_by('-id')
        paginator = Paginator(all_users, 10)
        p = self.request.GET.get('page')
        users = paginator.get_page(p)
        return users

class Login(LoginView):
    form_class = LoginForm
    template_name = 'user/login.html'

class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'user/login.html'

class UserCreate(CreateView):
    model = get_user_model()
    template_name = 'user/user_create.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('nnkr:index')
    
    def form_valid(self, form):
        """
        When Form is valid, authenticate the user.
        form_valid is Defiend by FormMixin.form_valid()
        and Called by ProcessFormView.post()
        """
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_pw = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_pw)
        login(self.request, user)

        # set default icon
        icon, _ = Icon.objects.get_or_create(name='icon_guest.png')
        user.icon = icon
        user.save()
        
        return response


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'user/password.html', {'form': form})

class UserDetail(UpdateView):
    template_name = 'user/user_detail.html'
    model = get_user_model()
    context_object_name = 'target_user'
    form_class = UserUpdateForm

    def get_success_url(self):
        return resolve_url('user:detail',pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = get_object_or_404(get_user_model(), pk=self.kwargs.get('pk'))
        context['target_user'] = target_user
        context['comments_likers_num'] = sum([c.likers.all().count() for c in target_user.comments.all()])

        # Icon cobtext
        if self.request.user == target_user:
            context['icons'] = Icon.objects.order_by('order')

        # Twitter context
        try:
            twitter_login = target_user.social_auth.get(provider='twitter')
            user_id = twitter_login.extra_data['access_token']['user_id']
            api = twitter.get_api()
            context['profile_image_url'] = api.get_user(user_id=user_id).profile_image_url_https
        except UserSocialAuth.DoesNotExist:
            twitter_login = None
        context['twitter_login'] = twitter_login
        
        can_disconnect = (target_user.social_auth.count() > 1 or target_user.has_usable_password())
        context['can_disconnect'] = can_disconnect

        return context

class UserQuestion(ListView):
    template_name = 'user/user_question.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        all_questions = Question.objects.all().filter(author=target_user).order_by('-created_datetime')
        paginator = Paginator(all_questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        context['target_user'] = target_user
        return context

class UserBookmark(ListView):
    template_name = 'user/user_bookmark.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        all_questions = target_user.bookmarks.all()
        paginator = Paginator(all_questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        context['target_user'] = target_user
        return context

class UserHistory(ListView):
    template_name = 'user/user_history.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)

        custom_list = [q.id for q in Question.objects.all() if target_user in q.voters.all()]
        all_questions = Question.objects.filter(id__in=custom_list)

        paginator = Paginator(all_questions, 6)
        p = self.request.GET.get('page')
        questions = paginator.get_page(p)
        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        context['target_user'] = target_user
        return context

@login_required
def update_icon(request, pk, i_pk):
    user = get_object_or_404(get_user_model(),pk=pk)
    icon = get_object_or_404(Icon, pk=i_pk)
    user.icon = icon
    user.save()
    return redirect(request.META['HTTP_REFERER'])