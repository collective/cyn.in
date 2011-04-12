#/bin/bash
files=`find . -type f -iname "*.gif" -o -iname "*.jpg" -o -iname "*.ico" -o -iname "*.png"`

for file in $files; do
    echo "[default]" > ${file}.metadata
    echo "cache=HTTPCache" >> ${file}.metadata
done

