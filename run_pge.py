#!/usr/lib/python
import argparse
from datetime import datetime
import glob
import itertools
import json
import os
import subprocess
from typing import List

import pandas as pd
from shapely.geometry import Polygon

# TODO: Clean up code
# TODO: Python docstrings once code is cleaned up
from Dataset import Dataset
from RunConfig import RunConfig


def argument_parser():
    parse = argparse.ArgumentParser(description='Run MintPy with given parameters')
    parse.add_argument('-b', '--bounds',
                       required=False,
                       default=None,
                       help='Space-separated latitude/longitude bounds in order S, N, W, E',
                       dest='bounds')
    parse.add_argument('-c', '--polygonfromcontext',
                       required=False,
                       default=None,
                       help='Use geoJSON from _context.json "polygon" parameter',
                       action='store_true')
    parse.add_argument('-t', '--tracknumber',
                       required=True,
                       default=None,
                       help='Sentinel track number',
                       dest='track_number')
    parse.add_argument('-s', '--start',
                       required=True,
                       default=None,
                       help='Start date (YYYY-MM-DD)',
                       dest='start_date')
    parse.add_argument('-e', '--end',
                       required=True,
                       default=None,
                       help='End date (YYYY-MM-DD)',
                       dest='end_date')
    parse.add_argument('-v', '--virtualdownload',
                       help='Enable virtual download to avoid unnecessary data transfer',
                       action='store_true')
    parse.add_argument('--pgeroot',
                       required=False,
                       default=None,
                       help='PGE root directory',
                       dest='pge_root')

    return parse


def verify_dependencies() -> None:
    # Verifying if ARIA-tools is installed correctly
    try:
        import ARIAtools.shapefile_util as shputil
    except ImportError as err:
        raise Exception(
            f'ARIA-tools is missing from your PYTHONPATH, has not been installed correctly, '
            f'or is missing a dependency: {err}')

    # Verifying if Mintpy is installed correctly
    try:
        import numpy as np
        from mintpy import view, tsview, plot_network, plot_transection, plot_coherence_matrix
    except ImportError as err:
        raise Exception(f'Looks like mintPy is not fully installed: {err}')


def download_raw_products(run_config: RunConfig) -> None:
    subprocess.call([
        f'{run_config.wrapper_script_dir}/download_data_products.sh',
        str(run_config.track_number),
        run_config.downloads_dir,
        run_config.bounding_geojson_filename,
        run_config.start_date.strftime("%Y%m%d"),
        run_config.end_date.strftime("%Y%m%d"),
        run_config.download_mode
    ])


def verify_successful_download():
    downloaded_product_count = len(glob.glob('products/*.nc')) > 0
    if downloaded_product_count < 1:
        raise RuntimeError("Failed to download any inteferograms from ASF")


def get_track_metadata(track_number: int, bounds):
    west_bound, south_bound, east_bound, north_bound = [str(bound) for bound in bounds]

    url_base = 'https://api.daac.asf.alaska.edu/services/search/param?'
    url = '{}platform=SENTINEL-1&processinglevel=SLC&beamSwath=IW&output=CSV&maxResults=5000000'.format(url_base)
    url += '&relativeOrbit={}'.format(track_number)
    url += '&bbox=' + ','.join([west_bound, south_bound, east_bound, north_bound])

    # could also include start and end time for period. Needs to be of the form:
    # start=2018-12-15T00:00:00.000Z&end=2019-01-01T23:00:00.000Z

    url = url.replace(' ', '+')
    print(url)

    subprocess.call(["wget", "-O", "test.csv", url])

    return pd.read_csv('test.csv', index_col=False)


def get_slc_polygons(track_metadata) -> List[Polygon]:
    slc_polygons = []
    for index, frame in track_metadata.iterrows():
        # Convert frame coords to polygon
        slc_polygons.append(polygon_from_frame(frame))
    return slc_polygons


def polygon_from_frame(frame) -> Polygon:
    """
        Create a Shapely polygon from the coordinates of a frame.
    """
    return Polygon([(float(frame['Near Start Lon']), float(frame['Near Start Lat'])),
                    (float(frame['Far Start Lon']), float(frame['Far Start Lat'])),
                    (float(frame['Far End Lon']), float(frame['Far End Lat'])),
                    (float(frame['Near End Lon']), float(frame['Near End Lat']))])


def get_bounded_swath_polygon(track_number: int, bounding_geojson_filename: str) -> Polygon:
    """Returns the intersection of all SLC polygons and the bounding polygon"""
    from ARIAtools.shapefile_util import open_shapefile

    # Call the DAAC API and retrieve the SLC's outlines
    bounds = open_shapefile(bounding_geojson_filename, 0, 0).bounds
    track_metadata = get_track_metadata(track_number, bounds)

    # Compute polygons
    slc_polygons = get_slc_polygons(track_metadata)

    swath_polygon = slc_polygons[0]
    for slc_polygon in slc_polygons:
        swath_polygon = swath_polygon.union(slc_polygon)

    with open(bounding_geojson_filename) as bounding_geojson:
        bounding_polygon = Polygon(json.load(bounding_geojson)['features'][0]['geometry']['coordinates'][0])

    return bounding_polygon.intersection(swath_polygon)


def get_minimum_overlap(bounded_swath_polygon: Polygon) -> float:
    from ARIAtools.shapefile_util import shapefile_area

    overlap_area = shapefile_area(bounded_swath_polygon)
    print("Common intersection has an area of %fkm\u00b2" % overlap_area)

    # Due to numerical issue (floating point error?), reduce threshold to 90%
    minimum_overlap = overlap_area * 0.9
    print("Minimum Area threshold set to 90%" + " or %fkm\u00b2" % minimum_overlap)

    return minimum_overlap


def prepare_time_series(run_config: RunConfig) -> None:
    print('Calculating minimum_overlap...')
    bounded_swath_polygon = get_bounded_swath_polygon(run_config.track_number, run_config.bounding_geojson_filename)
    minimum_overlap = get_minimum_overlap(bounded_swath_polygon)

    print(f'Preparing time series with minimum overlap={minimum_overlap}:')

    subprocess.call([
        f'{run_config.wrapper_script_dir}/prepare_time_series.sh',
        run_config.working_dir,
        run_config.downloads_dir,
        run_config.bounding_geojson_filename,
        str(minimum_overlap)
    ])

def verify_time_series_preparation(working_dir) -> None:
    required_files = [
        './stack/cohStack.vrt',
        './stack/connCompStack.vrt',
        './stack/unwrapStack.vrt',
        './DEM/SRTM_3arcsec.dem',
        './mask/watermask.msk',
    ]

    missing_files = [filepath for filepath in required_files if not os.path.isfile(os.path.join(working_dir, filepath))]
    print('Checking time series preparation output...')
    if len(missing_files) > 0:
        raise RuntimeError(f'Some time-series preparation files were not created: {",".join(missing_files)}')
    else:
        print('All required time-series files are present')

def run_mintpy(working_dir) -> None:
    mintpy_app = 'smallbaselineApp.py'
    mintpy_config = f'{working_dir}/smallbaselineApp.cfg'

    print(f'Running MintPy {mintpy_app} using config at {mintpy_config}')
    subprocess.call([mintpy_app, mintpy_config])


def get_temporal_span(downloads_dir) -> (datetime, datetime):
    """Returns a pair of datetimes representing the earliest and latest datetimes for ASF downloaded files in the given
    directory"""

    def extract_date_pair(filename):
        date_chunk = next((chunk for chunk in filename.split('-') if
                           len(chunk) == 17 and all([subchunk.isnumeric() for subchunk in chunk.split('_')])))
        return date_chunk.split('_')

    # TODO: Implement for virtual downloads as well
    filenames = glob.glob(downloads_dir + '/*.nc')
    datestring_pairs = map(extract_date_pair, filenames)
    datestrings = itertools.chain.from_iterable(datestring_pairs)
    dates = list(map(lambda x: datetime.strptime(x, '%Y%m%d'), datestrings))
    return min(dates), max(dates)


def generate_product(run_config: RunConfig) -> None:
    dataset = Dataset('S1-TIMESERIES-MINTPY', run_config.working_dir)
    sensing_start, sensing_end = get_temporal_span(run_config.downloads_dir)
    with open(run_config.bounding_geojson_filename) as bounding_geojson_file:
        location_geometry = json.load(bounding_geojson_file)['features'][0]['geometry']

    dataset.populate_definition('MintPy Time Series', location_geometry, sensing_start, sensing_end)
    dataset.populate_metadata({
        'track': run_config.track_number
    })

    dataset.assemble()


def main(**kwargs) -> None:
    verify_dependencies()

    run_config = RunConfig(working_dir=os.path.abspath(os.getcwd()), **kwargs)
    run_config.print_job_arguments()

    download_raw_products(run_config)
    verify_successful_download()

    prepare_time_series(run_config)
    verify_time_series_preparation(run_config.working_dir)

    run_mintpy(run_config.working_dir)

    generate_product(run_config)


if __name__ == '__main__':
    args = argument_parser().parse_args()
    main(bounds=args.bounds,
         get_polygon_from_context=args.polygonfromcontext,
         track_number=int(args.track_number),
         start_date=datetime.strptime(args.start_date, '%Y-%m-%d'),
         end_date=datetime.strptime(args.end_date, '%Y-%m-%d'),
         virtual_download=args.virtualdownload,
         pge_root=args.pge_root)
