#!/bin/bash

PREV_VERSION=$(git describe --tags --abbrev=0)

read -p "Previous version is ${PREV_VERSION} please give new version" NEW_VERSION

git tag -a $NEW_VERSION -m "new version"

FINADDR_BUILD_VERSION=$NEW_VERSION python3 setup.py sdist