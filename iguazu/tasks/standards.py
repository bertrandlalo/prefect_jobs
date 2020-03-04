import collections
import logging

import iguazu


logger = logging.getLogger(__name__)


class Report(iguazu.Task):

    def run(self, *, files):
        logger.info('This is a very reduced report!')
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
        msg = []
        for k, v in counter.most_common():
            msg.append(f'{v} tasks with status {k}')
        msg = '\n'.join(msg)
        logger.info('Report is:\n%s', msg)
        return msg
