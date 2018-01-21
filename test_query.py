#!/usr/bin/python
# encoding: utf-8

import argparse
import sys

from bookmark_index import BookmarkIndex
from workflow import Workflow3


def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser("This will show parsed queries and number of results")
    parser.add_argument('query', default=None)
    args = parser.parse_args(wf.args)

    bookmark_index = BookmarkIndex(wf)
    ix = bookmark_index.get_index_if_exists()
    if not ix:
        print("No Index")
        return 1

    with ix.searcher() as searcher:
        query_string = args.query

        print("Index has %d documents" % searcher.doc_count())
        print("Query String: %s" % query_string)

        parsed_prefix_query = bookmark_index.prefix_query(query_string)
        prefix_results = searcher.search(parsed_prefix_query, limit=50)
        print("\nprefix query: %s\nprefix results: %d" % (parsed_prefix_query, prefix_results.scored_length()))
        print("Top 10 Results:")
        for hit in prefix_results[0:10]:
            print("  %.06f - %s" % (hit.score, hit['name'][0:90]))

        parsed_term_query = bookmark_index.n_gram_query(query_string)
        results = searcher.search(parsed_term_query, limit=50)
        print("\nterm query: %s\nterm results: %d" % (parsed_term_query, results.scored_length()))
        print("Top 10 Results:")
        for hit in results[0:10]:
            print("  %.06f - %s" % (hit.score, hit['name'][0:90]))

        results.upgrade_and_extend(prefix_results)
        print("\nCombined(upgrade_and_extend): %d" % results.scored_length())
        print("Top 10 Results:")
        for hit in results[0:10]:
            print("  %.06f - %s" % (hit.score, hit['name'][0:90]))


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
