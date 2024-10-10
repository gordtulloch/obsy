from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView
from .forms import CurrentConfigForm
from .models import currentConfig

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

def realtimeLogView(request):
    return render(request, 'operations/realtimeLog.html')
