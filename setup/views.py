from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import observatory, telescope, imager
from .forms import ObservatoryForm, TelescopeForm, ImagerForm

class ObservatoryListView(ListView):
    model = observatory
    template_name = 'setup/observatory_list.html'
    context_object_name = 'observatory_list'

class TelescopeListView(ListView):
    model = telescope
    template_name = 'setup/telescope_list.html'
    context_object_name = 'telescope_list'

    def get_queryset(self):
        return telescope.objects.select_related('observatoryId').all()

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
    template_name = 'setup/observatory_form.html'
    success_url = reverse_lazy('observatory_list')

class TelescopeCreateView(CreateView):
    model = telescope
    form_class = TelescopeForm
    template_name = 'setup/telescope_form.html'
    success_url = reverse_lazy('telescope_list')

class TelescopeUpdateView(UpdateView):
    model = telescope
    form_class = TelescopeForm
    template_name = 'setup/telescope_form.html'
    success_url = reverse_lazy('telescope_list')

class ImagerCreateView(CreateView):
    model = imager
    form_class = ImagerForm
    template_name = 'setup/imager_form.html'
    success_url = reverse_lazy('imager_list')

class ImagerUpdateView(UpdateView):
    model = imager
    form_class = ImagerForm
    template_name = 'setup/imager_form.html'
    success_url = reverse_lazy('imager_list')

