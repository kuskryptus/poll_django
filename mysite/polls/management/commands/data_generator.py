import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from polls.models import Question, Answer, Choice, Poll


class Command(BaseCommand):
    help = 'Create Sample Data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        for poll_index in range(1, 11):
            poll = Poll.objects.create(poll_name=f'Poll {poll_index}')

            for question_index in range(1, 51):
                question = Question.objects.create(
                    question_text=f'Question {poll_index}-{question_index}',
                    pub_date=timezone.now(),
                    poll=poll)

                for choice_index in range(1, 6):
                    choice = Choice.objects.create(
                        question=question,
                        choice_text=
                        f'Choice {poll_index}-{question_index}-{choice_index}')

                    answer = Answer.objects.create(choice=choice)

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully.'))
