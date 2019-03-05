from django.shortcuts import render
from django.http import HttpResponse
from .util import get_matching_by_button

# Handles a request.  Most of the heavy lifting is in a utility file,
# which keeps views clean.
def index(request):
    output_list = []
    context = {'outputList': output_list}

    # Postback when button is pushed.
    # When multiple matchings are implemented,
    # which one is applied will be determined by which button was pushed.
    if request.method == 'POST':
        matching = get_matching_by_button(request)
        if matching == None:
            output_list.append("[None].  No matches found.")
        else:
            output_list.extend(matching)
    return render(request, 'dictmatcher/index.html', context)
