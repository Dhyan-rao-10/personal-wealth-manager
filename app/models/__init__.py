"""Database table models. Every file in this folder is imported here so its tables get created."""
import importlib
import pkgutil

for _module in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{_module.name}")
