def parent_template(request):
    template = 'base.html'

    if request.user.is_authenticated:
        if request.user.user_type in ['admin', 'superuser']:
            template = 'sidebar.html'

    return {
        'parent_template': template
    }