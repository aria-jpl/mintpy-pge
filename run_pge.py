#!/usr/lib/python
import argparse
import os
import subprocess

import pandas as pd
from shapely.geometry import Polygon

# TODO: Clean up code
# TODO: Python docstrings once code is cleaned up

pge_root = '/home/ops/verdi/ops/mintpy-pge'
# pge_root = '/home/parallels/dev/access-mintpy-pge'
wrapper_script_dir = '{}/wrapper_scripts'.format(pge_root)


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


def parse_polygon(_):
    # TODO: implement validation
    return _


def parse_track_number(_):
    # TODO: implement validation
    return _


def parse_date(_):
    # TODO: implement validation
    return _


def verify_dependencies():
    # Verifying if ARIA-tools is installed correctly
    try:
        import ARIAtools.shapefile_util as shputil
    except ImportError as err:
        raise Exception(
            f'ARIA-tools is missing from your PYTHONPATH, has not been installed correctly, or is missing a dependency: {err}')

    # Verifying if Mintpy is installed correctly
    try:
        import numpy as np
        from mintpy import view, tsview, plot_network, plot_transection, plot_coherence_matrix
    except ImportError as err:
        raise Exception(f'Looks like mintPy is not fully installed: {err}')


def get_bbox(kwargs):
    if kwargs.get('bounds') and kwargs.get('polygon'):
        raise Exception('Only one of "--bounds" and "--polygon" may be supplied (both were supplied)')

    if not (kwargs.get('bounds') or kwargs.get('polygon')):
        raise Exception('Either "--bounds" or "--polygon" must be supplied (neither were supplied)')

    if kwargs.get('bounds'):
        bbox = parse_bounds(kwargs.get('bounds'))
    else:

        bbox = parse_polygon(kwargs.get('polygon'))

    return bbox


def polygon_from_frame(frame):
    """
        Create a Shapely polygon from the coordinates of a frame.
    """
    return Polygon([(float(frame['Near Start Lon']), float(frame['Near Start Lat'])),
                    (float(frame['Far Start Lon']), float(frame['Far Start Lat'])),
                    (float(frame['Far End Lon']), float(frame['Far End Lat'])),
                    (float(frame['Near End Lon']), float(frame['Near End Lat']))])


def list_time_series_files(working_dir):
    subprocess.call(['ls', f'{working_dir}/stack'])
    subprocess.call(['ls', f'{working_dir}/DEM/SRTM_3arcsec.dem'])
    subprocess.call(['ls', f'{working_dir}/mask/watermask.msk'])


def main(**kwargs):
    verify_dependencies()

    from ARIAtools.shapefile_util import open_shapefile, shapefile_area

    working_dir = os.path.abspath(os.getcwd())

    bounding_box = get_bbox(kwargs)
    track_number = parse_track_number(kwargs.get('track_number'))
    start_date = parse_date(kwargs.get('start_date'))
    end_date = parse_date(kwargs.get('end_date'))
    use_virtual_download: bool = kwargs.get('virtual_download')

    download = 'url' if use_virtual_download else 'download'
    downloads_dir = os.path.join(working_dir, 'URLproducts' if use_virtual_download else 'products')

    print("Work directory: ", working_dir)
    print("Download: ", download)
    print("Start: ", start_date)
    print("End: ", end_date)
    print("Track: ", track_number)
    print("bbox: ", bounding_box)

    # Download the data products
    subprocess.call(
        [f'{wrapper_script_dir}/download_data_products.sh', track_number, downloads_dir, bounding_box, start_date,
         end_date, download])

    # # Call the DAAC API and retrieve the SLC's outlines

    # checking if bbox exist
    if os.path.exists(os.path.abspath(bounding_box)):
        bounds = open_shapefile(bounding_box, 0, 0).bounds
        w, s, e, n = [str(i) for i in bounds]
    else:
        try:
            s, n, w, e = bounding_box.split()
        except ValueError:
            raise Exception(
                'Cannot understand the --bbox argument. Input string was entered incorrectly or path does not exist.')

    url_base = 'https://api.daac.asf.alaska.edu/services/search/param?'
    url = '{}platform=SENTINEL-1&processinglevel=SLC&beamSwath=IW&output=CSV&maxResults=5000000'.format(url_base)
    url += '&relativeOrbit={}'.format(track_number)
    url += '&bbox=' + ','.join([w, s, e, n])

    # could also include start and end time for period. Needs to be of the form:
    # start=2018-12-15T00:00:00.000Z&end=2019-01-01T23:00:00.000Z

    url = url.replace(' ', '+')
    print(url)

    subprocess.call(["wget", "-O", "test.csv", url])

    track_metadata = pd.read_csv('test.csv', index_col=False)

    # Compute polygons
    slc_polygons = []
    for index, frame in track_metadata.iterrows():
        # Convert frame coords to polygon
        slc_polygons.append(polygon_from_frame(frame))

    # Find union of polygons
    swath_polygon = slc_polygons[0]
    for slc_polygon in slc_polygons:
        swath_polygon = swath_polygon.union(slc_polygon)
    print(swath_polygon)

    # Load the shapefile (shapefile option)
    # bboxRead = json.loads(open('./user_bbox.json').read())
    # bounding_polygon = Polygon(bboxRead['features'][0]['geometry']['coordinates'][0])

    # Convert the bbox in a shapefile (SNWG option)
    frame_bounds = [float(i) for i in bounding_box.split(' ')]
    bounding_polygon = Polygon(
        ([frame_bounds[2], frame_bounds[1]], [frame_bounds[3], frame_bounds[1]], [frame_bounds[3], frame_bounds[0]],
         [frame_bounds[2], frame_bounds[0]]))

    # Load the shapefile (shapefile option)
    # bboxRead = json.loads(open('./user_bbox.json').read())
    # bboxPolygon = Polygon(bboxRead['features'][0]['geometry']['coordinates'][0])

    # TODO use shapely intersect function.
    bounded_swath_polygon = bounding_polygon.intersection(swath_polygon)

    # TODO calculate shapely area.
    minimum_overlap = shapefile_area(bounded_swath_polygon)
    print("Common intersection has an area of %fkm\u00b2" % minimum_overlap)

    # TODO for numerical issue, should make this area threshold a little bit smaller. i.e. 90% or so
    minimum_overlap = minimum_overlap * 0.9
    print("Minimum Area threshold set to 90%" + " or %fkm\u00b2" % minimum_overlap)

    print('Preparing time series using the following arguments:')
    print('Working directory: {}'.format(working_dir))
    print('Downloads directory: {}'.format(downloads_dir))
    print('Bounding-box: {}'.format(bounding_box))
    print('Minimum overlap: {}'.format(minimum_overlap))

    # Prepare the time-series data using ARIA-Tools
    subprocess.call([f'{wrapper_script_dir}/prepare_time_series.sh', working_dir, downloads_dir, bounding_box,
                     str(minimum_overlap)])

    list_time_series_files(working_dir)

    # Run MintPy using the ARIA configuration
    subprocess.call(['smallbaselineApp.py', f'{working_dir}/smallbaselineApp.cfg'])


if __name__ == '__main__':
    args = argument_parser().parse_args()
    main(bounds=args.bounds,
         shape_file=args.shape_file,
         track_number=args.track_number,
         start_date=args.start_date,
         end_date=args.end_date,
         virtual_download=args.virtualdownload)
