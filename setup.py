from setuptools import setup

setup(
    name="hydllp-server",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Simple FastAPI interface to the HYDLLP executable shipped with Hydstra",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dew-waterscience/hydllp-server",
    author="Kent Inverarity",
    author_email="kent.inverarity@sa.gov.au",
    packages=["hydllp_server"],
    install_requires=("pandas", "fastapi", "uvicorn"),
    entry_points={
        "console_scripts": ["hydllp-server = hydllp_server.webapp:run_entry_point"]
    },
)
