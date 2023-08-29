from django import forms
from app.models import Profile, Question, Answer, Tag
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class RegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password', 'avatar']

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password'])
        email = self.cleaned_data['email']
        avatar = self.cleaned_data['avatar']

        user.username = username
        user.email = email

        user.save()
        self.cleaned_data.pop('password_confirm')
        profile = Profile.objects.create(user=user)
        profile.avatar = avatar

        if commit:
            profile.save()

        return profile

    def clean(self):
        for field in ['email', 'username', 'password', 'password_confirm']:
            if field not in self.cleaned_data.keys():
                return self.cleaned_data

        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error('password_confirm', "Passwords don't match")

        email_count = User.objects.filter(
            email=self.cleaned_data['email']).count()

        if email_count:
            self.add_error(
                'email', 'A user with such an email has already been registered')

        if len(self.cleaned_data['username']) < 4:
            self.add_error(
                'username', 'The minimum length of the username is 4')

        username_count = User.objects.filter(
            username=self.cleaned_data['username']).count()

        if username_count:
            self.add_error(
                'username', 'username count > 0')

        return self.cleaned_data

class SettingsForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField()
    avatar = forms.ImageField(required=False)


    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'avatar']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curr_user = user
        self.fields['email'].widget.attrs['value'] = user.email
        self.fields['username'].widget.attrs['value'] = user.username
        self.fields['avatar'].widget.attrs['value'] = user.profile.avatar


    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        avatar = self.cleaned_data['avatar']

        if username != self.curr_user.username:
            self.curr_user.username = username
        if password != '':
            self.curr_user.set_password(password)
        if email != self.curr_user.email:
            self.curr_user.email = email

        self.curr_user.profile.avatar = avatar

        self.curr_user.save()
        return self.curr_user.profile

    def clean(self):
        object = User.objects.filter(email=self.cleaned_data['email'])
        email_count = object.count()

        if email_count:
            if object[0].email != self.cleaned_data['email']:
                self.add_error(
                    'email', 'A user with such an email has already been registered')

        if len(self.cleaned_data['username']) < 4:
            self.add_error(
                'username', 'The minimum length of the username is 4')

        object = User.objects.filter(username=self.cleaned_data['username'])

        username_count = object.count()

        if username_count:
            if object[0].username != self.cleaned_data['username']:
                self.add_error(
                    'username', 'username count > 0')



        return self.cleaned_data


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'mb-3'}), help_text='There may be several tags, list them separated by a space')

    class Meta:
        model = Question
        fields = ['title', 'text']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'mb-3'}),
            'text': forms.Textarea(attrs={'class': 'mb-3'}),
        }

        help_texts = {
            'title': (
                'Enter a title that briefly describes your problem. The length of the title should be from 10 to 80 characters.'),
            'text': ('Describe your problem in the most detail'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'How to create a question?'
        self.fields['title'].required = False
        self.fields['text'].widget.attrs['placeholder'] = ''
        self.fields['text'].required = False
        self.fields['tags'].widget.attrs['placeholder'] = 'Python PostgreSQL'
        self.fields['tags'].required = False

    def clean(self):
        if 'title' not in self.cleaned_data.keys() or len(self.cleaned_data['title']) < 3:
            self.add_error('title', 'The minimum length of the title is 3')

        if 'text' not in self.cleaned_data.keys() or len(self.cleaned_data['text']) < 5:
            self.add_error(
                'text', 'The minimum length of the text of the question text is 5')

        title = Question.objects.filter(
            title=self.cleaned_data['title']).count()

        if title:
            self.add_error(
                'title', 'A user with such an title has already been registered')


    def save(self, profile):
        question = super().save(commit=False)
        question.user = profile
        question.save()
        tags = self.cleaned_data['tags'].split()

        for tag in tags:
            new = Tag.objects.get_or_create(tag_name=tag)
            question.tags.add(new[0].id)
        question.save()

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

        widgets = {
            'text': forms.Textarea(attrs={'class': 'mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = 'Write your answer'
        self.fields['text'].required = False

    def clean(self):
        if 'text' not in self.cleaned_data.keys() or len(self.cleaned_data['text']) < 1:
            self.add_error(
                'text', 'The minimum length of the text of the question text is 1')

    def save(self, profile, question):
        answer = super().save(commit=False)
        answer.user = profile
        answer.question = question

        answer.save()
        question.answer_count = Answer.objects.filter(question=question).count()
        question.save()

        return answer