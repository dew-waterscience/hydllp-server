# hydllp-server

![Status](https://img.shields.io/badge/status-alpha-red.svg)
[![Version](http://img.shields.io/pypi/v/hydllp-server.svg)](https://pypi.python.org/pypi/hydllp-server/)
[![License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kinverarity1/lasio/blob/master/LICENSE)

CherryPy server for the Hydstra HYDLLP executable, written in Python.

If you are just looking for code to access Hydstra directly, you may want to
check out [pyhydllp](https://pypi.org/project/pyhydllp/). That calls the 
HYDLLP DLL directly, and has a lot of helper stuff in pandas.

I wrote this because (1) not all users have access to Hydstra executables
locally on their machines and (2) the DLL code is finicky to get running.

## Install

```posh
> pip install -U hydllp-server
```

## Web app configuration

Create a [TOML](https://github.com/toml-lang/toml) file with the details of your
Hydstra installation:

```toml
hydllpx_exe = 't:\ts_manage\hyd\sys\run\hydllpx.exe'
user = "person"
pwd = "XYZ"
hyaccess = 't:\ts_manage\hyd\hyaccess.ini'
hyconfig = 't:\ts_manage\hyd\prod.local.hyconfig.ini'
```

And the details of how you want your web app served:

```
[cherrypy]
server-socket_host = "0.0.0.0"
server-socket_port = 8096
server-thread_pool = 20
engine-autoreload-on = false
```

These are passed directly to ``cherrypy.config``, with the `-` replaced by `.`.

## Run web app

See `hydllp_server.webapp` for various entry points, including the 
`HYDLLPEndpoint` cherrypy handler, which you can mount anywhere you like.

It can be run as a cherrypy server at `http://server:port/api/` using a variety
of entry points, the simplest of which is the `hydllp-server` executable:

```posh
> hydllp-server hydllp-server-config.toml
[07/May/2019:15:54:24] ENGINE Listening for SIGTERM.
[07/May/2019:15:54:24] ENGINE Bus STARTING
[07/May/2019:15:54:24] ENGINE Set handler for console events.
[07/May/2019:15:54:24] ENGINE Serving on http://127.0.0.1:8080
[07/May/2019:15:54:24] ENGINE Bus STARTED
```

## Client-side use

POST your [HYDLLP-formatted JSON request](http://kisters.com.au/doco/hydllp.htm) 
to the configured endpoint:

```python
>>> import requests
>>> r = requests.post(
    "http://127.0.0.1:8080/api/",
    json={
        "function": "get_site_list", 
        "version": 1, 
        "params": {"site_list": "G7029021*"}
        },
    )
>>> r.json()
{'error_num': 0,
 'buff_required': 402,
 'return': {'sites': ['G702902137',
   'G702902138',
   'G702902139',
   'G702902140',
   'G702902141',
   'G702902142',
   'G702902143',
   'G702902144',
   'G702902145',
   'G702902146',
   'G702902147',
   'G702902148',
   'G702902149',
   'G702902150',
   'G702902151',
   'G702902152',
   'G702902159',
   'G702902160',
   'G702902161',
   'G702902163',
   'G702902164',
   'G702902165',
   'G702902166',
   'G702902168',
   'G702902169']},
 'buff_supplied': 3000}
 ```

The web app will automatically increase the buffer size as required.

## License

MIT
