from django.shortcuts import render, get_object_or_404, redirect
from .models import observation
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import UpdateView, DeleteView
from .forms import ObservationUpdateForm, ObservationForm
from targets.models import target

import logging

logger = logging.getLogger("obsy")

##################################################################################################
## observationDetailView - List observation detail with DetailView template                               ## 
##################################################################################################
class observation_detail_view(DetailView):
    model = observation
    context_object_name = "observation"
    template_name = "observations/observation_detail.html"
    login_url = "account_login"
     
##################################################################################################
## observationAllList - List all observations                                                             ## 
##################################################################################################
class observation_all_list(ListView):
    model=observation
    context_object_name="observation_list"
    template_name="observations/observation_all_list.html"
    login_url = "account_login"

##################################################################################################
## Observation Update     -  Use the UpdateView class to edit observation records                         ##
##################################################################################################
class observation_update(UpdateView):
    model = observation
    form_class = ObservationUpdateForm
    template_name = "observations/observation_form.html"
    success_url = reverse_lazy('observation_all_list')
    
##################################################################################################
## Observation Delete     -  Use the DeleteView class to edit observation records               ##
##################################################################################################    
class observation_delete(DeleteView):
    model = observation
    template_name = "observations/observation_confirm_delete.html"
    success_url = reverse_lazy('observation_all_list')

##################################################################################################
## Observation create     -  Use the class to edit observation records               ##
################################################################################################## 
def observation_create(request,target_uuid):    
    if request.method == 'POST':
        form = ObservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')  
    else:
        form = ObservationForm()
    return render(request, 'observations/observation_create.html', {'form': form})