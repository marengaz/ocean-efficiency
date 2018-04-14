from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Float, SmallInteger, Sequence, DateTime
from geoalchemy2 import Geometry

Base = declarative_base()


class EEZ12(Base):
    __tablename__ = 'eez_12nm_v2'
    gid = Column(Integer, primary_key=True)
    mrgid = Column(BigInteger)
    geoname = Column(String(254))
    pol_type = Column(String(254))
    mrgid_ter1 = Column(BigInteger)
    territory1 = Column(String(254))
    mrgid_sov1 = Column(BigInteger)
    sovereign1 = Column(String(254))
    iso_ter1 = Column(String(254))
    x_1 = Column(Float)
    y_1 = Column(Float)
    mrgid_eez = Column(BigInteger)
    area_km2 = Column(Float)
    geom = Column(Geometry('MultiPolygon', srid=4326))


class WorldBorders(Base):
    __tablename__ = 'tm_world_borders_v03'
    gid = Column(Integer, primary_key=True)
    fips = Column(String(2))
    iso2 = Column(String(2))
    iso3 = Column(String(3))
    un = Column(SmallInteger)
    name = Column(String(50))
    area = Column(Integer)
    pop2005 = Column(BigInteger)
    region = Column(SmallInteger)
    subregion = Column(SmallInteger)
    lon = Column(Float)
    lat = Column(Float)
    geom = Column(Geometry('MultiPolygon', srid=4326))


class Journey(Base):
    __tablename__ = 'journey'
    journey_id = Column(Integer, Sequence('journey_id_seq'), primary_key=True)
    name = Column(String(100))
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    geom = Column(Geometry('CompoundCurve', srid=4326))  # , index=True)



"""
create table journey
(
	journey_id serial not null primary key ,
	geom geometry(COMPOUNDCURVE, 4326)
)
;

create index journey_geom_idx
	on journey (geom)
;
"""



"""
create table eez_24nm_v2
(
	gid serial not null
		constraint eez_24nm_v2_pkey
			primary key,
	mrgid bigint,
	geoname varchar(254),
	pol_type varchar(254),
	mrgid_ter1 bigint,
	territory1 varchar(254),
	mrgid_sov1 bigint,
	sovereign1 varchar(254),
	iso_ter1 varchar(254),
	x_1 numeric,
	y_1 numeric,
	mrgid_eez bigint,
	area_km2 bigint,
	geom geometry(MultiPolygon,4326)
)
;

create index eez_24nm_v2_geom_idx
	on eez_24nm_v2 (geom)
;

create table eez_archipelagic_waters_v2
(
	gid serial not null
		constraint eez_archipelagic_waters_v2_pkey
			primary key,
	mrgid bigint,
	geoname varchar(254),
	pol_type varchar(254),
	mrgid_ter1 bigint,
	territory1 varchar(254),
	mrgid_sov1 bigint,
	sovereign1 varchar(254),
	iso_ter1 varchar(254),
	x_1 numeric,
	y_1 numeric,
	mrgid_eez bigint,
	area_km2 bigint,
	geom geometry(MultiPolygon,4326)
)
;

create index eez_archipelagic_waters_v2_geom_idx
	on eez_archipelagic_waters_v2 (geom)
;

create table eez_boundaries_v10
(
	gid serial not null
		constraint eez_boundaries_v10_pkey
			primary key,
	line_id bigint,
	line_name varchar(254),
	line_type varchar(254),
	mrgid_sov1 bigint,
	mrgid_ter1 bigint,
	territory1 varchar(254),
	sovereign1 varchar(254),
	mrgid_ter2 bigint,
	territory2 varchar(254),
	mrgid_sov2 bigint,
	sovereign2 varchar(254),
	mrgid_eez1 bigint,
	eez1 varchar(254),
	mrgid_eez2 bigint,
	eez2 varchar(254),
	source1 varchar(254),
	url1 varchar(254),
	source2 varchar(254),
	url2 varchar(254),
	source3 varchar(254),
	url3 varchar(254),
	origin varchar(254),
	doc_date date,
	mrgid_jreg bigint,
	joint_reg varchar(254),
	length_km bigint,
	geom geometry(MultiLineString,4326)
)
;

create index eez_boundaries_v10_geom_idx
	on eez_boundaries_v10 (geom)
;

create table eez_v10
(
	gid serial not null
		constraint eez_v10_pkey
			primary key,
	mrgid bigint,
	geoname varchar(254),
	mrgid_ter1 bigint,
	pol_type varchar(254),
	mrgid_sov1 bigint,
	territory1 varchar(254),
	iso_ter1 varchar(254),
	sovereign1 varchar(254),
	mrgid_ter2 bigint,
	mrgid_sov2 bigint,
	territory2 varchar(254),
	iso_ter2 varchar(254),
	sovereign2 varchar(254),
	mrgid_ter3 bigint,
	mrgid_sov3 bigint,
	territory3 varchar(254),
	iso_ter3 varchar(254),
	sovereign3 varchar(254),
	x_1 numeric,
	y_1 numeric,
	mrgid_eez bigint,
	area_km2 bigint,
	geom geometry(MultiPolygon,4326)
)
;

create index eez_v10_geom_idx
	on eez_v10 (geom)
;

create table eez_internal_waters_v2
(
	gid serial not null
		constraint eez_internal_waters_v2_pkey
			primary key,
	mrgid bigint,
	geoname varchar(254),
	pol_type varchar(254),
	mrgid_ter1 bigint,
	territory1 varchar(254),
	mrgid_sov1 bigint,
	sovereign1 varchar(254),
	iso_ter1 varchar(254),
	x_1 numeric,
	y_1 numeric,
	mrgid_eez bigint,
	area_km2 bigint,
	geom geometry(MultiPolygon,4326)
)
;

create index eez_internal_waters_v2_geom_idx
	on eez_internal_waters_v2 (geom)
;

create table meow_ecos
(
	gid serial not null
		constraint meow_ecos_pkey
			primary key,
	eco_code numeric,
	ecoregion varchar(50),
	prov_code numeric,
	province varchar(40),
	rlm_code numeric,
	realm varchar(40),
	alt_code numeric,
	eco_code_x numeric,
	lat_zone varchar(10),
	geom geometry(MultiPolygon,4326)
)
;

create index meow_ecos_geom_idx
	on meow_ecos (geom)
;
"""















