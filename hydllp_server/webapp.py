from datetime import datetime
import sys
import io
import traceback

import json
import pandas as pd
import toml
from fastapi import FastAPI, Body, Query, Path, Response
from typing import List
import pandas as pd

from hydllp_server.hydstra_application import Hydstra


hyd = Hydstra(
    r"E:\Telemetry\kinverarity\dew-deployment-tools\services\hydllp-server\config.toml"
)


app = FastAPI()


@app.post("/hydllp")
def hydllp(json_request: dict):
    """Send a JSON call to hydllpx.exe.

    See <a href="http://kisters.com.au/doco/hydllp.htm">http://kisters.com.au/doco/hydllp.htm</a> for more details.

    """
    return hyd.request(json_request)


@app.get("/sites")
def get_site_list(site_list: str = "*"):
    return hyd.request(
        {"function": "get_site_list", "version": 1, "params": {"site_list": site_list}}
    )


@app.get("/sites/{site_list}/traces")
def get_ts_traces(
    site_list: str = Path(
        ...,
        description="Hydstra site list expression, you can use * or also separate with commas e.g. A5031001,A5031002",
    ),
    start_time: datetime = Query(
        None,
        description="Start time in YYYY-MM-DD HH:MM:SS format. If you enter a start time you must also enter an end time.",
    ),
    end_time: datetime = Query(
        None,
        description="End time in YYYY-MM-DD HH:MM:SS format. If you enter an end time you must also enter a start time.",
    ),
    varfrom: str = Query(
        "",
        description="Hydstra variable to calculate from (only use for data transformation)",
    ),
    varto: str = Query(
        "",
        description="Hydstra variable to calculate to (only use for data transformation)",
    ),
    var_list: str = Query(
        "114.00",
        description="Hydstra variable list e.g. 10.00 rainfall, 100.00 water level, 114.00 DTW",
    ),
    interval: str = Query(
        "day",
        description=(
            "Period to aggregate over (ignored if data_type='point', "
            "valid options are 'year, month, day, hour, minute, second, period'"
        ),
    ),
    multiplier: int = Query(
        1,
        description="Multiplier for interval i.e. if interval == 'minute' and multiplier == 10 you'll get data every 10 minutes.",
    ),
    report_time: str = "end",
    offset: int = 0,
    datasource: str = Query(
        "A", description="Hydstra datasources to use - either A or TELEM"
    ),
    data_type: str = Query(
        "point",
        description=(
            "Aggregation method - use 'point' to return each measurement. "
            "Other options are mean, maxmin, max, min, start, end, first, last, tot, partialtot, cum"
        ),
    ),
    match_comment: str = "",
    rel_times: bool = False,
    compressed: bool = False,
    return_format: str = Query("json", description="Return as 'json' or as 'csv'"),
    # rounding: - TBA
):
    """Retrieves one or more time series traces.

    See <a href='http://kisters.com.au/doco/hydllp.htm#get_ts_traces'>http://kisters.com.au/doco/hydllp.htm#get_ts_traces</a> for more details.

    """
    if start_time:
        start_time = start_time.strftime("%Y%m%d%H%M%S")
    else:
        start_time = 0
    if end_time:
        end_time = end_time.strftime("%Y%m%d%H%M%S")
    else:
        end_time = 0
    if start_time == 0:
        assert end_time == 0
    elif end_time == 0:
        assert start_time == 0
    rel_times = 1 if rel_times else 0
    compressed = 1 if compressed else 0
    params = {
        "site_list": site_list,
        "start_time": start_time,
        "end_time": end_time,
        "interval": interval,
        "multiplier": multiplier,
        "report_time": report_time,
        "offset": offset,
        "datasource": datasource,
        "data_type": data_type,
        "match_comment": match_comment,
        "rel_times": rel_times,
        "compressed": compressed,
    }
    if varfrom and varto:
        params.update({"varfrom": varfrom, "varto": varto})
    else:
        params.update({"var_list": var_list})
    result = hyd.request({"function": "get_ts_traces", "version": 2, "params": params})
    if return_format == "json":
        return result
    elif return_format == "csv":
        try:
            df = pd.io.json.json_normalize(
                result["return"], ["traces", "trace"], [["traces", "site"]]
            )
            df["t"] = pd.to_datetime(df.t, format="%Y%m%d%H%M%S")
            df = df.rename(
                columns={
                    "traces.site": "station",
                    "t": "timestamp",
                    "d": "datatrans",
                    "q": "quality_code",
                    "v": "value",
                }
            )
            # short_name = df["traces.site_details.short_name"].iloc[0]
            site = df["station"].iloc[0]
            df = df[["station", "timestamp", "value", "quality_code", "datatrans"]]
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return Response(
                content=buffer.read(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment;filename="trace-{site}.csv"'
                },
            )
        except:
            return Response(content=str(traceback.format_exc()))


@app.get("/sites/{site_list}/geojson")
def get_site_geojson(
    site_list: str = Path(..., description="Hydstra site list expression"),
    get_elev: bool = True,
    fields: List[str] = None,
):
    get_elev = 1 if get_elev else 0
    if not fields:
        fields = []
    return hyd.request(
        {
            "function": "get_site_geojson",
            "version": 2,
            "params": {"site_list": site_list, "get_elev": get_elev, "fields": fields},
        }
    )


@app.get("/sites/{site_list}/variables")
def get_variable_list(
    site_list: str = Path(..., description="Hydstra site list expression"),
    datasource: str = Query("A", description="Hydstra datasources to use"),
):
    return hyd.request(
        {
            "function": "get_variable_list",
            "version": 1,
            "params": {"site_list": site_list, "datasource": datasource},
        }
    )


@app.get("/sites/{site_list}/subvariables")
def get_subvar_details(
    site_list: str = Path(..., description="Hydstra site list expression"),
    variable: str = Query(..., description="Variable and subvariable e.g. 100.01"),
):
    return hyd.request(
        {
            "function": "get_subvar_details",
            "version": 1,
            "params": {"site_list": site_list, "variable": variable},
        }
    )


@app.get("/sites/{site_list}/blocks")
def get_ts_blockinfo(
    site_list: str = Path(..., description="Hydstra site list expression"),
    datasources: List[str] = Query(
        ["A", "TELEM"], description="Datasource codes either A or TELEM"
    ),
    variables: List[str] = Query(None, description="Variables"),
    # variables: str = "",
    starttime: datetime = Query(
        None, description="Start time in YYYY-MM-DD HH:MM:SS format"
    ),
    endtime: datetime = Query(
        None, description="End time in YYYY-MM-DD HH:MM:SS format"
    ),
    start_modified: datetime = Query(
        None, description="Start modified time in YYYY-MM-DD HH:MM:SS format"
    ),
    end_modified: datetime = Query(
        None, description="End modified time in YYYY-MM-DD HH:MM:SS format"
    ),
    fill_gaps: bool = Query(
        False,
        description="a boolean value used to request gaps returned as blocks with the block being marked as a gap",
    ),
    auditinfo: bool = False,
):
    if starttime:
        starttime = starttime.strftime("%Y%m%d%H%M%S")
    else:
        starttime = 0
    if endtime:
        endtime = endtime.strftime("%Y%m%d%H%M%S")
    else:
        endtime = 0
    if start_modified:
        start_modified = start_modified.strftime("%Y%m%d%H%M%S")
    else:
        start_modified = 0
    if end_modified:
        end_modified = end_modified.strftime("%Y%m%d%H%M%S")
    else:
        end_modified = 0
    fill_gaps = 1 if fill_gaps else 0
    auditinfo = 1 if auditinfo else 0
    params = {
        "site_list": site_list,
        "datasources": datasources,
        "variables": variables,
        "fill_gaps": fill_gaps,
        "auditinfo": auditinfo,
    }
    if starttime != 0:
        params["starttime"] = starttime
    if endtime != 0:
        params["endtime"] = endtime
    if start_modified != 0:
        params["start_modified"] = start_modified
    if end_modified != 0:
        params["end_modified"] = end_modified
    return hyd.request({"function": "get_ts_blockinfo", "version": 2, "params": params})

