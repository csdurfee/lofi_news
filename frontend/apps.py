from django.apps import AppConfig


class FrontendConfig(AppConfig):
    name = 'frontend'

    def ready(self):
        """
        registers signals for frontend.models
        """
        import frontend.models # noqa: F401
