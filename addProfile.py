#!/usr/bin/python
# encoding: utf-8

import sys
import argparse

from workflow import Workflow3
from workflow.notify import notify

log = None

def main(wf):

    parser = argparse.ArgumentParser()
    parser.add_argument('profile', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    ####################################################################
    # Get saved profiles or use Default
    ####################################################################
    profiles = wf.settings.setdefault("profiles", [])
    wf.logger.debug("profiles=%s", ', '.join(profiles))

    profile = args.profile
    if not profile:  # we have no data to show, so show a warning and stop
        notify('No profile specified')
        return 1

    ####################################################################
    # Save the added profiles
    ####################################################################
    profiles.append(profile)
    wf.settings['profiles'] = profiles
    wf.clear_cache(lambda f: f.startswith('bookmarks'))
    notify('Profile will be searched', profile)
    return 0  # 0 means script exited cleanly

if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))