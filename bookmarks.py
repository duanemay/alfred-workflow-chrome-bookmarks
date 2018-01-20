#!/usr/bin/python
# encoding: utf-8

import argparse
import sys

from bookmarkIndex import BookmarkIndex
from workflow import Workflow3, ICON_WARNING
from workflow.background import run_in_background


def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    ####################################################################
    # Get saved profiles or use Default
    ####################################################################
    bookmark_index = BookmarkIndex(wf)
    profiles = wf.settings.setdefault("profiles", ["Default"])

    ####################################################################
    # Do Search
    ####################################################################
    ix = bookmark_index.get_index(profiles)

    with ix.searcher() as searcher:
        if searcher.doc_count() == 0:  # we have no data to show, so show a warning and stop
            wf.add_item('No bookmarks found', 'bm-add to add profiles', icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        query_string = args.query
        if len(query_string) == 1:
            parsed_query = bookmark_index.prefix_query(query_string)
            results = searcher.search(parsed_query, limit=20)
        elif query_string:
            parsed_query = bookmark_index.parse_query(query_string)
            results = searcher.search(parsed_query, limit=20)
        else:
            results = searcher.search(bookmark_index.all_query(), limit=20, sortedby="urlSize")

        if results.scored_length() == 0:  # we have no data to show, so show a warning and stop
            wf.add_item('No bookmarks found', 'Try a different query', icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        # Loop through the returned bookmarks and add an item for each to
        # the list of results for Alfred
        for hit in results:
            location = "in " + hit['path'] + " " if hit['path'] != "" else ""
            url = "(" + hit['url'] + ")"
            wf.add_item(title=hit['name'],
                        subtitle=location + url,
                        arg=hit['url'],
                        valid=True,
                        icon=hit['icon'])

    ####################################################################
    # Reindex in background, if our index was old
    ####################################################################
    fresh_index = wf.cached_data('freshIndex', max_age=600)
    if fresh_index is None:
        run_in_background('index',
                          ['/usr/bin/python',
                           wf.workflowfile('bookmarkIndex.py')])

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
