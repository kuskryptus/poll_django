from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Prefetch
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Choice, Question, Poll, Answer
from rest_framework.views import APIView
from rest_framework.response import Response
from polls.serializers import AnswerSerializer, PollDetailSerializer
from rest_framework import status
from rest_framework.generics import RetrieveAPIView


@method_decorator(cache_page(60 * 60), name='dispatch')
class IndexView(generic.ListView):
    model = Poll
    template_name = "polls/index.html"
    context_object_name = "polls"


@method_decorator(cache_page(60 * 60), name='dispatch')
class DetailView(generic.DetailView):
    model = Poll
    template_name = "polls/questions.html"
    context_object_name = "poll"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = context["poll"]
        questions = poll.questions.prefetch_related("choices")
        context["questions"] = questions
        return context


class ResultsView(generic.DetailView):
    model = Poll
    template_name = "polls/results.html"

    def get_object(self, queryset=None):
        poll_id = self.kwargs.get("poll_id")
        return get_object_or_404(Poll.objects.prefetch_related\
                                 (Prefetch('questions__choices',\
                                queryset=Choice.objects.annotate\
                                (answer_count=Count('answers')))), id=poll_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll_id = self.kwargs.get("poll_id")

        poll = self.get_object()
        question_data = []

        for question in poll.questions.all():
            choice_data = []

            for choice in question.choices.all():
                choice_data.append({
                    'choice_text': choice.choice_text,
                    'answer_count': choice.answer_count
                })

            question_data.append({
                'question_text': question.question_text,
                'choices': choice_data
            })

        context["question_data"] = question_data
        return context


@cache_page(60 * 60)
def vote(request, poll_id):
    poll = Poll.objects.prefetch_related('questions').get(pk=poll_id)
    answers = []
    all_questions = poll.questions.count()
    selected_choices = []

    for question in poll.questions.all():
        selected_choice_ids = [
            int(request.POST.get(f"choice{question.id}", 0))
        ]

        with transaction.atomic():
            choice_queryset = Choice.objects.filter(id__in=selected_choice_ids,
                                                    question=question)
            choice_queryset.update(selected=True)

        Choice.objects.exclude(id__in=selected_choice_ids).filter(
            question=question).update(selected=False)

    for question in poll.questions.all():
        try:
            selected_choice = question.choices.get(pk=request.POST\
                                                      [f"choice{question.id}"])
            answer = Answer(choice=selected_choice)
            answers.append(answer)

        except (KeyError, Choice.DoesNotExist):
            missing_questions = [question for question in poll.questions.all()\
                                    if not request.POST.get(f"choice{question.id}")]

            return render(
                request, "polls/questions.html", {
                    "questions": poll.questions.all(),
                    "error_message": "You didn't select a choice.",
                    "missing_questions": missing_questions,
                    "poll": poll,
                })

    else:
        for answer in answers:
            answer.save()
        for question in poll.questions.all():
            for choice in question.choices.all():
                choice.selected_false()

        return HttpResponseRedirect(reverse("polls:results", args=(poll.id, )))


class VoteApiView(APIView):

    def post(self, request, poll_id):
        poll = Poll.objects.get(pk=poll_id)
        answers_data = request.POST
        questions = poll.questions.all().count()
        answers = []

        for question_id, choice_id in answers_data.items():
            if question_id.startswith('choice') and choice_id:
                try:
                    question_id = int(question_id.replace('choice', ''))
                    question = Question.objects.get(pk=question_id, poll=poll)
                    choice = Choice.objects.get(pk=choice_id,
                                                question=question)
                    answer = Answer(choice=choice)
                    answers.append(answer)
                except (Question.DoesNotExist, Choice.DoesNotExist,
                        ValueError):
                    return Response({'error': 'Invalid question or choice'},\
                                     status=status.HTTP_400_BAD_REQUEST)
        if answers:
            serialized_answers = AnswerSerializer(answers, many=True)
            if len(answers) == questions:
                for answer in answers:
                    answer.save()
                return Response({'success': 'Votes added' , "answers": serialized_answers.data},\
                                 status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Please answer all questions'},\
                                 status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No valid votes submitted'},\
                             status=status.HTTP_400_BAD_REQUEST)


class PollDetailView(RetrieveAPIView):
    queryset = Poll.objects.prefetch_related('questions__choices__answers')

    serializer_class = PollDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)
