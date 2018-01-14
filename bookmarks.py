#!/usr/bin/python
# encoding: utf-8

import argparse
import codecs
import json
import sys
from os.path import expanduser, isfile
from workflow import Workflow3, ICON_WARNING, MATCH_ALL,  MATCH_ALLCHARS, MATCH_SUBSTRING

log = None

def get_bookmarks(profiles):
    bookmarks = []

    for profile in profiles:
        profileDir = expanduser("~/Library/Application Support/Google/Chrome/%s" % profile)
        iconFile = profileDir + "/Google Profile Picture.png"
        if not isfile(iconFile):
            iconFile = "icon.png"

        bookmark_filename = profileDir + "/Bookmarks"
        if isfile(bookmark_filename):
            wf.logger.info("Searching file: %s", bookmark_filename)
            bookmark_file = codecs.open(bookmark_filename, encoding='utf-8')
            bookmark_data = json.load(bookmark_file)
            roots = bookmark_data["roots"]

            for key in roots:
                get_bookmark_tree(roots[key], bookmarks, "", iconFile)

    return bookmarks

def get_bookmark_tree(tree, bookmarks, path, icon_filename):
    if type(tree) is not dict:
        return
    for i, item in enumerate(tree["children"]):
        name = item['name']
        itemPath = path + " : " + name if path != "" else name
        if item.has_key("children"):
            get_bookmark_tree(item, bookmarks, itemPath, icon_filename)
        else:
            bookmarks.append({"name": name, "url": item['url'], "path": path, "icon": icon_filename})


def search_key_for_bookmark(bookmark):
    """Generate a string search key for a post"""
    elements = []
    elements.append(bookmark['name'])  # name of bookmark
    elements.append(bookmark['url'])  # url of bookmark
    elements.append(bookmark['path'])  # path of bookmark
    return u' '.join(elements)


def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    ####################################################################
    # Get saved profiles or use Default
    ####################################################################
    profiles = wf.settings.setdefault("profiles", ["Default"])
    wf.logger.debug("profiles=%s", ', '.join(profiles))

    ####################################################################
    # View/filter Bookmarks
    ####################################################################
    query = args.query

    # Retrieve bookmarks from cache if available and no more than 600 seconds old
    def wrapper():
        return get_bookmarks(profiles)

    bookmarks = wf.cached_data('bookmarks', wrapper, max_age=1)

    if not bookmarks:  # we have no data to show, so show a warning and stop
        wf.add_item('No bookmarks found', 'bm-add to add profiles', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # If script was passed a query, use it to filter posts
    if query:
        # match everything but all-characters-in-item and substring
        match_on=MATCH_ALL ^ MATCH_ALLCHARS ^ MATCH_SUBSTRING
        bookmarks = wf.filter(query, bookmarks, key=search_key_for_bookmark, min_score=20, match_on=match_on)

    # Loop through the returned bookmarks and add an item for each to
    # the list of results for Alfred
    for bookmark in bookmarks:
        location = "in " + bookmark['path'] if bookmark['path'] != "" else ""
        url = " (" + bookmark['url'] + ")"
        wf.add_item(title=bookmark['name'],
                    subtitle=location + url,
                    arg=bookmark['url'],
                    valid=True,
                    icon=bookmark['icon'])

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
