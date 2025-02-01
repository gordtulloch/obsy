# filepath: /home/gtulloch/obsy.dev/config/views.py
from django.shortcuts import render, redirect
from .forms import GeneralConfigForm, CommunicationsConfigForm, RepositoryConfigForm
from .models import GeneralConfig, CommunicationsConfig, RepositoryConfig

def config_view(request):
    # Fetch or create the first record for each configuration model with default values
    general_config = GeneralConfig.objects.first()
    if general_config is None:
        general_config = GeneralConfig.objects.create(
            latitude=0.0,
            longitude=0.0,
            elevation=0
        )

    # Get first CommunicationsConfig record
    communications_config = CommunicationsConfig.objects.first()
    if communications_config is None:
        communications_config = CommunicationsConfig.objects.create(
            email_host='smtp.gmail.com',
            email_port=587,
            email_use_tls=True,
            email_host_user='email@gmail.com',
            email_host_password='secret',
            sender_email='email@gmail.com',
            recipient_email='email@gmail.com',
        )

    repository_config = RepositoryConfig.objects.first()
    if repository_config is None:
        repository_config = RepositoryConfig.objects.create(
            ppsourcepath='/home/user/REPOSITORY.Incoming',
            pprepopath='/home/user/REPOSITORY'
        )

    # Initialize the forms with the fetched or created records
    general_form = GeneralConfigForm(request.POST, instance=general_config, prefix='general')
    communications_form = CommunicationsConfigForm(request.POST, instance=communications_config, prefix='communications')
    repository_form = RepositoryConfigForm(request.POST, instance=repository_config, prefix='repository')

    if request.method == 'POST':
        # Reinitialize the forms with the POST data
        general_form = GeneralConfigForm(request.POST, instance=general_config, prefix='general')
        communications_form = CommunicationsConfigForm(request.POST, instance=communications_config, prefix='communications')
        repository_form = RepositoryConfigForm(request.POST, instance=repository_config, prefix='repository')

        # Save the forms if they are valid
        if general_form.is_valid():
            general_form.save()
        if communications_form.is_valid():
            communications_form.save()
        if repository_form.is_valid():
            repository_form.save()
        return redirect('config_view')
    else:
        # Reinitialize the forms with the fetched or created records
        general_form = GeneralConfigForm(instance=general_config, prefix='general')
        communications_form = CommunicationsConfigForm(instance=communications_config, prefix='communications')
        repository_form = RepositoryConfigForm(instance=repository_config, prefix='repository')

    return render(request, 'config/config.html', {
        'general_form': general_form,
        'communications_form': communications_form,
        'repository_form': repository_form
    })