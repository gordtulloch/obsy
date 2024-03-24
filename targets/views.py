# targets/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import TargetModel
from .forms import TargetModelForm

def TargetModel_list(request):
    TargetModels = TargetModel.objects.all()
    return render(request, "targets/TargetModel_list.html", {"TargetModels": TargetModels})

def TargetModel_create(request):
    if request.method == "POST":
        form = TargetModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("TargetModel_list")
    else:
        form = TargetModelForm()
    return render(request, "targets/TargetModel_form.html", {"form": form})

def TargetModel_update(request, pk):
    TargetModel = get_object_or_404(TargetModel, pk=pk)
    if request.method == "POST":
        form = TargetModelForm(request.POST, instance=TargetModel)
        if form.is_valid():
            form.save()
            return redirect("TargetModel_list")
    else:
        form = TargetModelForm(instance=TargetModel)
    return render(request, "targets/TargetModel_form.html", {"form": form})

def TargetModel_delete(request, pk):
    TargetModel = get_object_or_404(TargetModel, pk=pk)
    if request.method == "POST":
        TargetModel.delete()
        return redirect("TargetModel_list")
    return render(request, "targets/TargetModel_confirm_delete.html", {"TargetModel": TargetModel})
