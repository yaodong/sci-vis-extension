import logging
import requests
from analyses.models import ContextHandler
from os import path, makedirs
from shutil import rmtree


class Process:
    DATASET_FILE_NAME = 'dataset.csv'

    STATE_READY = 'ready'

    params = {}
    dataset = None

    class HasFinished(RuntimeError):
        pass

    def __init__(self, analysis):
        self.analysis = analysis
        self.contexts = self.analysis.contexts  # type: ContextHandler
        self.params = self.analysis.params
        self.dataset = self.analysis.dataset

    def tick(self):
        current_state = self.contexts.read('state', None)

        logging.info('process tick %i:%s' % (self.analysis.id, current_state))

        if current_state is None:
            self.download_dataset()
            self.contexts.write('state', self.STATE_READY)
        else:
            handle_func = getattr(self, 'when_%s' % current_state)
            handle_func()

    def when_ready(self):
        pass

    def download_dataset(self):
        from django.conf import settings

        logging.info('cleaning analysis contexts')
        self.contexts.remove_all()

        # prepare files
        logging.info('prepare work dir')
        work_dir = path.join(settings.DATA_DIR,
                             'analyses', str(self.analysis.id))
        if path.isdir(work_dir):
            rmtree(work_dir)
        makedirs(work_dir)

        # file provider urls
        file_id = self.analysis.dataset.file_name
        file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

        # fetch file meta
        if self.analysis.dataset.file_meta['mimetype'] != 'text/csv':
            raise RuntimeError("invalid dataset format")

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
