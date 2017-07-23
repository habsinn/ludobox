#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 3 compatibility
from __future__ import print_function

import os
import glob
import shutil
import argparse
import py
import sys

from ludobox.run import serve
from ludobox import create_app
from ludobox.content import validate_content, read_content, ValidationError

# TODO: move this to config file
INPUT_DIR = os.path.join(os.getcwd(),"data")
OUTPUT_DIR = os.path.join(os.getcwd(),"static")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def red(txt):
    print(bcolors.FAIL + txt + bcolors.ENDC)

def green(txt):
    print(bcolors.OKGREEN + txt + bcolors.ENDC)

def clean(**kwargs):
    """Delete tmp files

    This function will remove:
    *   any *.pyc file generated by previous python execution/test
    *   any *.pyo file generated by previous python execution/test
    *   any __pycache__ files generated by previous python :mod:`py.test`

    """

    print("Remove all precompiled python files (*.pyc): ", end='')
    for f in glob.glob("server/**/*.pyc"):
        os.remove(f)
    print("SUCCESS")

    print("Remove all python generated object files (*.pyo): ", end='')
    for f in glob.glob("server/**/*.pyo"):
        os.remove(f)
    print("SUCCESS")

    print("Remove py.test caches directory (__pycache__): ", end='')
    shutil.rmtree("__pycache__", ignore_errors=True)
    shutil.rmtree("server/tests/__pycache__", ignore_errors=True)
    print("SUCCESS")

def test(fulltrace, **kwargs):
    """Run tests from the command line"""

    # unexported constasts used as pytest.main return codes
    # c.f. https://github.com/pytest-dev/pytest/blob/master/_pytest/main.py
    PYTEST_EXIT_OK = 0
    PYTEST_EXIT_TESTSFAILED = 1
    PYTEST_EXIT_INTERRUPTED = 2
    PYTEST_EXIT_INTERNALERROR = 3
    PYTEST_EXIT_USAGEERROR = 4
    PYTEST_EXIT_NOTESTSCOLLECTED = 5

    cmd = "server/tests"

    if fulltrace : cmd = cmd + " --fulltrace"

    unit_result = py.test.cmdline.main(cmd)
    # return the right code
    if unit_result not in (PYTEST_EXIT_OK, PYTEST_EXIT_NOTESTSCOLLECTED):
        print("To have more details about the errors you should try the command: py.test tests", file=sys.stderr)
        sys.exit("TESTS : FAIL")
    else:
        print("TESTS : SUCCESS")

def games(**kwargs):
    data_dir = os.path.join(os.getcwd(), 'data')

    errors_count = 0
    app=create_app()
    with app.app_context():
        for game_folder_name in os.listdir(data_dir) :
            errors = []
            path = os.path.join(data_dir,game_folder_name)

            # get only folders
            if os.path.isdir(path):
                info_file = os.path.join(path, "info.json")
                if os.path.exists(info_file):
                    info = read_content(path)
                    errors = validate_content(info, get_all_errors=True)
                    if len(errors):
                        print(info["title"] + bcolors.FAIL + "  %s"%len(errors) + bcolors.ENDC)
                        errors_count = errors_count + len(errors)
                    else :
                        print(bcolors.OKGREEN + info["title"] + " " + u"\u2713" + bcolors.ENDC)

    print()
    print("Done.")

    if errors_count :
        red("%s JSON formatting errors."%errors_count)
    else :
        green("No errors detected.")
    print()

def validate(game, **kwargs):
    if os.path.exists(game):
        app=create_app()
        with app.app_context():
            info = read_content(game)
            errors = validate_content(info, get_all_errors=True)
            if len(errors):
                for i, err in enumerate(errors):
                    print( "Error %s"%i , "--"*50)
                    print(err["path"])
                    red(err["message"])
                    print()
                print()
                print(info["title"])
                red("%s ERRORS"%len(errors))
                print()

            else :
                print(bcolors.OKGREEN + info["title"] + ". No errors " + u"\u2713" + bcolors.ENDC)

    else :
        print('ERROR : %s does not exist. Please specify a valid game path'%game)


def parse_args(args):
    """Configure the argument parser and returns it."""
    # Initialise the parsers
    parser = argparse.ArgumentParser(description="Ludobox server.")

    # Add all the actions (subcommands)
    subparsers = parser.add_subparsers(
        title="actions",
        description="the program needs to know what action you want it to do.",
        help="those are all the possible actions")

    # Test command ###########################################################
    parser_test = subparsers.add_parser(
        "test",
        help="Run server tests.")
    parser_test.add_argument(
        "--fulltrace",
        default=False,
        action='store_true',
        help="Show the complete test log")
    parser_test.set_defaults(func=test)

    # List games command ################################################
    parser_games = subparsers.add_parser(
        "games",
        help="List all games and trace existing errors in data.")
    parser_games.set_defaults(func=games)

    # Validate single games command ######################################
    parser_validate = subparsers.add_parser(
        "validate",
        help="Show errors in games' data.")
    parser_validate.add_argument(
        "game",
        action='store',
        help="Path of game",
        type=str)
    parser_validate.set_defaults(func=validate)

    # Clean command ###########################################################
    parser_clean = subparsers.add_parser(
        "clean",
        help="Remove temp files from the folder.")
    parser_clean.set_defaults(func=clean)

    # Serve command ###########################################################
    parser_start = subparsers.add_parser(
        "start",
        help="Launch a tiny Ludobox web server.")
    parser_start.set_defaults(func=serve)

    parser_start.add_argument(
        "--debug",
        default=False,
        action='store_true',
        help="activate the debug mode of the Flask server (for development "
             "only NEVER use it in production).")
    parser_start.add_argument(
        "--port",
        default=None,
        help="define port to serve the web application.")

    # Returns the, now configured, parser
    return parser.parse_args(args)

def main(commands=None):
    """
    Launch command parser from real command line or from args.
    """
    # Configure the parser
    # commands.split()
    args = parse_args(sys.argv[1:])

    return args.func(**vars(args))  # We use `vars` to convert args to a dict

if __name__ == "__main__":
    main()
