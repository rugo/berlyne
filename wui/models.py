from django.db import models
import vmapi.models
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext_lazy as _


class Course(models.Model):
    name = models.SlugField(_('name'), unique=True)
    description = models.TextField(_('description'), max_length=1024)
    creation_time = models.DateTimeField(_('creation date'), auto_now_add=True)
    # start_time = models.DateTimeField(_('start time'), )
    # end_time = models.DateTimeField(_('end time'), )
    show_scoreboard = models.BooleanField(_('show scoreboard'), default=True)

    teacher = models.ForeignKey(auth_models.User,
                                related_name='teacher_courses')
    participants = models.ManyToManyField(auth_models.User)

    # Pre shared key needed to join
    password = models.CharField(_('password'), max_length=255, blank=True, default="")

    # Points needed to pass
    point_threshold = models.IntegerField(_('point threshold'), )

    # instances of problems (VMs)
    problems = models.ManyToManyField(vmapi.models.VirtualMachine,
                                      through='CourseProblems')

    writeups = models.BooleanField(_("write ups"))

    def __str__(self):
        return "{} ({})".format(
            self.name,
            self.teacher.last_name or self.teacher.username
        )

    def has_user(self, user):
        if not isinstance(user, str):
            user = user.username

        return self.participants.filter(username=user).exists()


class CourseProblems(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    problem = models.ForeignKey(
        vmapi.models.VirtualMachine,
        on_delete=models.CASCADE
    )
    points = models.IntegerField()

    class Meta:
        unique_together = ('course', 'problem')

    @classmethod
    def create_or_update(cls, course, problem, points=0):
        cp = cls.objects.filter(course=course, problem=problem).first()
        if not cp:
            cp = cls(course=course, problem=problem, points=points)
        cp.points = points
        cp.save()

    @staticmethod
    def check_problem_flag(course, problem_slug, flag):
        cp = CourseProblems.objects.get(
            course=course,
            problem__slug=problem_slug
        )
        correct = cp.problem.flag == flag
        return correct, cp

    def __str__(self):
        return str(self.problem)


class Submission(models.Model):
    flag = models.CharField(_('flag'), max_length=255)
    problem = models.ForeignKey(CourseProblems, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField(_('correct'))
    writeup = models.TextField(_('write up'), null=True)
    user = models.ForeignKey(auth_models.User)

    class Meta:
        unique_together = ('flag', 'correct', 'user', 'problem')

    def __str__(self):
        return "<{}:{}>".format(self.correct, self.flag)
