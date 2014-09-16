from django import forms
from django.conf import settings
from django.forms import models, ValidationError
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import modelformset_factory
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from .models import SecurityAnswer


class BaseSecurityQuestionsRegisterFormSet(models.BaseModelFormSet):
    class Meta:
        model = SecurityAnswer

    def __init__(self, *args, **kwargs):
        self.num_questions = getattr(settings, "QUESTIONS_NUM_REGISTER")
        super(BaseSecurityQuestionsRegisterFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            # Do not bother validating the formset unless each form is valid on its own
            return
        if self.management_form.cleaned_data["TOTAL_FORMS"] < self.num_questions:
            raise ValidationError(
                _("ManagementForm data is missing or has been tampered with"),
                code='management_form_missing',
            )
        completed = 0
        values = set()
        for cleaned_data in self.cleaned_data:
            # form has data and we are not deleting it.
            if cleaned_data and not cleaned_data.get("DELETE", False):
                completed += 1
            # security question is not the same
            if cleaned_data.get("question", None):
                value = cleaned_data["question"]
                if value in values:
                    raise ValidationError(
                        _("Must select different security questions"),
                        code='security_questions_same'
                    )
                values.add(value)

        if completed < self.num_questions:
            raise ValidationError(
                _("%(value)s security question and answer pairs are required"),
                code='security_questions_cnt',
                params={'value': self.num_questions}
            )
        self.validate_unique()


SecurityQuestionsRegisterFormSet = modelformset_factory(SecurityAnswer,
                                                        fields=("question", "answer"),
                                                        formset=BaseSecurityQuestionsRegisterFormSet,
                                                        extra=getattr(settings, "QUESTIONS_NUM_REGISTER"),
                                                        can_delete=False
                                                        )


class SecurityQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.sa_obj = kwargs.pop("security_answer_obj")
        super(SecurityQuestionForm, self).__init__(*args, **kwargs)
        self.fields["user_answer"] = forms.CharField(label=self.sa_obj.question.question,
                                                     initial="", required=True)
        self.fields["security_question"] = forms.IntegerField(initial=self.sa_obj.pk,
                                                              widget=forms.HiddenInput(attrs={"readonly": True}))

    def clean_user_answer(self):
        if (hasattr(self, "cleaned_data") and
                self.cleaned_data.get("user_answer", None) and
                not self.cleaned_data.get("DELETE", False)):
            if not self.sa_obj.check_answer(self.cleaned_data["user_answer"]):
                raise ValidationError(
                    _("Incorrect answer to security question"),
                    code='security_question_incorrect'
                )
        return self.cleaned_data["user_answer"]


class BaseSecurityQuestionResetFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.num_questions = int(getattr(settings, "QUESTIONS_NUM_RESET"))
        self.user = kwargs.pop("user")
        super(BaseSecurityQuestionResetFormSet, self).__init__(*args, **kwargs)
        if len(self.data) > 0:
            # If data is being passed to the form (likely a POST)
            q_pks = []
            if int(self.management_form.cleaned_data["TOTAL_FORMS"]) != self.num_questions:
                raise ValidationError(
                    _("ManagementForm data is missing or has been tampered with"),
                    code='management_form_missing'
                )
            for i in range(self.num_questions):
                field_name = "form-%s-security_question" % i
                try:
                    q_pks.append(int(self.data[field_name]))
                except KeyError:
                    raise ValidationError(
                        _("Missing security question(s) and answer(s)"),
                        code='security_questions_missing'
                    )
            qs = SecurityAnswer.objects.filter(pk__in=q_pks).all()
            for pk in q_pks:
                qs = sorted(qs, key=lambda x: x.pk == pk)
            self.sa_objs = qs
        else:
            # No data is being passed to teh form (likely a GET)
            qs = SecurityAnswer.objects.filter(user=self.user).order_by("?")
            self.sa_objs = qs[:self.num_questions]
        self.extra = len(self.sa_objs)
        if self.extra < self.num_questions:
            raise Http404(_("User does not have %s security questions") % self.num_questions)

        for form in self.forms:
            form.empty_permitted = False

    def _construct_form(self, index, **kwargs):
        # Passing a SecurityAnswer objects to each form
        kwargs["security_answer_obj"] = self.sa_objs[index]
        return super(BaseSecurityQuestionResetFormSet, self)._construct_form(index, **kwargs)

    def clean(self):
        if any(self.errors):
            # Provide a generic answer, and do not leak information about which questions are incorrect
            raise ValidationError(
                _("Incorrect answer to 1 or more security questions"),
                code='security_questions_incorrect'
            )

SecurityQuestionsResetFormSet = formset_factory(SecurityQuestionForm,
                                                formset=BaseSecurityQuestionResetFormSet,
                                                can_delete=False
                                                )