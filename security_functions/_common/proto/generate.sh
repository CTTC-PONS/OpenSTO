#!/bin/bash -eu

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

touch __init__.py

# Generate Python code
python3 -m grpc_tools.protoc -I=./ --python_out=./ --grpc_python_out=./ --pyi_out=./ *.proto

# Arrange generated code imports to enable imports from arbitrary subpackages
find . -type f -iname "*.py" -exec sed -i -E 's/^(import\ .*)_pb2/from . \1_pb2/g' {} \;
