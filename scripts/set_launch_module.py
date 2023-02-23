#!/usr/bin/env python3
from copy import deepcopy
import json
import argparse
import os


DEFAULT_LAUNCH = {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Poetry",
            "type": "python",
            "request": "launch",
            "module": None,
            "pythonPath": None,
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": None
            },
            "args": [],
            "justMyCode": True,
        }
    ]
}


def build_launch_configuration(module=None, env_root=None, env_name=None, python=None):
    """ Build the launch configuration for the given module. """
 
    launch = deepcopy(DEFAULT_LAUNCH)
    if module:
        launch['configurations'][0]['module'] = module

        print(f"Using module: {launch['configurations'][0]['module']}")

    if env_root and env_name and python:
        if env_root.startswith("~"):
            env_root = os.path.expanduser(env_root)
            
        env = f"{env_root}/.{env_name}"

        launch['configurations'][0]['pythonPath'] = f"{env}/bin/{python}"
        launch['configurations'][0]['env']['PYTHONPATH'] = f"{env}/lib/{python}/site-packages"

        print(f"Using python path: {launch['configurations'][0]['pythonPath']}")

    return launch


def load_launch_json(launch_json):
    """ Open the launch.json file and return the json object. """
    with open(launch_json, 'r') as f:
        return json.load(f)


def save_launch_json(launch_json, launch):
    """ Save the launch object to the launch.json file. """
    with open(launch_json, 'w') as f:
        json.dump(launch, f, indent=2)


def diff_launches(one, two):
    """
        See DEFAULT_LAUNCH above for an example of the format VSCode uses.

        This function will compare the two launch dicts and yield the differences.
    """ 
    for key, value in one['configurations'][0].items():
        if two['configurations'][0][key] != value:
            yield key, (value, two['configurations'][0][key])


def update_launch_module(launch_json, module):
    """ Update the launch.json to use the given module. """
    
    launch = load_launch_json(launch_json)
    launch['configurations'][0]['module'] = module
    with open(launch_json, 'w') as f:
        json.dump(launch, f, indent=2)


def update_config_key(launch_json, key, value):
    """ Update the launch.json to use the given module. """
    
    launch = load_launch_json(launch_json)
    launch['configurations'][0][key] = value
    with open(launch_json, 'w') as f:
        json.dump(launch, f, indent=2)


def argparser():
    # lets define an argparser that lets us change the launch module easily and generate a new .vscode/ + launch.json
    parser = argparse.ArgumentParser(description="Set the launch module for the current project.")
    parser.add_argument("module", help="The module to launch.", default=None)
    parser.add_argument("--env-root", help="The root of the virtual environment.", default=None)
    parser.add_argument("--env-name", help="The name of the virtual environment.", default=None)
    parser.add_argument("--python", help="The python executable to use.", default=None)
    parser.add_argument("--config", help="The config file to use. Mostly for testing purposes.", default=None)

    parser.add_argument("-dud", "--disable-user-defaults", help="Use the user defaults.", action="store_false", dest="user_defaults", default=True)

    return parser


USER_LAUNCH_DEFAULTS = {
    "config": ".vscode/launch.json",
    "module": "preposition_traversal",
    "env-root": "~",
    "env-name": "py311",
    "python": "python3.11"
}


def main():
    print("Welcome to set_launch_module.py\n"
          "This script will set the launch.json to the correct\n"
          "module and python path for the current project.\n")

    parser = argparser()
    args = parser.parse_args()

    if args.user_defaults:
        # set user defaults only if they are not already set
        args.config = args.config or USER_LAUNCH_DEFAULTS["config"]
        args.module = args.module or USER_LAUNCH_DEFAULTS["module"]
        args.env_root = args.env_root or USER_LAUNCH_DEFAULTS["env-root"]
        args.env_name = args.env_name or USER_LAUNCH_DEFAULTS["env-name"]
        args.python = args.python or USER_LAUNCH_DEFAULTS["python"]
    else:
        # if the user defaults are disabled, we just set the config file
        args.config = args.config or ".vscode/launch.json"

    # Get current launch.json
    try:
        launch = load_launch_json(args.config)
    except FileNotFoundError:
        launch = None

    # Create new launch.json
    new_launch = build_launch_configuration(args.module, args.env_root, args.env_name, args.python)
    diffs = list(diff_launches(launch, new_launch))

    # If there is no launch.json, we simply need to create one
    if launch is None:
        save_launch_json(args.config, new_launch)
    else:
        # If there is one, but there are no differences, we don't need to do anything
        # otherwise, we need to update the launch.json and save it.
        if len(diffs):
            launch['configurations'][0].update(new_launch['configurations'][0])

            # Show the differences
            for key, (default, current) in diffs:
                print(f"\t{key}: {default} -> {current}")

            # Save the new launch.json
            save_launch_json(args.config, launch)

if __name__ == "__main__":
    main()