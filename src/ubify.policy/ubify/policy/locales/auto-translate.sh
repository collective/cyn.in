#!/bin/bash
files=`find . -type f -iname "*.po"`

for file in $files; do
    lang=${file:8:2}
    echo ./googtext.py $file en $file $lang
    ./googtext.py $file en $file $lang
done
