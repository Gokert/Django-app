from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count


class ProfileManager(models.Manager):
    def get_top_users(self, count=5):
        return self.annotate(answer_count=Count('answer')).order_by('-answer_count')[:count]

    def get_profile_by_id(self, id):
        try:
            return self.annotate(question_count=Count('question', distinct=True), answer_count=Count('answer', distinct=True)).get(id=id)
        except Profile.DoesNotExist:
            return None

    def get_prof_by_user_id(self, id):
        try:
            return self.get(user_id=id)
        except Profile.DoesNotExist:
            return None


class Profile(models.Model):
    def __str__(self):
        return self.user

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='', default=None)
    objects = ProfileManager()

    def user_exists(username):
        user = User.objects.filter(username=username)
        if user:
            return user
        else:
            return None


class QuestionLikeManager(models.Manager):
    def q_downvotes(self, q_id):
        return self.filter(question_id=q_id, is_upvote=True)

    def q_upvotes(self, q_id):
        return self.filter(question_id=q_id, is_upvote=True)

    def by_question(self, q_id):
        return self.filter(question_id=q_id)


class QuestionLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    is_upvote = models.BooleanField(verbose_name="Положительный")

    objects = QuestionLikeManager()

    def __str__(self):
        return self.question.title

    class Meta:
        verbose_name = "Лайк на вопросе"
        verbose_name_plural = "Лайки на вопросах"


class AnswerLikeManager(models.Manager):
    def ans_upvotes(self, a_id):
        return self.filter(answer_id=a_id, is_upvote=True)

    def ans_downvotes(self, a_id):
        return self.filter(answer_id=a_id, is_upvote=False)

    def by_answer(self, a_id):
        return self.filter(answer_id=a_id)


class AnswerLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    is_upvote = models.BooleanField(verbose_name="Положительный")

    objects = AnswerLikeManager()

    class Meta:
        verbose_name = "Лайк на ответе"
        verbose_name_plural = "Лайки на ответах"


class TagManager(models.Manager):
    def by_title(self, title_name):
        return self.filter(title=title_name)

    def popular(self):
        return self.order_by('-question_count')[:20]


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True,
                             verbose_name="Название")
    objects = TagManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by("-creation_date")

    def hot(self):
        return self.order_by("-like_count")

    def by_tag(self, tag_title):
        return self.filter(tags__title=tag_title)


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    title = models.CharField(max_length=100, verbose_name="Название", unique=True)
    text = models.TextField(verbose_name="Текст")
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    like_count = models.IntegerField(default=0, verbose_name='Кол-во лайков')
    answer_count = models.IntegerField(default=0, verbose_name='Кол-во ответов')
    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class AnswerManager(models.Manager):
    def by_question(self, question_pk):
        return self.filter(question=Question.objects.get(pk=question_pk)).order_by('like_count')


class Answer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.TextField("Текст")
    creation_date = models.DateField(
        auto_now_add=True, verbose_name="Дата создания")
    like_count = models.IntegerField(default=0, verbose_name='Кол-во лайков')
    objects = AnswerManager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"