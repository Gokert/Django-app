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
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='', default=None)
    objects = ProfileManager()

    def user_exists(username):
        user = User.objects.filter(username=username)
        if user:
            return user
        else:
            return None


class TagManager(models.Manager):
    def get_top_tags(self, count=5):
        return self.annotate(answer_count=Count('tag_name')).order_by('-tags_count')[:count]

    def by_title(self, title_name):
        return self.filter(title=title_name)

    def popular(self):
        return self.order_by('-question_count')[:20]


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True,
                             verbose_name="Tag")

    tags_count = models.IntegerField(default=0, verbose_name='Number of tags')
    objects = TagManager()

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class QuestionManager(models.Manager):

    def new(self):
        return self.order_by("-creation_date")

    def hot(self):
        return self.order_by("-like_count")

    def by_tag(self, tag_name):
        return self.filter(tags__tag_name=tag_name)

    def get_info_questions(self):
        print(Count('likequestion', distinct=True))
        return self.annotate(count_answers=Count('answer', distinct=True),
                             raiting=Count('likequestion', distinct=True) - Count('dislikequestion', distinct=True))

    def get_question(self, id):
        try:
            return self.get_info_questions().get(id=id)
        except Question.DoesNotExist:
            return None

    def get_questions_by_user(self, user_id):
        return self.get_info_questions().filter(user_id=user_id).order_by('-publish_date')

    def is_question_from_this_user(self, question_id, user_id):
        return self.filter(id=question_id, user_id=user_id).exists()



class Question(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    title = models.CharField(max_length=100, verbose_name="Name", unique=True)
    text = models.TextField()
    creation_date = models.DateField(auto_now_add=True, verbose_name="Date of creation")
    like_count = models.IntegerField(default=0, verbose_name='Number of likes')
    answer_count = models.IntegerField(default=0, verbose_name='Number of answers')
    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

class AnswerManager(models.Manager):
    def get_info_answers(self):
        return self.annotate(raiting=Count('likeanswer', distinct=True) - Count('dislikeanswer', distinct=True))

    def get_answers_for_question(self, id):
        return self.get_info_answers().filter(question_id=id).order_by('-is_correct', 'publish_date')

    def get_answer(self, id):
        try:
            return self.get_info_answers().get(id=id)
        except Answer.DoesNotExist:
            return None

    def is_answer_from_this_user(self, answer_id, user_id):
        return self.filter(id=answer_id, user_id=user_id).exists()

    def get_correct_answer_for_question(self, question_id):
        answers = self.filter(question_id=question_id, is_correct=True)

        if len(answers):
            return answers[0]

        return None

    def by_question(self, question_pk):
        return self.filter(question=Question.objects.get(pk=question_pk)).order_by('like_count')


class Answer(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Text')
    creation_date = models.DateField(
        auto_now_add=True, verbose_name="Date of creation")
    like_count = models.IntegerField(default=0, verbose_name='Number of likes')
    is_correct = models.BooleanField(default=False)
    objects = AnswerManager()

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"


class LikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class DislikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class LikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class DislikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)
