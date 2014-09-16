from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


class QuestionsAddView(FormMixin, TemplateResponseMixin, ProcessFormView):
    """A view for security questions

    GET:
        Display a QuestionsFormset where each form has a ``question`` and ``answer``
        The same question can not be picked twice.

    POST:
        Associate the user with the selected ``question`` and inputted ``answer``
    """
    template_name = r'django_security_questions/questions_form.html'

