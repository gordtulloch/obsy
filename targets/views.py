# targets/views.py
from django.views.generic import ListView
from astroquery.simbad import Simbad
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from .models import target
from setup.models import objectsCatalog
import logging

logger = logging.getLogger("targets.views")

class target_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_list.html"

class target_all_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"

def target_query(request):
    if request.method == 'POST':
        Simbad.TIMEOUT = 10 # sets the timeout to 10s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            results_simbad = Simbad.query_object(search_term, wildcard=True)
            if (results_simbad):
                df=results_simbad.to_pandas()
                results=df.to_dict('records')
            else: 
                results=[]
            return render(request, 'targets/target_result.html',{'results': results})
        except:
            error_message="Search Timeout occurred with search: "+search_term
            logger.warning(error_message)
            return render(request, 'targets/target_search.html',{'error': error_message})
    return render(request, 'targets/target_search.html')

def target_create(request):
    if request.method == "POST":
        form = targetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("target_list")
    else:
        form = targetForm()
    return render(request, "targets/target_form.html", {"form": form})

def target_update(request, pk):
    target = get_object_or_404(target, pk=pk)
    if request.method == "POST":
        form = targetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            return redirect("target_list")
    else:
        form = targetForm(instance=target)
    return render(request, "targets/target_form.html", {"form": form})

def target_delete(request, pk):
    target = get_object_or_404(target, pk=pk)
    if request.method == "POST":
        target.delete()
        return redirect("target_list")
    return render(request, "targets/target_confirm_delete.html", {"target": target})
