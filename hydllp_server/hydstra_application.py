import toml

from hydllp_server.hydllpx import execute_hydllpx


class Hydstra:
    """Represent an installation of Hydstra.

    Args:
        f (filename or file-like object, optional): path to a TOML file
            which contains the config.

    Attributes:
        config (dict): Contains the details of a Hydstra installation,
            for example:

                {'hydllpx_exe': 't:\\ts_manage\\hyd\\sys\\run\\hydllpx.exe',
                 'user': 'guest0',
                 'pwd': 'water',
                 'hyaccess': 't:\\ts_manage\\hyd\\hyaccess.ini',
                 'hyconfig': 't:\\ts_manage\\hyd\\prod.local.hyconfig.ini'}
    
    """

    def __init__(self, f=None, **kwargs):
        if not f is None:
            self.config = toml.load(f)["hydllp"]
        else:
            self.config = kwargs

    def request(self, json_request):
        """Execute a hydllp call via the Hydstra installation referenced
        by the config attribute.

        Args:
            json_request (dict): JSON request

        See the source of :func:`hydllp_server.hydllpx.execute_hydllpx` for
        details of the actual command executed.

        See http://kisters.com.au/doco/hydllp.htm for details of the
        requests you can send to HYDLLP.

        """
        return execute_hydllpx(json_request, **self.config)
