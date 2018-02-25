
create DATABASE ocean_efficiency_geo;
\c ocean_efficiency_geo
CREATE EXTENSION postgis;
SELECT postgis_full_version();

shp2pgsql -I -s 4269 /Users/ben.marengo/other_code/oceanefficiency_data/World_EEZ_v10_20180221/eez_boundaries_v10.shp eez_boundaries | psql -U postgres -d ocean_efficiency_geo

In mapping frameworks spatial coordinates are often in order of latitude and longitude. In spatial databases spatial coordinates are in x = longitude, and y = latitude.


### prj file to srid
http://prj2epsg.org/search












