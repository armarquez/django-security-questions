import factory

from django_security_questions import models
from django_security_questions.compat import user_model_label


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = user_model_label
        django_get_or_create = ('username',)

    first_name = 'John'
    last_name = 'Doe'
    username = factory.LazyAttribute(lambda obj: '%s.%s' % (obj.first_name.lower(), obj.last_name.lower()))
    email = factory.LazyAttribute(lambda obj: '%s.%s@example.com' % (obj.first_name.lower(), obj.last_name.lower()))


class SecurityQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SecurityQuestion

    question = factory.Sequence(lambda n: "Question #%s" % n)


class SecurityAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SecurityAnswer

    user = factory.SubFactory(UserFactory)
    question = factory.SubFactory(SecurityQuestionFactory)
    answer = factory.PostGenerationMethodCall('set_answer', 'Answer')


#class UserWithSecurityQuestion(factory.django.DjangoModelFactory):
