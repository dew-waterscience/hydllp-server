import logging
import json
import os
import subprocess
import tempfile


logger = logging.getLogger(__name__)


def execute_hydllpx(
    json_request, hydllpx_exe, user, pwd, hyaccess, hyconfig, buff=3000
):
    """Run HYDLLPX.EXE. See Hydstra documentation for more details."""
    input_handle, input_filename = tempfile.mkstemp(suffix=".json")
    output_handle, output_filename = tempfile.mkstemp(suffix=".json")

    with open(input_filename, "w") as in_f:
        json.dump(json_request, in_f)

    with open(input_filename, "r") as in_f:
        with open(output_filename, "w") as out_f:
            folder, exe = os.path.split(hydllpx_exe)
            args = [
                exe,
                r"/u=" + user,
                r"/p=" + pwd,
                r"/hyaccess=" + hyaccess,
                r"/hyconfig=" + hyconfig,
                "/b=3000",
            ]
            p = subprocess.call(args, stdin=in_f, stdout=out_f, cwd=folder)
    with open(output_filename, "r") as f:
        result = json.loads(f.read())

    if result["buff_required"] > result["buff_supplied"]:
        return execute_hydllpx(
            json_request,
            hydllpx_exe,
            user,
            pwd,
            hyaccess,
            hyconfig,
            buff=result["buff_required"],
        )

    return result
