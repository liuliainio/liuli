#!/bin/bash
rm -rf ./MarketSearch/
thrift --gen py:new_style links.thrift
thrift --gen py:new_style apkpatch.thrift
cp -r ./gen-py/MarketSearch/ .
rm -rf ./gen-py/

