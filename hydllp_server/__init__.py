from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from hydllp_server.hydllpx import execute_hydllpx
from hydllp_server.hydstra_application import Hydstra
