# targets/views.py
from django.views.generic import ListView

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
        form = targetForm(request.POST)
        if form.is_valid():
            target_id = form.cleaned_data['targetName']
            # Fetch target information based on the target_id (e.g., query your database)
            # Populate a context dictionary with the retrieved information
            context = {
                'target_id': target_id,
                # Add other target-related data here
            }
            return render(request, 'targets/target_query.html', context)
    else:
        form = targetQueryForm()
    return render(request, 'targets/target_form.html', {'form': form})

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
