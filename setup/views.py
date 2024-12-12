from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import observatory, telescope, imager, currentConfig
from .forms import ObservatoryForm, TelescopeForm, ImagerForm, CurrentConfigForm

class CurrentConfigListView(ListView):
    model = currentConfig
    template_name = 'setup/currentConfig_list.html'
    context_object_name = 'currentConfig_list'

class CurrentConfigCreateView(CreateView):
    model = currentConfig
    form_class = CurrentConfigForm
    template_name = 'setup/currentConfig_form.html'
    success_url = reverse_lazy('currentConfig_list')

class CurrentConfigUpdateView(UpdateView):
    model = currentConfig
    form_class = CurrentConfigForm
    template_name = 'setup/currentConfig_form.html'
    success_url = reverse_lazy('currentConfig_list')

    def get_object(self, queryset=None):
        return get_object_or_404(currentConfig, pk=self.kwargs['pk'])
    
class CurrentConfigDeleteView(DeleteView):
    model = currentConfig
    template_name = 'setup/currentConfig_confirm_delete.html'
    success_url = reverse_lazy('currentConfig_list')

class ObservatoryListView(ListView):
    model = observatory
    template_name = 'setup/observatory_list.html'
    context_object_name = 'observatory_list'
    
class TelescopeListView(ListView):
    model = telescope
    template_name = 'setup/telescope_list.html'
    context_object_name = 'telescope_list'

class ImagerListView(ListView):
    model = imager
    template_name = 'setup/imager_list.html'
    context_object_name = 'imager_list'
    
class ObservatoryCreateView(CreateView):
    model = observatory
    form_class = ObservatoryForm
    template_name = 'setup/observatory_form.html'
    success_url = reverse_lazy('observatory_list')

class ObservatoryUpdateView(UpdateView):
    model = observatory
    form_class = ObservatoryForm
    template_name = 'setup/observatory_detail.html'
    success_url = reverse_lazy('observatory_list')
  
class TelescopeCreateView(CreateView):
    model = telescope
    form_class = TelescopeForm
    template_name = 'setup/telescope_form.html'
    success_url = reverse_lazy('telescope_list')

class TelescopeUpdateView(UpdateView):
    model = telescope
    form_class = TelescopeForm
    template_name = 'setup/telescope_detail.html'
    success_url = reverse_lazy('telescope_list')

class ImagerCreateView(CreateView):
    model = imager
    form_class = ImagerForm
    template_name = 'setup/imager_form.html'
    success_url = reverse_lazy('imager_list')

class ImagerUpdateView(UpdateView):
    model = imager
    form_class = ImagerForm
    template_name = 'setup/imager_detail.html'
    success_url = reverse_lazy('imager_list')

