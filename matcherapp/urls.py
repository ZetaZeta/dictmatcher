from django.urls import path

from . import views
from .util import load_dict
import os
from django.conf import settings

# Currently the dictionary is loaded only once, on startup.
# If we want to be able to live-swap it, we need either an interface
# to force-reload it, or to watch the filesystem for changes to it.
# We might also want to store it in a database or some other place
# that makes it easier to monitor and load from.
load_dict(settings.DICT_LOCATION)

app_name = 'matcherapp'
urlpatterns = [
    path('', views.index, name='index'),
]
