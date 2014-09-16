from django.contrib.auth import hashers
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .compat import user_model_label


class SecurityQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=150, null=False, blank=False)

    class Meta:
        db_table = "security_questions"

    def __unicode__(self):
        return _("%s") % self.question


class SecurityAnswer(models.Model):
    user = models.ForeignKey(user_model_label)
    question = models.ForeignKey("SecurityQuestion", verbose_name=_("Security Question"))
    answer = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        db_table = "security_answer"

    def __unicode__(self):
        return _("%s - %s") % (self.user, self.question)

    def hash_current_answer(self):
        self.set_answer(self.answer)

    def set_answer(self, raw_answer):
        if not bool(getattr(settings, "QUESTIONS_CASE_SENSITIVE", False)):
            raw_answer = raw_answer.upper()
        self.answer = hashers.make_password(raw_answer)

    def check_answer(self, raw_answer):
        if not bool(getattr(settings, "QUESTIONS_CASE_SENSITIVE", False)):
            raw_answer = raw_answer.upper()

        def setter(raw_answer):
            self.set_answer(raw_answer)
            self.save(update_fields=["answer"])
        return hashers.check_password(raw_answer, self.answer, setter)

    def set_unusable_answer(self):
        self.answer = hashers.make_password(None)

    def has_usable_answer(self):
        return hashers.is_password_usable(self.answer)