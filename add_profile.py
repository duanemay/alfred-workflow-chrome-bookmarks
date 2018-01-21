#!/usr/bin/python
# encoding: utf-8

import sys

from bookmark_index import BACKGROUND_JOB_KEY, UPDATE_INDEX_COMMAND
from workflow import Workflow3
from workflow.background import run_in_background


def main(wf):
    import argparse
    from workflow.notify import notify

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
    notify('Profile will be searched', profile)

    run_in_background(BACKGROUND_JOB_KEY,
                      ['/usr/bin/python',
                       wf.workflowfile(UPDATE_INDEX_COMMAND)])

    return 0  # 0 means script exited cleanly


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
