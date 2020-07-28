#!/usr/lib/python3
import argparse
import os
import subprocess

tutorial_home_dir = os.path.abspath(os.getcwd())
print("Tutorial directory: ", tutorial_home_dir)

# Verifying if ARIA-tools is installed correctly
try:
    import ARIAtools.shapefile_util as shputil
except:
    raise Exception('ARIA-tools is missing from your PYTHONPATH')

# Verifying if Mintpy is installed correctly
# verify if mintpy install is complete:
try:
    import numpy as np
    from mintpy import view, tsview, plot_network, plot_transection, plot_coherence_matrix
except:
    print("Looks like mintPy is not fully installed")

work_dir = os.path.abspath(os.getcwd())

bbox_SNWE = "18.8 20.3 -156.1 -154.8"
bbox_shp = os.path.join(tutorial_home_dir, 'support_docs', 'Big_Island', 'Big_Island.shp')

# Set the bbox to be used in subsequent processing:
bbox = bbox_SNWE

tracknumber = '124'

start = '20181215'
end = '20190101'

# True/False for using virtual data download
virtualDownload = False

# no changes needed below
# Selecting the download option to be used in subsequent processing.
if virtualDownload:
    download = 'url'
    downloadDir = os.path.join(work_dir, 'URLproducts')
else:
    download = 'download'
    downloadDir = os.path.join(work_dir, 'products')

print("Work directory: ", work_dir)
print("Download: ", download)
print("Start: ", start)
print("End: ", end)
print("Track: ", tracknumber)
print("bbox: ", bbox)

# Download the data products
subprocess.call(['./wrapper_scripts/download_data_products.sh', tracknumber, downloadDir, bbox, start, end, download])

## Caling the DAAC API and retrieving the SLCs outlines
# checking if bbox exist
from ARIAtools.shapefile_util import open_shapefile

if os.path.exists(os.path.abspath(bbox)):
    bounds = open_shapefile(bbox, 0, 0).bounds
    W, S, E, N = [str(i) for i in bounds]
else:
    try:
        S, N, W, E = bbox.split()
    except:
        raise Exception(
            'Cannot understand the --bbox argument. Input string was entered incorrectly or path does not exist.')

url_base = 'https://api.daac.asf.alaska.edu/services/search/param?'
url = '{}platform=SENTINEL-1&processinglevel=SLC&beamSwath=IW&output=CSV&maxResults=5000000'.format(url_base)
url += '&relativeOrbit={}'.format(tracknumber)
url += '&bbox=' + ','.join([W, S, E, N])

# could also include start and end time for period. Needs to be of the form:
# start=2018-12-15T00:00:00.000Z&end=2019-01-01T23:00:00.000Z

url = url.replace(' ', '+')
print(url)

subprocess.call(["wget", "-O", "test.csv", url])

import pandas as pd
from ARIAtools.shapefile_util import shapefile_area
from shapely.geometry import Polygon


def polygonFromFrame(frame):
    '''
        Create a Shapely polygon from the coordinates of a frame.
    '''
    P = Polygon([(float(frame['Near Start Lon']), float(frame['Near Start Lat'])),
                 (float(frame['Far Start Lon']), float(frame['Far Start Lat'])),
                 (float(frame['Far End Lon']), float(frame['Far End Lat'])),
                 (float(frame['Near End Lon']), float(frame['Near End Lat']))])
    return P


track_metadata = pd.read_csv('test.csv', index_col=False)

# Compute polygons
SLCPolygons = []
for frameNdx, frame in track_metadata.iterrows():
    # Convert frame coords to polygon
    SLCPolygons.append(polygonFromFrame(frame))

# Find union of polygons
swathPolygon = SLCPolygons[0]
for SLCPolygon in SLCPolygons:
    swathPolygon = swathPolygon.union(SLCPolygon)
print(swathPolygon)

import json

# Convert the bbox in a shapefile (SNWG option)
bboxCoord = [float(i) for i in bbox.split(' ')]
bboxPolygon = Polygon(([bboxCoord[2], bboxCoord[1]], [bboxCoord[3], bboxCoord[1]], [bboxCoord[3], bboxCoord[0]],
                       [bboxCoord[2], bboxCoord[0]]))

# Load the shapefile (shapefile option)
# bboxRead = json.loads(open('./user_bbox.json').read())
# bboxPolygon = Polygon(bboxRead['features'][0]['geometry']['coordinates'][0])


import json

# Convert the bbox in a shapefile (SNWG option)
bboxCoord = [float(i) for i in bbox.split(' ')]
bboxPolygon = Polygon(([bboxCoord[2], bboxCoord[1]], [bboxCoord[3], bboxCoord[1]], [bboxCoord[3], bboxCoord[0]],
                       [bboxCoord[2], bboxCoord[0]]))

# Load the shapefile (shapefile option)
# bboxRead = json.loads(open('./user_bbox.json').read())
# bboxPolygon = Polygon(bboxRead['features'][0]['geometry']['coordinates'][0])


# TODO use shapely intersect function.
bboxSwathPolygon = bboxPolygon.intersection(swathPolygon)

# TODO calculate shapely area.
minOverlap = shapefile_area(bboxSwathPolygon)
print("Common intersection has an area of %fkm\u00b2" % (minOverlap))

# TODO for numerical issue, should make this area threshold a little bit smaller. i.e. 90% or so
minOverlap = minOverlap * 0.9
print("Minimum Area threshold set to 90%" + " or %fkm\u00b2" % (minOverlap))

subprocess.call(['./wrapper_scripts/prepare_time_series.sh', downloadDir, bbox, str(minOverlap)])

subprocess.call(['ls', './stack/*'])
subprocess.call(['ls', './DEM/SRTM_3arcsec'])
subprocess.call(['ls', './mask/watermask.msk'])

# !ls stack/*
# !ls dem/SRTM_3arcsec.dem
# !ls mask/watermask.msk
#
#
# !smallbaselineApp.py -g smallbaselineApp.cfg --dostep load_data
