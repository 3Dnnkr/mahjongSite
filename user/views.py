from django.views.generic import TemplateView,CreateView, ListView, FormView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model, login, authenticate
from django.urls import reverse_lazy
from django.shortcuts import resolve_url, get_object_or_404
from django.core.paginator import Paginator

from .forms import LoginForm, UserCreateForm, UserUpdateForm
from nnkr.models import Question

class UserIndex(ListView):
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
        return response

class UserUpdate(UpdateView):
    template_name = 'user/user_detail.html'
    model = get_user_model()
    context_object_name = 'target_user'
    form_class = UserUpdateForm

    def get_success_url(self):
        """
        Redirect to dynamic URL.
        Called by FormMixin.form_valid()
        """
        return resolve_url('user:detail',pk=self.kwargs['pk'])

class UserQuestionIndex(ListView):
    template_name = 'user/user_question.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(get_user_model(), pk=user_id)
        all_questions = Question.objects.all().filter(author=target_user).order_by('-updated_datetime')
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

class OnlyYouMixin(UserPassesTestMixin):
    """Restrict accessible user"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser