from django.conf import settings
from django.utils.module_loading import import_string


class ProviderRegistry:
    """Registry of integration provider instances keyed by provider key."""

    def __init__(self):
        self._providers = {}
        self._discovered = False

    def register(self, provider):
        self._providers[provider.key] = provider

    def get_provider(self, key):
        return self._providers.get(key)

    def get_all_providers(self):
        return list(self._providers.values())

    def autodiscover(self):
        if self._discovered:
            return
        self._discovered = True
        provider_paths = getattr(settings, 'INTEGRATION_PROVIDERS', [])
        for dotted_path in provider_paths:
            provider_cls = import_string(dotted_path)
            self.register(provider_cls())


registry = ProviderRegistry()
