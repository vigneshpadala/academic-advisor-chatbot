from django.db import models


class PDFDocument(models.Model):
    file_name = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.file_name
