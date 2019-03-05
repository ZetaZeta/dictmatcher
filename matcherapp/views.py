from django.shortcuts import render
from django.http import HttpResponse
from .util import get_matching_by_button

def index(request):
    outputList = []
    context = {'outputList': outputList}
    
    if request.method == 'POST':
        outputList.extend(get_matching_by_button(request))
    return render(request, 'dictmatcher/index.html', context)
