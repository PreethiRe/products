from django.shortcuts import render
import random
import pandas as pd
from app.models import Products
from django.http import HttpResponse
from django_pandas.io import read_frame


def home(request):
    return render(request, "upload.html")


def upload(request):
    myfile = request.FILES['file']

    with open('products.csv', 'wb+') as destination:
        for chunk in myfile.chunks():
            destination.write(chunk)

    data = pd.read_csv('products.csv', chunksize=1000000)

    chunk_list = []

    for chunk in data:
        chunk_list.append(chunk)

    df_concat = pd.concat(chunk_list)
    stats = ['active', 'inactive']
    df_concat = df_concat.drop_duplicates(subset='sku', keep="last")

    df_records = df_concat.to_dict('records')

    model_instances = [Products(
        sku=record['sku'],
        description=record['description'],
        name=record['name'],
        status=random.choice(stats)
    ) for record in df_records]

    Products.objects.bulk_create(model_instances)

    return render(request, "upload.html")


def products(request):
    try:

        products = Products.objects.all()
        df = read_frame(products)
        html = df.to_html()

        return HttpResponse(html)

    except Exception as e:
        return (str(e))


def products_delete(request):
    Products.objects.truncate()
    return render(request, "upload.html")
