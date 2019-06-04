from django.shortcuts import render
import random
import pandas as pd
from app.models import Products
from django.http import HttpResponse
from django_pandas.io import read_frame
# UPLOAD_FOLDER="F:/coding/django_tutorials/products_importer/app/static/products"
# Create your views here.
def home(request):
    return render(request, "upload.html")


def upload(request):
    myfile = request.FILES['file']
    print(myfile.filename)
    with open('products.csv', 'wb+') as destination:
        for chunk in myfile.chunks():
            destination.write(chunk)
    # filepath = os.path.join(UPLOAD_FOLDER, myfile.filename)

    data = pd.read_csv('products.csv', chunksize=1000000)

    chunk_list = []

    for chunk in data:
        chunk_list.append(chunk)

    df_concat = pd.concat(chunk_list)
    stats=['active','inactive']
    df_concat = df_concat.drop_duplicates(subset='sku', keep="last")
    # print(df_concat['sku'])
    df_records = df_concat.to_dict('records')
    print("gonna save")
    model_instances = [Products(
        sku=record['sku'],
        description=record['description'],
        name=record['name'],
        status=random.choice(stats)
    ) for record in df_records]

    Products.objects.bulk_create(model_instances)
    # obj = Products()
    # obj.sku = df_concat['sku']
    # obj.description = df_concat['description']
    # obj.name = df_concat['name']
    # print("Saving")
    # obj.save()
    print("finishes")
    return render(request, "upload.html")
template = """
<!doctype html>
<input type="text" value="" name="my_filter" id="my_filter">

<div id="results">{{ data|safe }}</div>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

<script type="text/javascript">
   $('#my_filter').keyup(function() {
       if ($(this).val().length >= 1) {
           var requested_code = document.getElementById('my_filter').value;

           $.ajax({
               type: 'POST',
               data: JSON.stringify({
                   'requested_code': requested_code
               }),
               contentType: 'application/json; charset=utf-8',
               url: "{{ url_for('filter_html') }}",
               success: function(resp) {
                   $("#results").html(resp);
               }
           });

       }
});
</script>
</html>
"""

def products(request):
    try:
        qs = Products.pdobjects.all()  # Use the Pandas Manager
        df = qs.to_dataframe()
        template = 'test.html'

        # Format the column headers for the Bootstrap table, they're just a list of field names,
        # duplicated and turned into dicts like this: {'field': 'foo', 'title: 'foo'}
        columns = [{'field': f.column, 'title': f.column} for f in Products._Meta.fields]
        # Write the DataFrame to JSON (as easy as can be)
        json = df.to_json(orient='records')  # output just the records (no fieldnames) as a collection of tuples
        # Proceed to create your context object containing the columns and the data
        context = {
            'data': json,
            'columns': columns
        }
        # And render it!
        return render(request,  template, context,content_type='application/json')

        # products = Products.objects.all()
        # df = read_frame(products)
        # html = df.to_html()
        # return render_template_string(template, data=df.to_html(index=False))
        # return HttpResponse(html)
        #
        # print("Returnn")
        # return render(request, "products.html", {"products": products})

    except Exception as e:
        return (str(e))



def products_delete(request):
    Products.objects.truncate()
    return render(request, "upload.html")