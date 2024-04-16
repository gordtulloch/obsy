# targets/views.py
from django.views.generic import ListView
from astroquery.simbad import Simbad

from django.shortcuts import render, get_object_or_404, redirect
from .models import target
from .forms import targetForm,targetQueryForm

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
        search_term = request.POST.get('search_term')
        try:
            result_table = Simbad.query_object(search_term)
            if result_table:
                main_identifier = result_table['MAIN_ID'][0]
                target_ra = result_table['RA'][0]
                target_dec = result_table['DEC'][0]
                
                return render(request, 'targets/target_result.html', ({'main_identifier': main_identifier,'target_ra': target_ra,'target_dec': target_dec}))
            else:
                return render(request, 'targets/target_result.html', {'error_message': 'No results found.'})
        except Exception as e:
            return render(request, 'targets/target_result.html', {'error_message': f'Error: {str(e)}'})
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
