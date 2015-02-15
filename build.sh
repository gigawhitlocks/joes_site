#!/bin/bash
rm -rf output/;
mkdir -p output;
for asset_dir in $(ls assets -1); do
    ln -s $(pwd)/assets/"$asset_dir" $(pwd)/output/"$asset_dir"
done

for template in $(ls templates -1); do
	python generator/generate_site.py "$template" > output/"$template";
	python generator/generate_site.py "$template" --upload
done
