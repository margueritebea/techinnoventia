from django.shortcuts import render

# Create your views here.
def home(request):

    data = {
       "user": {
           "username": "bea",
           "first_name": "Peve"
       }
    }
    return render(request, "core/index.html", context = data)
