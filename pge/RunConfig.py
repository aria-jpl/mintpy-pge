import json
import os
from datetime import datetime


class RunConfig:
    def __init__(self, **kwargs):
        self.pge_root: str = kwargs.get('pge_root') if kwargs.get('pge_root') else '/home/ops/verdi/ops/mintpy-pge'
        self.wrapper_script_dir: str = '{}/wrapper_scripts'.format(self.pge_root)
        self.working_dir: str = kwargs.get('working_dir') if kwargs.get('working_dir') else os.path.abspath(os.getcwd())

        self.track_number: int = kwargs.get('track_number')
        self.start_date: datetime = kwargs.get('start_date')
        self.end_date: datetime = kwargs.get('end_date')
        self.use_virtual_download: bool = kwargs.get('virtual_download')

        self.download_mode: str = 'url' if self.use_virtual_download else 'download'
        self.downloads_dir: str = os.path.join(self.working_dir,
                                               'URLproducts' if self.use_virtual_download else 'products')

        self.bounding_geojson_filename = self.get_bounding_geojson_filename(**kwargs)

    def get_bounding_geojson_filename(self, **kwargs):
        if kwargs.get('bounds') and kwargs.get('get_polygon_from_context'):
            raise Exception(
                'Only one of "--bounds" and "--get_polygon_from_context" may be supplied (both were supplied)')

        if not (kwargs.get('bounds') or kwargs.get('get_polygon_from_context')):
            raise Exception(
                'Either "--bounds" or "--get_polygon_from_context" must be supplied (neither were supplied)')

        if kwargs.get('bounds'):
            frame_bounds = kwargs.get('bounds').split()
            polygon_coordinates = [
                [frame_bounds[2], frame_bounds[1]],
                [frame_bounds[3], frame_bounds[1]],
                [frame_bounds[3], frame_bounds[0]],
                [frame_bounds[2], frame_bounds[0]]
            ]
        else:
            working_dir = os.path.abspath(os.getcwd())
            context_filepath = os.path.join(working_dir, '_context.json')
            with open(context_filepath) as context_file:
                context = json.loads(context_file.read())
            polygon_arg = next(parameter['value'] for parameter in context['job_specification']['params'] if
                               parameter['name'] == 'polygon')
            polygon_coordinates = polygon_arg['coordinates'][0]

        # Ensure conformance with GeoJSON requirements (float-type members and closed ring)
        polygon_coordinates = [[float(value) for value in point] for point in polygon_coordinates]
        if not polygon_coordinates[0] == polygon_coordinates[-1]:
            polygon_coordinates.append(polygon_coordinates[0])

        polygon_filename = os.path.join(self.pge_root, 'polygon.json')

        with open(polygon_filename) as polygon_file:
            polygon = json.load(polygon_file)

        polygon['features'][0]['geometry']['coordinates'] = [polygon_coordinates, ]

        with open(polygon_filename, 'w') as polygon_file:
            json.dump(polygon, polygon_file)

        return polygon_filename

    def print_job_arguments(self):
        print("Work directory: ", self.working_dir)
        print("Downloads directory: ", self.downloads_dir)
        print("Download mode: ", self.download_mode)
        print("Start: ", self.start_date)
        print("End: ", self.end_date)
        print("Track number: ", self.track_number)
        print("BBox file: ", self.bounding_geojson_filename)
