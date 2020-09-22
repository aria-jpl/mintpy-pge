import json
import os
import subprocess
from datetime import datetime
from hashlib import md5
from shutil import copyfile


class Dataset:
    required_files = [
        # Filepath relative to working directory
        'maskTempCoh.h5',
        'timeseries.h5',
        'timeseries_demErr.h5',
        'velocity.h5',
        'waterMask.h5',
        'inputs/geometryGeo.h5',
        'demErr.h5',
        'avgSpatialCoh.h5',
        'temporalCoherence.h5'
    ]

    definition = None
    metadata = None

    def __init__(self, id_prefix, **kwargs):
        self.working_dir = kwargs.get('working_dir') if kwargs.get('working_dir') else os.getcwd()

        context_filename = os.path.join(self.working_dir, '_context.json')
        self.id = Dataset.generate_id(id_prefix, context_filename)
        self.staging_dir = os.path.join(self.working_dir, self.id)

        missing_files = []
        for filename in Dataset.required_files:
            if not os.path.isfile(os.path.join(self.working_dir, filename)):
                missing_files.append(filename)

        if len(missing_files) > 0:
            raise FileNotFoundError(
                f'The following required files are missing from "{self.working_dir}": {", ".join(missing_files)}')

    @staticmethod
    def generate_id(id_prefix, context_filename):
        timestamp = subprocess.check_output(['date', '-u', '+%Y%m%dT%H%M%S.%NZ']).decode().strip()

        with open(context_filename) as context_file:
            hash_suffix = md5(context_file.read().encode()).hexdigest()[0:5]

        job_id = f'{id_prefix}-{timestamp}-{hash_suffix}'
        print(f'Generated job ID: {job_id}')
        return job_id

    def populate_definition(
            self,
            label=None,
            location_geometry: dict = None,
            sensing_start: datetime = None,
            sensing_end: datetime = None):

        definition = {
            "version": "v1.0",
        }

        if label:
            definition.update({'label': label})

        if location_geometry and all([key in location_geometry for key in ['type', 'coordinates']]):
            definition.update({'location': location_geometry})

        if sensing_start and sensing_end:
            definition.update({
                'starttime': sensing_start.strftime('%Y-%m-%dT%H:%M:%S'),
                'endtime': sensing_end.strftime('%Y-%m-%dT%H:%M:%S')
            })

        self.definition = definition

    def populate_metadata(self, metadata):
        self.metadata = metadata

    def assemble(self):

        if self.definition is None:
            raise Exception(
                'Cannot assemble Dataset files without first populating *.dataset.json using populate_definition()')

        if self.metadata is None:
            raise Exception(
                'Cannot assemble Dataset files without first populating *.met.json using populate_metadata()')

        os.mkdir(self.staging_dir)

        with open(os.path.join(self.staging_dir, f'{self.id}.dataset.json'), 'w+') as definition_file:
            json.dump(self.definition, definition_file)

        with open(os.path.join(self.staging_dir, f'{self.id}.met.json'), 'w+') as metadata_file:
            json.dump(self.metadata, metadata_file)

        for relative_filepath in self.required_files:
            filename = os.path.split(relative_filepath)[1]
            copyfile(os.path.join(self.working_dir, relative_filepath), os.path.join(self.staging_dir, filename))
