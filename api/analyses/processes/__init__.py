import logging
import requests
from analyses.models import ContextHandler
from os import path, makedirs
from shutil import rmtree


class Process:
    DATASET_FILE_NAME = 'dataset.csv'

    STATE_READY = 'ready'

    class HasFinished(RuntimeError):
        pass

    def __init__(self, analysis):
        self.analysis = analysis
        self.contexts = self.analysis.contexts  # type: ContextHandler

    def init(self):
        raise NotImplementedError()

    def tick(self):
        current_state = self.contexts.read('state', None)

        if current_state is None:
            self.before_init()
            self.init()
            self.contexts.write('state', self.STATE_READY)
        else:
            handle_func = getattr(self, 'when_%s' % current_state)
            handle_func()

    def when_ready(self):
        pass

    def before_init(self):
        from django.conf import settings

        logging.info('cleaning analysis contexts')
        self.contexts.remove_all()

        # prepare files
        logging.info('prepare work dir')
        work_dir = path.join(settings.DATA_DIR, 'analyses', str(self.analysis.id))
        if path.isdir(work_dir):
            rmtree(work_dir)
        makedirs(work_dir)

        # file provider urls
        file_id = self.analysis.dataset.filename
        file_meta_url = 'https://www.filestackapi.com/api/file/%s/metadata' % file_id
        file_download_url = 'https://www.filestackapi.com/api/file/%s?dl=true' % file_id

        # fetch file meta
        logging.info('validate dataset file type')
        file_meta = requests.get(file_meta_url).json()
        if file_meta['mimetype'] != 'text/csv':
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
