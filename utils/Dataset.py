import json
import os
import subprocess
from hashlib import md5
from shutil import copyfile


class Dataset:
    required_files = [
        'maskTempCoh.h5',
        'timeseries.h5',
        'timeseries_demErr.h5',
        'velocity.h5',
        'waterMask.h5'
    ]

    definition = None
    metadata = None

    def __init__(self, working_dir=os.getcwd()):
        self.working_dir = working_dir
        self.id = Dataset.generate_id()
        self.staging_dir = os.path.join(self.working_dir, self.id)

        missing_files = []
        for filename in Dataset.required_files:
            if not os.path.isfile(os.path.join(self.working_dir, filename)):
                missing_files.append(filename)

        if len(missing_files) > 0:
            raise FileNotFoundError(
                f'The following required files are missing from "{self.working_dir}": {", ".join(missing_files)}')

    @staticmethod
    def generate_id(id_prefix):
        timestamp = subprocess.check_output(['date', '-u', '+%Y%m%dT%H%M%S.%NZ']).decode().strip()
        hash_suffix = md5(timestamp.encode()).hexdigest()[0:5]
        return f'{id_prefix}{timestamp}-{hash_suffix}'

    def populate_definition(self):
        self.definition = {
            "version": "v1.0"
        }

    def populate_metadata(self):
        self.metadata = {

        }

    def assemble(self):

        if self.definition is None:
            raise Exception(
                'Cannot assemble Dataset files without first populating *.dataset.json using populate_definition()')

        if self.metadata is None:
            raise Exception(
                'Cannot assemble Dataset files without first populating *.met.json using populate_metadata()')

        with open(os.path.join(self.staging_dir, f'{self.id}.dataset.json'), 'w+') as definition_file:
            json.dump(self.definition, definition_file)

        with open(os.path.join(self.staging_dir, f'{self.id}.met.json'), 'w+') as metadata_file:
            json.dump(self.metadata, metadata_file)

        os.mkdir(self.staging_dir)
        for filename in self.required_files:
            copyfile(os.path.join(self.working_dir, filename), os.path.join(self.staging_dir, filename))
