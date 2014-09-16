from django.conf import settings
from django.forms import ValidationError
from django.http import Http404
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from django_security_questions.forms import SecurityQuestionsRegisterFormSet, SecurityQuestionsResetFormSet

from .factories import SecurityAnswerFactory, UserFactory


class BaseSecurityQuestionsFormSetTest(TestCase):

    def setUp(self):
        # Create user with security questions
        self.user = UserFactory.create()
        SecurityAnswerFactory.create_batch(2, user=self.user)

        # Create user without security questions
        self.bad_user = UserFactory.create(first_name="Bad")

    def test_base_security_questions_register_formset(self):
        invalid_data_dicts = [
            {  # Number of security questions less than what was initially rendered
                "data": {
                    "form-TOTAL_FORMS": str(int(getattr(settings, "QUESTIONS_NUM_REGISTER")) - 1),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-question": "1",
                    "form-0-answer": "Answer"
                },
                "error": [_("ManagementForm data is missing or has been tampered with")]
            },
            {  # Selecting the same security question
                "data": {
                    "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_REGISTER")),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-question": "1",
                    "form-0-answer": "Answer",
                    "form-1-question": "1",
                    "form-1-answer": "Answer"
                },
                "error": [_("Must select different security questions")]
            },
            {  # Not enough security questions submitted
                "data": {
                    "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_REGISTER")),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-question": "1",
                    "form-0-answer": "Answer",
                },
                "error": [_("%s security question and answer pairs are required") % getattr(settings, "QUESTIONS_NUM_REGISTER")]
            }
        ]
        for invalid_dict in invalid_data_dicts:
            formset = SecurityQuestionsRegisterFormSet(data=invalid_dict["data"])
            self.failIf(formset.is_valid())
            self.assertEqual(formset.non_form_errors(), invalid_dict["error"])

        valid_data = {
            "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_REGISTER")),
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "",
            "form-0-question": "1",
            "form-0-answer": "Answer",
            "form-1-question": "2",
            "form-1-answer": "Answer"
        }
        form = SecurityQuestionsRegisterFormSet(data=valid_data)
        self.failUnless(form.is_valid())

    def test_base_security_questions_reset_formset(self):
        with self.assertRaises(Http404) as cm:
            SecurityQuestionsResetFormSet(user=self.bad_user)
        self.assertEqual(
            cm.exception.message,
            _("User does not have %s security questions") % getattr(settings, "QUESTIONS_NUM_RESET")
        )

        invalid_data_dicts = [
            {  # TOTAL_FORMS is not equal to setting for num of required questions
                "data": {
                    "form-TOTAL_FORMS": str(int(getattr(settings, "QUESTIONS_NUM_RESET")) - 1),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-security_question": "1",
                    "form-0-user_answer": "Answer"
                },
                "error": [_("ManagementForm data is missing or has been tampered with")]
            },
            {  # Missing security questions
                "data": {
                    "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_RESET")),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-security_question": "1",
                    "form-0-user_answer": "Answer"
                },
                "error": [_("Missing security question(s) and answer(s)")]
            },
        ]

        for invalid_dict in invalid_data_dicts:
            with self.assertRaises(ValidationError) as cm:
                SecurityQuestionsResetFormSet(data=invalid_dict["data"], user=self.user)
            self.assertEqual(
                cm.exception.messages,
                invalid_dict["error"]
            )

        invalid_data_dicts = [
            {  # In correct answer for the second question
                "data": {
                    "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_RESET")),
                    "form-INITIAL_FORMS": "0",
                    "form-MAX_NUM_FORMS": "",
                    "form-0-security_question": "1",
                    "form-0-user_answer": "Answer",
                    "form-1-security_question": "2",
                    "form-1-user_answer": "Wrong Answer",
                },
                "non_form_errors": [_("Incorrect answer to 1 or more security questions")],
                "errors": [{}, {'user_answer': [_("Incorrect answer to security question")]}]
            }
        ]

        for invalid_dict in invalid_data_dicts:
            formset = SecurityQuestionsResetFormSet(data=invalid_dict["data"], user=self.user)
            self.failIf(formset.is_valid())
            self.assertEqual(formset.non_form_errors(), invalid_dict["non_form_errors"])
            self.assertEqual(formset.errors, invalid_dict["errors"])

        valid_data = {
            "form-TOTAL_FORMS": str(getattr(settings, "QUESTIONS_NUM_RESET")),
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "",
            "form-0-security_question": "1",
            "form-0-user_answer": "Answer",
            "form-1-security_question": "2",
            "form-1-user_answer": "Answer"
        }
        formset = SecurityQuestionsResetFormSet(data=valid_data, user=self.user)
        self.failUnless(formset.is_valid())

    def tearDown(self):
        pass