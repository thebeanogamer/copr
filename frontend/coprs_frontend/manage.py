#!/usr/bin/python3


import os
import sys
import copy
import pipes
import importlib
import click
from commands.flask3_wrapper import get_flask_wrapper_command
import commands.test
import commands.create_sqlite_file
import commands.create_db
import commands.drop_db
import commands.create_chroot
import commands.alter_chroot
import commands.display_chroots
import commands.drop_chroot
import commands.branch_fedora
import commands.comment_chroot
import commands.alter_user
import commands.add_user
import commands.dump_user
import commands.update_indexes
import commands.update_indexes_quick
import commands.update_indexes_required
import commands.get_admins
import commands.fail_build
import commands.rawhide_to_release
import commands.update_graphs
import commands.vacuum_graphs
import commands.notify_outdated_chroots
import commands.delete_outdated_chroots
import commands.clean_expired_projects
import commands.clean_old_builds
import commands.delete_orphans

from coprs import app

if os.getuid() == 0:
    sys.stderr.write("Please don't run this script as a 'root' user, use:\n")
    sys.stderr.write("$ sudo -u copr-fe {}\n".format(
            ' '.join([pipes.quote(arg) for arg in sys.argv])))
    sys.exit(1)

commands_list =	[
    # General commands
    "test",

    # Database commands
    "create_sqlite_file",
    "create_db",
    "drop_db",

    # Chroot commands
    "create_chroot",
    "alter_chroot",
    "display_chroots",
    "drop_chroot",
    "branch_fedora",
    "comment_chroot",

    # User commands
    "alter_user",
    "add_user",
    "dump_user",

    # Whooshee indexes
    "update_indexes",
    "update_indexes_quick",
    "update_indexes_required",

    # Other
    "get_admins",
    "fail_build",
    "rawhide_to_release",
    "update_graphs",
    "vacuum_graphs",
    "notify_outdated_chroots",
    "delete_outdated_chroots",
    "clean_expired_projects",
    "clean_old_builds",
    "delete_orphans",
]

for command in commands_list:
    cmd_obj = getattr(getattr(commands, command), command)

    # Add underscored commands, e.g. 'add_user' for 'add-user' for compatibility
    # reasons.  TODO: we can drop this once we have the deployment scripts fixed
    # to use the dash-variant commands.
    if '_' in command and hasattr(cmd_obj, 'hidden'):
        # hidden option is available on f30+ only (click v7.0)
        alias = copy.deepcopy(cmd_obj)
        alias.hidden = True
        app.cli.add_command(alias, command)

    app.cli.add_command(cmd_obj)


app.cli.add_command(get_flask_wrapper_command('runserver'))
app.cli.add_command(get_flask_wrapper_command('run'))
app.cli.add_command(get_flask_wrapper_command('shell'))

if __name__ == "__main__":
    app.cli()
