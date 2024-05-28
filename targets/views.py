# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from .models import target,simbadType
from .forms import TargetUpdateForm
from django.urls import reverse_lazy
from setup.models import objectsCatalog 
import logging
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation


logger = logging.getLogger("targets.views")

class target_detail_view(DetailView):
    model = target
    context_object_name = "target"
    template_name = "targets/target_detail.html"
    login_url = "account_login"
    
class target_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"
    login_url = "account_login"

class target_all_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"
    login_url = "account_login"

def assignTargetClass(targetType):
    allwithTT=simbadType.objects.filter(label=targetType)
    firstentry= simbadType.objects.first()
    if firstentry != None: 
        return firstentry.category
    else:
        logger.warning("Type "+targetType+" not found in simbadTypes table")
        return "Unknown"


def target_query(request):
    error_message=""
    if request.method == 'POST':
        Simbad.TIMEOUT = 10 # sets the timeout to 10s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
            if (results_simbad != None):
                df=results_simbad.to_pandas()
                results=df.to_dict('records')
                # Add results to the targets database
                for index, row in df.iterrows():
                    # Figure out the constellation
                    coords=row["RA"]+" "+row["DEC"]
                    c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                    
                    # Add the target record
                    target.objects.create(               
                        userId=request.user.id,
                        targetName = row["MAIN_ID"],
                        catalogIDs = row["MAIN_ID"],
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

class target_update(UpdateView):
    model = target
    form_class = TargetUpdateForm
    template_name = "targets/target_form.html"
    success_url = reverse_lazy('target_all_list')
    
class target_delete(DeleteView):
    model = target
    template_name = "targets/target_confirm_delete.html"
    success_url = reverse_lazy('target_all_list')
