# filepath: /home/gtulloch/obsy.dev/config/views.py
from django.shortcuts import render, redirect
from .forms import GeneralConfigForm, CommunicationsConfigForm, RepositoryConfigForm
from .models import GeneralConfig, CommunicationsConfig, RepositoryConfig

def config_view(request):
    # Fetch or create the first record for each configuration model with default values
    general_config, created = GeneralConfig.objects.get_or_create(
        id=1,
        defaults={'latitude': 0.0, 'longitude': 0.0, 'elevation': 0}
    )
    communications_config, created = CommunicationsConfig.objects.get_or_create(
        id=1,
        defaults={
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
            'email_host': 'smtp.gmail.com',
            'email_port': 587,
            'email_use_tls': True,
            'email_host_user': 'email@gmail.com',
            'email_host_password': 'secret',
            'sender_email': 'email@gmail.com',
            'recipient_email': 'email@gmail.com',
        }
    )
    repository_config, created = RepositoryConfig.objects.get_or_create(
        id=1,
        defaults={
            'ppsourcepath': '/home/gtulloch/REPOSITORY.Incoming',
            'pprepopath': '/home/gtulloch/REPOSITORY'
        }
    )
    general_form = GeneralConfigForm(request.POST, instance=general_config, prefix='general')
    communications_form = CommunicationsConfigForm(request.POST, instance=communications_config, prefix='communications')
    repository_form = RepositoryConfigForm(request.POST, instance=repository_config, prefix='repository')

    if request.method == 'POST':
        if general_form.is_valid():
            general_form.save()
        if communications_form.is_valid():
            communications_form.save()
        if repository_form.is_valid():            
            repository_form.save()
        return redirect('config_view')
    else:
        general_form = GeneralConfigForm(instance=general_config, prefix='general')
        communications_form = CommunicationsConfigForm(instance=communications_config, prefix='communications')
        repository_form = RepositoryConfigForm(instance=repository_config, prefix='repository')

    return render(request, 'config/config.html', {
        'general_form': general_form,
        'communications_form': communications_form,
        'repository_form': repository_form
    })