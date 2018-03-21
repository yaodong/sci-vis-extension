import logging
import requests
from analyses.models import ContextHandler
from os import path, makedirs
from shutil import rmtree
import numpy as np


class Process:
    DATASET_FILE_NAME = 'dataset.csv'

    STATE_READY = 'ready'

    params = {}
    dataset = None

    work_dir = None

    class HasFinished(RuntimeError):
        pass

    def __init__(self, analysis):

        # assign objects
        self.analysis = analysis
        self.contexts = self.analysis.contexts  # type: ContextHandler
        self.params = self.analysis.params
        self.dataset = self.analysis.dataset

        # preparing workspace
        self.remove_contexts()
        self.download_dataset()

        logging.info('analysis init %i' % self.analysis.id)

    def download_dataset(self):
        from django.conf import settings

        logging.info('cleaning analysis contexts')
        self.contexts.remove_all()

        # prepare files
        logging.info('prepare work dir')
        work_dir = path.join(settings.DATA_DIR,
                             'analyses', str(self.analysis.id))
        self.work_dir = work_dir

        if path.isdir(work_dir):
            rmtree(work_dir)

        makedirs(work_dir)

        # file provider urls
        file_id = self.analysis.dataset.file_name
        file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

        # fetch file meta
#        if self.analysis.dataset.file_meta['mimetype'] != 'text/csv':
#            raise RuntimeError("invalid dataset format %s" % self.analysis.dataset.file_meta['mimetype'])

        # download files
        logging.info('download dataset file')
        local_file_path = path.join(work_dir, self.DATASET_FILE_NAME)
        req = requests.get(file_download_url, stream=True)
        with open(local_file_path, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # save contexts
        self.contexts.write('path.work_dir', work_dir)
        self.contexts.write('path.dataset_file', local_file_path)

    def remove_contexts(self):
        self.analysis.contexts.remove_all()

    def convert_to_points(self, method='MDS', dimension=3):
        logging.info('create points file')

        dataset_file_name = self.contexts.read('path.dataset_file')

        dataset_path = path.join(self.work_dir, dataset_file_name)
        points_path = path.join(self.work_dir, 'base_points')

        from analyses.utils.graph_scaling import graph_scaling

        points = graph_scaling(
            dataset_path,
            points_path,
            method,
            dimension
        )

        np.save(points_path, points)
        points_path += '.npy'
        self.contexts.write('path.points_file', points_path)
        return points
