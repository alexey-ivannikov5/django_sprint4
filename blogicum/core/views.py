from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)


def server_error(request, exception):
    return render(request, 'core/500.html', status=500)


def csrf_failure(request):
    return render(request, 'core/403csrf.html', status=403)
