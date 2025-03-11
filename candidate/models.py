from django.db import models


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20
    )  # Char field because we probably won't be doing arithmetic operations on it
