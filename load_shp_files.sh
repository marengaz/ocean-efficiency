#!/bin/bash

#################################################
# this script loads all the shape files (*.shp) #
# in a supplied directory into postgis          #
#################################################

dir=$1

if [ ! -d ${dir} ]
then
    echo "Directory ${dir} DOES NOT exists."
    exit
fi

for f in $(find ${dir} -name '*.shp');
do
    filename=$(basename "$f")
    extension="${filename##*.}"
    filename="${filename%.*}"
    psql -U postgres -d ocean_efficiency_geo -c "DROP TABLE IF EXISTS ${filename};"
    shp2pgsql -I -s 4326 ${f} "${filename}" | psql -U postgres -d ocean_efficiency_geo
done
