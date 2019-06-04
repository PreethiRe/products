from django.db import models
from django_pandas.managers import DataFrameManager


# Create your models here.
class Products(models.Model):
    name = models.TextField()
    sku = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=10)
    objects = models.Manager()
    pdobjects = DataFrameManager()

    class Meta:
        db_table = "products"
        managed = True