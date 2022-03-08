#!/usr/bin/python3

import re
import sys
import os
import logging
import argparse
import pwd

from copr_backend.helpers import BackendConfigReader, call_copr_repo
from copr_backend.sign import get_pubkey, unsign_rpms_in_dir, sign_rpms_in_dir, create_user_keys, create_gpg_email

logging.basicConfig(
    filename="/var/log/copr-backend/fix_gpg.log",
    format='[%(asctime)s][%(levelname)6s]: %(message)s',
    level=logging.DEBUG)
log = logging.getLogger(__name__)


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
Script to generate missing keys for copr owners, regenerate pubkey.gpg and fix signatures on rpms in coprs:
    a) that were forked
    b) influenced by gpgdup bug (bz#1330322)
    c) ...
As input, takes file with new-line separated copr full names (owner/coprname).
For all coprs in this file, generates key-pairs on copr-keygen machine (if not generated),
re-signs its rpms and regenerates pubkey.gpg.
""")

parser.add_argument('coprs_file_path', action='store', help='Path to the text file with copr full names (owner/coprname) to be fixed.')
args = parser.parse_args()


def fix_copr(opts, copr_full_name):
    log.info('Going to fix {}:'.format(copr_full_name))

    owner, coprname = tuple(copr_full_name.split('/'))
    copr_path = os.path.abspath(os.path.join(opts.destdir, owner, coprname))

    if not os.path.isdir(copr_path):
        log.info('Ignoring {}. Directory does not exist.'.format(copr_path))
        return

    log.info('> Generate key-pair on copr-keygen (if not generated) for email {}.'.format(create_gpg_email(owner, coprname)))
    create_user_keys(owner, coprname, opts)

    log.info('> Regenerate pubkey.gpg in copr {}.'.format(copr_path))
    get_pubkey(owner, coprname, log, os.path.join(copr_path, 'pubkey.gpg'))

    # Match the "00001231-anycharacer" directory names.  Compile once, use many.
    builddir_matcher = re.compile(r"\d{8,}-")

    log.info('> Re-sign rpms and call createrepo in copr\'s chroots:')
    for chroot in os.listdir(copr_path):
        dir_path = os.path.join(copr_path, chroot)
        if not os.path.isdir(dir_path):
            log.info('> > Ignoring {}'.format(dir_path))
            continue

        if chroot in ["srpm-builds", "modules", "repodata"]:
            log.debug("Ignoring %s, not a chroot", chroot)
            continue

        for builddir_name in os.listdir(dir_path):
            builddir_path = os.path.join(dir_path, builddir_name)
            if not os.path.isdir(builddir_path):
                continue
            if not builddir_matcher.match(builddir_name):
                log.debug("Skipping %s, not a build dir", builddir_name)
                continue

            log.info('> > Processing rpms in builddir {}:'.format(builddir_path))
            try:
                unsign_rpms_in_dir(builddir_path, opts, log) # first we need to unsign by using rpm-sign before we sign with obs-sign
                sign_rpms_in_dir(owner, coprname, builddir_path, chroot, opts, log)
            except Exception as e:
                log.exception(str(e))
                continue

        log.info("> > Running add_appdata for %s", dir_path)
        call_copr_repo(dir_path, logger=log)


def main():
    opts = BackendConfigReader().read()
    with open(args.coprs_file_path) as coprs_file:
        for copr_full_name in coprs_file:
            try:
                fix_copr(opts, copr_full_name.strip())
            except Exception as e:
                log.exception(str(e))


if __name__ == "__main__":
    if pwd.getpwuid(os.getuid())[0] != "copr":
        print("This script should be executed under the `copr` user")
        sys.exit(1)
    else:
        main()
