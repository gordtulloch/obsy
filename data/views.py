from django.shortcuts import render
from .models import fitsFile,fitsHeader
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
import logging

logger = logging.getLogger("data.views")

##################################################################################################
## FitsFileAllList - List all FITS files                                                        ## 
##################################################################################################
class fitsFile_all_list(ListView):
    model=fitsFile
    context_object_name="fitsFile_all_list"
    template_name="targets/fitsFile_all_list.html"
    login_url = "account_login"

##################################################################################################
## fitsHeaderAllList - List all FITS headers                                                    ## 
##################################################################################################
class fitsHeader_all_list(ListView):
    model=fitsHeader
    context_object_name="fitsHeader_all_list"
    template_name="data/fitsHeader_all_list.html"
    login_url = "account_login"

##################################################################################################
## fitsFile_detail_view - List fitsFile detail with DetailView template                         ## 
##################################################################################################
class fitsFile_detail_view(DetailView):
    model = fitsFile
    context_object_name = "fitsFile"
    template_name = "data/fitsFile_detail.html"
    login_url = "account_login"

##################################################################################################
## targetDetailView - List target detail with DetailView template                               ## 
##################################################################################################
class fitsHeader_detail_view(DetailView):
    model = fitsHeader
    context_object_name = "fitsHeader"
    template_name = "data/fitsHeader_detail.html"
    login_url = "account_login"
