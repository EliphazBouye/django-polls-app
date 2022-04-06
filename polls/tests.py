import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertIs(response.status_code, 200)
        self.assertContains(response, "No poll are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_questions(self):
        question = create_question(question_text="Past question.", days=-30)
        question.choice_set.create(choice_text="y")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [question])

    def test_future_question(self):
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No poll are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [])

    # TODO review
    def test_future_question_and_past_question(self):
        question = create_question(question_text="Pas de question.", days=-30)
        create_question(question_text="Future question.", days=30)
        question.choice_set.create(choice_text="y")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [question])

    def test_two_past_questions(self):
        question1 = create_question(question_text="Past question1", days=-40)
        question1.choice_set.create(choice_text="y")
        question2 = create_question(question_text="Past question2", days=-30)
        question2.choice_set.create(choice_text="y")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 question2, question1])

    def test_question_who_have_not_choice(self):
        question = create_question(question_text="A question", days=-1)
        # choices = question.choice_set.count()
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No poll are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


class QuestionDetailsViewTests(TestCase):
    def test_future_question_detail(self):
        future_question = create_question(
            question_text="Future question", days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_detail(self):
        past_question = create_question(question_text="Past question", days=-2)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_questions(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_with_old_questions(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_publishid_with_recent_questions(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
