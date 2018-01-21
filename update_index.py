#!/usr/bin/python
# encoding: utf-8

import sys
import time

from bookmark_index import BookmarkIndex, INDEXING_SETTING
from workflow import Workflow3

if __name__ == u"__main__":
    workflow = Workflow3()
    if workflow.cached_data(INDEXING_SETTING, max_age=30):
        workflow.logger.info("Already indexing, quitting")
        sys.exit(0)

    start = time.time()
    bi = BookmarkIndex(workflow)
    profilesToIndex = workflow.settings.setdefault("profiles", ["Default"])
    whoosh_index = bi.index_profiles(profilesToIndex)
    end = time.time()
    with whoosh_index.searcher() as searcher:
        numDocs = searcher.doc_count()

    time = end - start
    workflow.logger.info("Indexed %d documents, in %f seconds.", numDocs, time)

    sys.exit(0)
