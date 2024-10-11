from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView
from .forms import CurrentConfigForm
from .models import currentConfig
from django.core.paginator import Paginator

import os
import logging

logger = logging.getLogger("operations.views")

class CurrentConfigListView(ListView):
    model = currentConfig
    template_name = 'operations/currentConfig_list.html'
    context_object_name = 'currentConfig_list'

class CurrentConfigCreateView(CreateView):
    model = currentConfig
    form_class = CurrentConfigForm
    template_name = 'operations/currentConfig_form.html'
    success_url = reverse_lazy('currentConfig_list')

class CurrentConfigUpdateView(UpdateView):
    model = currentConfig
    form_class = CurrentConfigForm
    template_name = 'operations/currentConfig_form.html'
    success_url = reverse_lazy('currentConfig_list')

    def get_object(self, queryset=None):
        return get_object_or_404(currentConfig, pk=self.kwargs['pk'])
    
class CurrentConfigDeleteView(DeleteView):
    model = currentConfig
    template_name = 'operations/currentConfig_confirm_delete.html'
    success_url = reverse_lazy('currentConfig_list')
    
def power110PanelView(request):
    return render(request, 'operations/power110_panel.html',{'range': range(1, 8)})

def power12PanelView(request):
    return render(request, 'operations/power12_panel.html',{'range': range(1, 16)})

def LogView(request):
    file_path = 'obsy.log'
    if not os.path.exists(file_path):
        reversed_lines = ["Log file does not exist"]
        logger.error("Log file does not exist")
    else:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        stripped_lines = [line.strip() for line in lines]
        reversed_lines = stripped_lines[::-1]

    # Paginate the log entries
    paginator = Paginator(reversed_lines, 20)  # Show 20 log entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'operations/logViewer.html', {'page_obj': page_obj})