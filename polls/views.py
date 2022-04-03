from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello words , your are at the polls index")
