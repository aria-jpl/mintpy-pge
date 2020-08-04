#!/usr/lib/python
import argparse
import os
import subprocess


# TODO: Clean up code
# TODO: Python docstrings once code is cleaned up

def argument_parser():
    parse = argparse.ArgumentParser(description='Run MintPy with given parameters')
    parse.add_argument('-b', '--bounds',
                       required=False,
                       default=None,
                       help='Space-separated latitude/longitude bounds in order S, N, W, E',
                       dest='bounds')
    parse.add_argument('-f', '--shapefile',
                       required=False,
                       default=None,
                       help='Bounding-box shape file path',
                       dest='shape_file')
    parse.add_argument('-t', '--tracknumber',
                       required=True,
                       default=None,
                       help='Sentinel track number',
                       dest='track_number')
    parse.add_argument('-s', '--start',
                       required=True,
                       default=None,
                       help='Start date (YYYYMMDD)',
                       dest='start_date')
    parse.add_argument('-e', '--end',
                       required=True,
                       default=None,
                       help='End date (YYYYMMDD)',
                       dest='end_date')
    parse.add_argument('-v', '--virtualdownload',
                       help='Enable virtual download to avoid unnecessary data transfer',
                       action='store_true')
    return parse



def parse_bounds(_):
    # TODO: implement validation
    return _


def parse_shape_file(_):
    # TODO: implement validation
    return _


def parse_track_number(_):
    # TODO: implement validation
    return _


def parse_date(_):
    # TODO: implement validation
    return _


def main(**kwargs):
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

    if kwargs.get('bounds') and kwargs.get('shape_file'):
        raise Exception('Only one of "--bounds" and "--shapefile" may be supplied (both were supplied)')

    if not (kwargs.get('bounds') or kwargs.get('shape_file')):
        raise Exception('Either "--bounds" or "--shapefile" must be supplied (neither were supplied)')

    if kwargs.get('bounds'):
        bbox = parse_bounds(kwargs.get('bounds'))
    else:

        bbox = parse_shape_file(kwargs.get('shape_file'))

    tracknumber = parse_track_number(kwargs.get('track_number'))

    start = parse_date(kwargs.get('start_date'))
    end = parse_date(kwargs.get('end_date'))

    # True/False for using virtual data download
    virtualDownload = kwargs.get('virtual_download')

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
    subprocess.call(
        ['./wrapper_scripts/download_data_products.sh', tracknumber, downloadDir, bbox, start, end, download])

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

    # Prepare the time-series data using ARIA-Tools
    subprocess.call(['./wrapper_scripts/prepare_time_series.sh', downloadDir, bbox, str(minOverlap)])

    subprocess.call(['ls', './stack'])
    subprocess.call(['ls', './DEM/SRTM_3arcsec.dem'])
    subprocess.call(['ls', './mask/watermask.msk'])

    # Run MintPy using the ARIA configuration
    subprocess.call(['smallbaselineApp.py', './smallbaselineApp.cfg'])


if __name__ == '__main__':
    args = argument_parser().parse_args()
    main(bounds=args.bounds,
         shape_file=args.shape_file,
         track_number=args.track_number,
         start_date=args.start_date,
         end_date=args.end_date,
         virtual_download=args.virtualdownload)
