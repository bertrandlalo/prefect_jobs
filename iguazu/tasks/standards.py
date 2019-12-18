import collections
import logging

import iguazu


logger = logging.getLogger(__name__)


class Report(iguazu.Task):

    def __init__(self, #*,
                 suffix: str = '_merged',
                 # temporary: bool = False,
                 # check_status: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        # self.suffix = suffix
        # self.temporary = temporary
        # self.check_status = check_status

    # def run(self, *, parent: FileProxy, **kwargs) -> str:
    #     output_file = self.default_outputs(parent=parent, **kwargs)
    #     status = dict()

    def run(self, *, files):
        logger.info('STANDARDIZATION REPORT NOT YET IMPLEMENTED WITH %s', files)
        status = []
        journal_family = self.meta.metadata_journal_family
        for f in files:
            meta = f.metadata.get(journal_family, {})
            journal_status = meta.get('status', 'No status')
            problem = meta.get('problem', None)
            if problem is not None:
                title = problem.get('title', '')
                journal_status = ': '.join([journal_status, title])
            status.append(journal_status)

        counter = collections.Counter(status)
        logger.info('status report:\n%s', counter)

        msg = []
        for k, v in counter.most_common():
            msg.append(f'{v} tasks with status {k}')
        return '\n'.join(msg)
