from .serializers import CandidateSerializer
from .models import Candidate
from django.db.models import Q, Case, When, IntegerField, Value
from django.db.models.functions import Length
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class CandidateViewSet(viewsets.ViewSet):

    def list(self, *args, **kwargs):
        queryset = Candidate.objects.all()
        serializer = CandidateSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs):
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, pk, *args, **kwargs):
        try:
            instance = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CandidateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk, *args, **kwargs):
        try:
            instance = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def search(self, request: Request, *args, **kwargs):
        query: str = request.query_params.get("q", "").strip().lower()

        if len(query) < 3:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        words_to_search = query.split()

        filter_query = Q()
        for word in words_to_search:
            filter_query |= Q(name__icontains=word)

        exact_match = When(name__iexact=query, then=Value(100))

        word_cases = [
            When(name__icontains=word, then=Value(1)) for word in words_to_search
        ]

        queryset = (
            Candidate.objects.filter(filter_query)
            .annotate(
                relevancy=Case(
                    exact_match,
                    *word_cases,
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
            .annotate(name_length=Length("name"))
            .exclude(relevancy=0)
            .order_by("-relevancy", "name_length")
        )

        serializer = CandidateSerializer(queryset, many=True)
        return Response(serializer.data)
