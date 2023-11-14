from rest_framework import serializers
from .models import Question, Choice, Answer, Poll


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    num_answers = serializers.SerializerMethodField()

    def get_num_answers(self, choice):
        return choice.answers.count()

    class Meta:
        model = Choice
        fields = ('id', 'choice_text', "num_answers")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'pub_date', "choices")


class PollDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'poll_name', 'created_at', 'questions')
