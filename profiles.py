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
    profileList = []

    chromeDir = expanduser("~/Library/Application Support/Google/Chrome/")
    bookmarkFiles = glob(chromeDir + "/*/Bookmarks")
    wf.logger.info("Searching profiles: %s", ", ".join(bookmarkFiles))

    for bookmarkFile in bookmarkFiles:
        profileDir = ntpath.dirname(bookmarkFile)
        profileInfo = build_Profile_info(profileDir)
        profileList.append(profileInfo)

    return profileList


def build_Profile_info(profileDir):
    profileDirName = ntpath.basename(profileDir)
    iconFile = profileDir + "/Google Profile Picture.png"
    if not isfile(iconFile):
        iconFile = "icon.png"

    preferences_filename = profileDir + "/Preferences"
    if isfile(preferences_filename):
        wf.logger.info("Searching file: %s", preferences_filename)
        preferences_file = codecs.open(preferences_filename, encoding='utf-8')
        preferences_data = json.load(preferences_file)
        profileName = preferences_data["profile"]["name"]
    else:
        profileName = "Guest"

    return {"name": profileName, "dirName": profileDirName, "icon": iconFile}


def search_key_for_profile(profile):
    """Generate a string search key for a post"""
    elements = []
    elements.append(profile['name'])  # name of bookmark
    elements.append(profile['dirName'])  # url of bookmark
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
        profileList = []
        for profile in profiles:
            profileDir = expanduser("~/Library/Application Support/Google/Chrome/%s" % profile)
            profileInfo = build_Profile_info(profileDir)
            profileList.append(profileInfo)

    else:  # Script was passed or defaults to addProfile
        profileList = wf.cached_data('profiles', get_profiles, max_age=300)

    query = args.query
    if query:
        profileList = wf.filter(query, profileList, key=search_key_for_profile, min_score=20)

    if not profileList:  # we have no data to show, so show a warning and stop
        wf.add_item('No profiles found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned profiles and add an item for each to
    # the list of results for Alfred
    for profile in profileList:
        wf.add_item(title=profile['name'],
                    subtitle=profile['dirName'],
                    arg=profile['dirName'],
                    valid=True,
                    icon=profile['icon'])

    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
