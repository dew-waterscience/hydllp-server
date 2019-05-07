from setuptools import setup

setup(
    name="hydllp-server",
    version="0.1.0",
    description="CherryPy server for the Hydstra HYDLLPX executable",
    url="https://github.com/kinverarity1/hydllp-server",
    author="Kent Inverarity",
    author_email="kent.inverarity@sa.gov.au",
    packages=["hydllp_server"],
    install_requires=(),
    entry_points={"console_scripts": ["hydllp-server = hydllp_server.webapp:run_entry_point"]},
)
