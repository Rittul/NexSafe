# from django.apps import AppConfig


# class AuthenticationConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'authentication'


from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        import authentication.models  # Import to register signals
