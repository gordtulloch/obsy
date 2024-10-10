# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import target,simbadType
from .forms import TargetUpdateForm, TargetImportForm
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

import logging

import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation
import ephem
from datetime import datetime

logger = logging.getLogger("targets.views")

##################################################################################################
## targetDetailView - List target detail with DetailView template                               ## 
##################################################################################################
class target_detail_view(DetailView):
    model = target
    context_object_name = "target"
    template_name = "targets/target_detail.html"
    login_url = "account_login"
     
##################################################################################################
## targetAllList - List all targets                                                             ## 
##################################################################################################
class target_all_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"
    login_url = "account_login"

##################################################################################################
## assignTargetClass -  A helper function that looks up targetClass based on the label          ## 
##                      from SIMBAD                                                             ##
##################################################################################################
def assignTargetClass(targetType):
    allwithTT=simbadType.objects.filter(label=targetType)
    firstentry= simbadType.objects.first()
    if firstentry != None: 
        return firstentry.category
    else:
        logger.warning("Type "+targetType+" not found in simbadTypes table")
        return "Unknown"

##################################################################################################
## Target Query     -  Allow the user to search for objects using SimBad                        ##
##################################################################################################
def target_query(request):
    error_message=""
    if request.method == 'POST':
        Simbad.TIMEOUT = 10 # sets the timeout to 10s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
            if (len(results_simbad)>0):
                df=results_simbad.to_pandas()
                results=df.to_dict('records')
                # Add results to the targets database
                for index, row in df.iterrows():
                    # Figure out the constellation
                    coords=row["RA"]+" "+row["DEC"]
                    c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                    
                    # Add the target record
                    target.objects.create(               
                        targetName = row["MAIN_ID"],
                        targetType  =row["OTYPE_main"],
                        targetClass=assignTargetClass(row["OTYPE_main"]),
                        targetRA2000 = row["RA"],
                        targetDec2000 = row["DEC"],
                        targetConst = get_constellation(c),
                        targetMag = row["FLUX_V"],
                        )
            else: 
                results=[]
            return render(request, 'targets/target_result.html',{'results': results})
        except astroquery.exceptions.TableParseError as ex:
            error_message="Search Error occurred with search ("+search_term+" error: "+ex
            logger.error(error_message)
            return render(request, 'targets/target_search.html',{'error': error_message})
    else:
        return render(request, 'targets/target_search.html',{'error': error_message})
    
##################################################################################################
## Target Update     -  Use the UpdateView class to edit target records                         ##
##################################################################################################
class target_update(UpdateView):
    model = target
    form_class = TargetUpdateForm
    template_name = "targets/target_form.html"
    success_url = reverse_lazy('target_all_list')
    
##################################################################################################
## Target Delete     -  Use the DeleteView class to edit target records                         ##
##################################################################################################    
class target_delete(DeleteView):
    model = target
    template_name = "targets/target_confirm_delete.html"
    success_url = reverse_lazy('target_all_list')

def targetUpload(request):
    if request.method == 'POST':
        form = TargetImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('targetUploadSuccess')
    else:
        form = TargetImportForm()
    return render(request, 'targets/target_upload.html', {'form': form})

def targetUploadSuccess(request):
    # Actually import the data
    return HttpResponse('File uploaded successfully')

def importNGC(request):
    # Import the NGC catalog
    from pyongc import ongc
    objectList = ongc.listObjects()
    for obj in objectList:
        target.objects.create(
            targetName=obj['name'],
            targetType=obj['type'],
            targetClass=assignTargetClass(obj['type']),
            targetRA2000=obj['ra'],
            targetDec2000=obj['dec'],
            targetConst=obj['constellation'],
            targetMag=obj['magnitude'],
            )
    return redirect('targetUploadSuccess')
