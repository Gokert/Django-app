import requests
from django.http import HttpResponseRedirect, JsonResponse
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
    questions = paginate_objects(Question.objects.new(), request.GET.get('page'), 11)

    return render(request, 'new_questions.html', {
        'questions': questions,
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
    else:
        form = AnswerForm(request.POST)

        if form.is_valid():
            form.save(request.user.profile, question)
        else:
            messages.error(request, 'something went wrong')

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
    return redirect("/")


@require_http_methods(['POST', 'GET'])
def ask_page(request):
    if request.method == 'GET':
        form = QuestionForm()
    else:
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save(request.user.profile)
            return redirect('/')
        else:
            messages.error(request, 'something went wrong')
            return redirect('ask')

    return render(request, 'ask_page.html', {"form": form})


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
        else:
            messages.error(request, 'no valid')

    return render(request, 'login_page.html', {'form': form})


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
            return render(request, 'question_page.html', {'form': setting_form})
        else:
            messages.error(request, 'invalid inputs')

    return render(request, 'signup_page.html', {'form': setting_form})


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

# @login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['POST', 'GET'])
def like(request):
    messages = []

    if request.POST['essence'] == 'question':
        question = Question.objects.get_question(request.POST.get('question_id'))

        if not request.user.is_authenticated:
            messages.append('To like question, you need to log in')
        elif Question.objects.is_question_from_this_user(question.id, request.user.profile.id):
            messages.append("You can't like your own question")
        elif LikeQuestion.objects.filter(question_id=question.id, from_user_id=request.user.profile.id).exists():
            LikeQuestion.objects.filter(
                question_id=question.id, from_user_id=request.user.profile.id).delete()
            question.like_count -= 1
            question.save()
            messages.append("Your like has been removed")
        elif DislikeQuestion.objects.filter(question_id=question.id, from_user_id=request.user.profile.id).exists():
            DislikeQuestion.objects.filter(
                question_id=question.id, from_user_id=request.user.profile.id).delete()
            messages.append("Your dislike has been removed and like is added")
            like = LikeQuestion.objects.create(
                question=question, from_user=request.user.profile)
            question.like_count += 2
            question.save()
            like.save()
        else:
            messages.append("You liked this question")
            like = LikeQuestion.objects.create(
                question=question, from_user=request.user.profile)
            question.like_count += 1
            question.save()
            like.save()

        print(messages)
        return JsonResponse({
            'like_count': question.like_count,
            'messages': messages
        })
    else:
        answer = Answer.objects.get_answer(request.POST['id'])

        if not request.user.is_authenticated:
            messages.append('To like answer, you need to log in')
        elif Answer.objects.is_answer_from_this_user(answer.id, request.user.profile.id):
            messages.append("You can't like your own answer")
        elif LikeAnswer.objects.filter(answer_id=answer.id, from_user_id=request.user.profile.id).exists():
            LikeAnswer.objects.filter(
                answer_id=answer.id, from_user_id=request.user.profile.id).delete()
            answer.like_count -= 1
            answer.save()
            messages.append("Your like has been removed")
        elif DislikeAnswer.objects.filter(answer_id=answer.id, from_user_id=request.user.profile.id).exists():
            DislikeAnswer.objects.filter(
                answer_id=answer.id, from_user_id=request.user.profile.id).delete()
            messages.append("Your dislike has been removed and like is added")
            like = LikeAnswer.objects.create(
                answer=answer, from_user=request.user.profile)
            answer.like_count += 2
            answer.save()
            like.save()
        else:
            messages.append("You liked this answer")
            like = LikeAnswer.objects.create(
                answer=answer, from_user=request.user.profile)
            answer.like_count += 1
            answer.save()
            like.save()

        return JsonResponse({
            'like_count': answer.like_count,
            'messages': messages
        })


@require_http_methods(['POST'])
def dislike(request):
    messages = []

    if request.POST['essence'] == 'question':
        question = Question.objects.get_question(request.POST.get('question_id'))

        if not request.user.is_authenticated:
            messages.append('To dislike question, you need to log in')
        elif Question.objects.is_question_from_this_user(question.id, request.user.profile.id):
            messages.append("You can't dislike your own question")
        elif DislikeQuestion.objects.filter(question_id=question.id, from_user_id=request.user.profile.id).exists():
            DislikeQuestion.objects.filter(
                question_id=question.id, from_user_id=request.user.profile.id).delete()
            question.raiting += 1
            question.save()
            messages.append("Your dislike has been removed")
        elif LikeQuestion.objects.filter(question_id=question.id, from_user_id=request.user.profile.id).exists():
            LikeQuestion.objects.filter(
                question_id=question.id, from_user_id=request.user.profile.id).delete()
            messages.append("Your like has been removed and dislike is added")
            dislike = DislikeQuestion.objects.create(
                question=question, from_user=request.user.profile)
            question.like_count -= 2
            question.save()
            dislike.save()
        else:
            messages.append("You disliked this question")
            dislike = DislikeQuestion.objects.create(
                question=question, from_user=request.user.profile)
            question.like_count -= 1
            question.save()
            dislike.save()
        print(messages)
        return JsonResponse({
            'like_count': question.like_count,
            'messages': messages
        })
    else:
        answer = Answer.objects.get_answer(request.POST['id'])

        if not request.user.is_authenticated:
            messages.append('To dislike answer, you need to log in')
        elif Answer.objects.is_answer_from_this_user(answer.id, request.user.profile.id):
            messages.append("You can't dislike your own answer")
        elif DislikeAnswer.objects.filter(answer_id=answer.id, from_user_id=request.user.profile.id).exists():
            DislikeAnswer.objects.filter(
                answer_id=answer.id, from_user_id=request.user.profile.id).delete()
            answer.like_count += 1
            answer.save()
            messages.append("Your dislike has been removed")
        elif LikeAnswer.objects.filter(answer_id=answer.id, from_user_id=request.user.profile.id).exists():
            LikeAnswer.objects.filter(
                answer_id=answer.id, from_user_id=request.user.profile.id).delete()
            messages.append("Your like has been removed and dislike is added")
            like = DislikeAnswer.objects.create(
                answer=answer, from_user=request.user.profile)
            answer.like_count -= 2
            answer.save()
            like.save()
        else:
            messages.append("You disliked this answer")
            like = DislikeAnswer.objects.create(
                answer=answer, from_user=request.user.profile)
            answer.like_count -= 1
            answer.save()
            like.save()

        return JsonResponse({
            'like_count': answer.like_count,
            'messages': messages
        })


@require_http_methods(['POST', 'GET'])
def correct_answer(request):
    prev_correct_id = None
    answer = models.Answer.objects.get_answer(request.POST['answer_id'])
    messages = []

    if not answer.is_correct:
        question = models.Question.objects.get_question(id=answer.question_id)
        prev_correct = models.Answer.objects.get_correct_answer_for_question(
            question_id=question.id)

        if prev_correct:
            prev_correct_id = prev_correct.id
            prev_correct.is_correct = False
            prev_correct.save()
            messages.append('The correct answer has been changed')
        else:
            messages.append('The answer is marked as correct')

        answer.is_correct = True
    else:
        answer.is_correct = False
        messages.append('The mark of the correct answer has been removed')

    answer.save()

    print(prev_correct_id)

    return JsonResponse({
        'status': 'ok',
        'status': json.dumps(answer.is_correct),
        'prev_correct': json.dumps(prev_correct_id),
        'messages': messages,
    })