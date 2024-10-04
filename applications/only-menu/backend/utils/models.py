from django.db import models

from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_createdby', on_delete=models.CASCADE, null=True)
    modified_by = models.ForeignKey(User, related_name='%(class)s_modifiedby', null=True,
                                    blank=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True
