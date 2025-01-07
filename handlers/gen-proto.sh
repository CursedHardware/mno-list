#!/bin/bash
set -xeuo pipefail
protoc --proto_path=. --python_out=. --pyi_out=. carrierId.proto
