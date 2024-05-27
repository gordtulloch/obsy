# targets/views.py
from django.views.generic import ListView
import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from .models import target
from setup.models import objectsCatalog
import logging

logger = logging.getLogger("targets.views")

class target_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_list.html"

class target_all_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"

def assignTargetClass(targetType)
    return "VS"

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
                    target.objects.create(
                    #                       TARGET_TYPES=(
                    #       ("VS", "Variable Star"),
                    #       ("EX", "Exoplanet"),
                    #       ("DS", "Deep Sky Object"),
                    #       ("PL", "Planet"),
                    #       ("LU", "Luna"),
                    #       ("SU", "Sun"),
                    #       ("SA", "Satellite"),
                    #       ("OT", "Other")
                    #   )                   
                        userId=request.user.id,
                        targetName = row["MAIN_ID"],
                        catalogIDs = "",
                        targetType  =row["OTYPE_main"],
                        targetClass=assignTargetClass(targetType)
                        objID = "",
                        objName = "",
                        objRA2000 = row["RA"],
                        objDec2000 = row["DEC"],
                        objConst = "",
                        objMag = row["FLUX_V"],
                        objSize = "",
                        objType = "",
                        objClass = "",
                        objCatalogs = "",
                        )
            else: 
                results=[]
            return render(request, 'targets/target_result.html',{'results': results})
        except astroquery.exceptions.TableParseError as ex:
            error_message="Search Error occurred with search ("+search_term+" error: "+ex
            logger.error(error_message)
            return render(request, 'targets/target_search.html',{'error': error_message})
        """except astroquery.exceptions.TableParseError as ex:
            error_message=ex
            logger.warning(Simbad.last_response)"""
    else:
        return render(request, 'targets/target_search.html',{'error': error_message})

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
