def social(response, *args, **kwargs):
    user = kwargs['user']
    if user.email:
        user.is_verified_email = True
        user.save()
