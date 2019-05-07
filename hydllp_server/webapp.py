import sys

import cherrypy
import json
import toml


def get_hydstra_object(*args, thread_index=0, **kwargs):
    from hydllp_server.hydstra_application import Hydstra

    cherrypy.thread_data.hyd = Hydstra(*args, **kwargs)
    return cherrypy.thread_data.hyd


class HYDLLPEndpoint(object):
    """Web service API endpoint for HYDLLP.

    Args:
        config (dict): configuration for hydllp_server.Hydstra instance

    You can POST JSON to this endpoint, and will receive the HYDLLP JSON
    back.

    See http://kisters.com.au/doco/hydllp.htm for details of the JSON requests
    which you can send.

    """

    def __init__(self, config):
        self.config = config
        self.hyd = get_hydstra_object(**config)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        return self.hyd.request(cherrypy.request.json)


def run(tomlfile=None, hydllp=None, cherrypy_config=None):
    """Run server.

    Args:
        tomlfile (filename or file-like object, optional): configuration file
        hydllp (dict): hydllp_server.Hydstra config
        cherrypy_config (dict): cherrypy server config

    The simplest usage is to pass tomlfile to this function. Otherwise
    you can pass the dictionaries that would otherwise be inside your
    TOML file as the hydllp and cherrypy_config kwargs.

    """
    if hydllp is None:
        hydllp = {}
    if cherrypy_config is None:
        cherrypy_config = {
            "server-socket_host": "127.0.0.1",
            "server-socket_port": 8080,
            "server-thread_pool": 1,
            "engine-autoreload-on": True,
        }

    if tomlfile:
        tomlcfg = toml.load(tomlfile)
        hydllp.update(tomlcfg["hydllp"])
        cherrypy_config.update(tomlcfg["cherrypy"])

    cherrypy.config.update({k.replace("-", "."): v for k, v in cherrypy_config.items()})
    cherrypy.quickstart(HYDLLPEndpoint(hydllp), "/api", {"/": {}})


def run_entry_point():
    run(tomlfile=sys.argv[1])


if __name__ == "__main__":
    run_entry_point()
