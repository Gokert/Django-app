from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib import messages

from app.forms import *
from app.models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

questions_per_page = 11
answer_count = 10

def paginate_objects(objects, page, objects_per_page=20):
    return Paginator(objects, objects_per_page).get_page(page)

@require_http_methods(['GET'])
def new_questions(request):
    return render(request, 'new_questions.html', {
        'questions': paginate_objects(Question.objects.new(),
                                      request.GET.get('page'), 11),
        'popular_tags': Tag.objects.all()[:20]

    })

@require_http_methods(['GET'])
def hot_questions(request):
    q = paginate_objects(Question.objects.hot(),
                         request.GET.get('page'), 11)
    return render(request, 'hot_questions.html', {
        'questions': q,
        'popular_tags': Tag.objects.all()[:20]
    })


def tag_questions(request, t):
    q = paginate_objects(Question.objects.by_tag(t),
                         request.GET.get('page'), 11)
    return render(request, 'tag_page.html', {
        'tag_title': t,
        'questions': q,
        'popular_tags': Tag.objects.all()[:20]
    })

@require_http_methods(['GET', 'POST'])
def question_page(request, qid):
    question = Question.objects.get(pk=qid)
    answers = paginate_objects(Answer.objects.by_question(qid),
                               request.GET.get('page'), 5)

    if request.method == 'GET':
        form = AnswerForm()
        print(request.method)
    else:
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(request.user, question)
        else:
            messages.error(request, 'something went wrong')
        print("POST")

    return render(request, 'question_page.html', {
        'question': question,
        'questions': answers,
        'popular_tags': Tag.objects.all()[:20],
        'form': form
    })

@require_http_methods(['POST', 'GET'])
@login_required
def logout(request):
    auth.logout(request)
    prev_page = request.META.get("HTTP_REFERER")
    if prev_page is not None:
        return redirect(prev_page)
    return redirect("/")  # TODO нужны правильный редиректы (на предыдущую страницу)

@require_http_methods(['POST', 'GET'])
def ask_page(request):
    form = None
    if request.method == 'GET':
        form = QuestionForm()
    else:
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(request.user)
            return redirect('/')
        else:
            messages.error(request, 'something went wrong')
            return redirect('ask')


    ctx = {"form": form}
    return render(request, 'ask_page.html', ctx)


@require_http_methods(['POST', 'GET'])
def login_page(request):
    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():

            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect("/")
            else:
                messages.error(request, 'invalid user or password')
                #return redirect(request.POST.get('next', '/'))
        else:
            print("NO VALID")
    ctx = {'form': form}
    return render(request, 'login_page.html', ctx)


@require_http_methods(['POST', 'GET'])
def signup_page(request):
    if request.method == 'GET':
        setting_form = RegistrationForm()
    else:
        setting_form = RegistrationForm(request.POST)
        avatar_form = AvatarForm(request.FILES)
        if setting_form.is_valid() and avatar_form.is_valid():
            profile = setting_form.save()
            avatar_form.save(profile)
            auth.login(request, profile.user)
            ctx = {'form': setting_form}
            return render(request, 'question_page.html', ctx)
        else:
            messages.error(request, 'invalid inputs')

    ctx = {'form': setting_form}
    return render(request, 'signup_page.html', ctx)


@require_http_methods(['POST', 'GET'])
def settings_page(request):
    if request.method == 'GET':
        setting_form = SettingsForm(request.user)
        avatar_form = AvatarForm()
    else:
        setting_form = SettingsForm(request.user, request.POST)
        avatar_form = AvatarForm(request.FILES)
        if setting_form.is_valid() and avatar_form.is_valid():
            profile = setting_form.save()
            avatar_form.save(profile)

            auth.login(request, profile.user)
        else:
            messages.error(request, 'invalid inputs')

    content = {
        "setting_form": setting_form,
        "avatar_form": avatar_form
    }

    return render(request, 'settings_page.html', content)
