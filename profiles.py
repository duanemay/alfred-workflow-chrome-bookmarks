#!/usr/bin/python
# encoding: utf-8

import argparse
import codecs
import json
import ntpath
import sys
from glob import glob
from os.path import expanduser, isfile

from workflow import Workflow3, ICON_WARNING

log = None


def get_profiles():
    profile_list = []

    chrome_dir = expanduser("~/Library/Application Support/Google/Chrome/")
    bookmark_files = glob(chrome_dir + "/*/Bookmarks")
    log.info("Searching profiles: %s", ", ".join(bookmark_files))

    for bookmarkFile in bookmark_files:
        profile_dir = ntpath.dirname(bookmarkFile)
        profile_info = build_profile_info(profile_dir)
        profile_list.append(profile_info)

    return profile_list


def build_profile_info(profile_dir):
    profile_dir_name = ntpath.basename(profile_dir)
    icon_file = profile_dir + "/Google Profile Picture.png"
    if not isfile(icon_file):
        icon_file = "icon.png"

    preferences_filename = profile_dir + "/Preferences"
    if isfile(preferences_filename):
        log.info("Searching file: %s", preferences_filename)
        preferences_file = codecs.open(preferences_filename, encoding='utf-8')
        preferences_data = json.load(preferences_file)
        profile_name = preferences_data["profile"]["name"]
    else:
        profile_name = "Guest"

    return {"name": profile_name, "dirName": profile_dir_name, "icon": icon_file}


def search_key_for_profile(profile):
    """Generate a string search key for a post"""
    elements = [profile['name'], profile['dirName']]
    return u' '.join(elements)


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('--addProfile', action='store_true')
    parser.add_argument('--removeProfile', action='store_true')
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    ####################################################################
    # View/filter Profiles
    ####################################################################
    if args.removeProfile:  # Script was passed removeProfile
        profiles = wf.settings.setdefault("profiles", [])
        profile_list = []
        for profile in profiles:
            profile_dir = expanduser("~/Library/Application Support/Google/Chrome/%s" % profile)
            profile_info = build_profile_info(profile_dir)
            profile_list.append(profile_info)
    else:  # Script was passed or defaults to addProfile
        profile_list = wf.cached_data('profiles', get_profiles, max_age=300)

    query = args.query
    if query:
        profile_list = wf.filter(query, profile_list, key=search_key_for_profile, min_score=20)

    if not profile_list:  # we have no data to show, so show a warning and stop
        wf.add_item('No profiles found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned profiles and add an item for each to
    # the list of results for Alfred
    for profile in profile_list:
        wf.add_item(title=profile['name'],
                    subtitle=profile['dirName'],
                    arg=profile['dirName'],
                    valid=True,
                    icon=profile['icon'])

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    workflow = Workflow3()
    log = workflow.logger
    sys.exit(workflow.run(main))
