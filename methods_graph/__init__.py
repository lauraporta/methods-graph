from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("methods-graph")
except PackageNotFoundError:
    # package is not installed
    pass
