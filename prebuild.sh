#!/bin/bash

set -e

rm -rf dist debian-files
mkdir -p debian-files/tmp
python3.11 -m pip install build
python3.11 -m build --wheel
python3.11 -m venv /var/lib/nmexec/venv
/var/lib/nmexec/venv/bin/pip install uv
/var/lib/nmexec/venv/bin/python -m uv pip install dist/*.whl
tar -zcf debian-files/tmp/nmexec.tar.gz /var/lib/nmexec/venv
