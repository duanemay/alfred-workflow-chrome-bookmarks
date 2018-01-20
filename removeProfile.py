#!/usr/bin/python
# encoding: utf-8

import sys

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
    # Save the removed profiles
    ####################################################################
    profiles.remove(profile)
    wf.settings['profiles'] = profiles
    wf.clear_cache(lambda f: f.startswith('bookmarks'))
    notify('Profile no longer searched', profile)

    run_in_background('index',
                      ['/usr/bin/python',
                       wf.workflowfile('bookmarkIndex.py')])

    return 0  # 0 means script exited cleanly


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
