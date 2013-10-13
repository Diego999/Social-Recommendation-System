from django.shortcuts import render_to_response

def index(request):
    return render_to_response('main/index.html', {})

def manage(request):
    context = {
        'name': request.session.get('nameFB')
    }
    return render_to_response('main/manage.html', context)
