#!/usr/bin/env python3
from copy import deepcopy
import json
import argparse
import os


DEFAULT_LAUNCH_DICT = {
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


class CodeLaunchJson:
    """ This class is an OOP implementation of the functions above. """
    def __init__(self, json_path):
        self.json_path = json_path
        self._launch = None

        self.load(json_path)

    def load(self, json_path=None):
        """ Update the json path and load the json. """
        json_path = self.__check_json_path(json_path)

        with open(json_path, 'r') as f:
            self._launch = json.load(f)

        return self

    def save(self, json_path=None):
        """ Save the launch object to the launch.json file. """
        json_path = self.__check_json_path(json_path)

        with open(json_path, 'w') as f:
            json.dump(self._launch, f, indent=2)

    def diff(self, other):
        """
            See DEFAULT_LAUNCH above for an example of the format VSCode uses.

            This function will compare the two launch dicts and yield the differences.
        """ 
        other = self.__check_other(other)                

        for key, value in self._launch['configurations'][0].items():
            if other['configurations'][0][key] != value:

                yield key, (value, other['configurations'][0][key])

    def update_keys(self, **kwargs):
        """ Update the launch.json with the given kwargs. """
        for key, value in kwargs.items():
            if key in self._launch['configurations'][0]:
                self._launch['configurations'][0][key] = value
        
        return self

    def update(self, other):
        """ Update the launch.json with the values from other. """
        other = self.__check_other(other)

        self.update_keys(**other['configurations'][0])

        return self

    def build(self, module=None, env_root=None, env_name=None, python=None):
        """ Build the launch configuration for the given module. """
        self._launch = deepcopy(DEFAULT_LAUNCH_DICT)
        if module:
            self._launch['configurations'][0]['module'] = module

            print(f"Using module: {self._launch['configurations'][0]['module']}")

        if env_root and env_name and python:
            if env_root.startswith("~"):
                env_root = os.path.expanduser(env_root)
                
            env = f"{env_root}/.{env_name}"

            self._launch['configurations'][0]['pythonPath'] = f"{env}/bin/{python}"
            self._launch['configurations'][0]['env']['PYTHONPATH'] = f"{env}/lib/{python}/site-packages"

            print(f"Using python path: {self._launch['configurations'][0]['pythonPath']}")

        return self

    def __check_other(self, other):
        if isinstance(other, CodeLaunchJson):
            return other._launch
        elif not isinstance(other, dict):
            raise TypeError("other must be a dict or CodeLaunchJson object.")
        elif 'configurations' not in other:
            raise KeyError("other must have a 'configurations' key.")
        
        return other

    def __check_json_path(self, json_path):
        if json_path is None:
            json_path = self.json_path
        
        if json_path is None:
            raise ValueError("json_path must be set.")

        return json_path

    def __str__(self) -> str:
        # print launch dict pretty
        return json.dumps(self._launch, indent=2)

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

    # If the config file is not an absolute path, we need to make it one
    # if not os.path.isabs(args.config):
    #     args.config = os.path.join(os.getcwd(), args.config)

    # Get current launch.json
    try:
        launch = CodeLaunchJson(args.config)
    except FileNotFoundError:
        launch = None

    # Create new launch.json
    new_launch = CodeLaunchJson(args.config).build(module=args.module, env_root=args.env_root, env_name=args.env_name, python=args.python)
    diffs = list(new_launch.diff(launch))

    # If there is no launch.json, we simply need to create one
    if launch is None:
        new_launch.save()
    else:
        # If there is one, but there are no differences, we don't need to do anything
        # otherwise, we need to update the launch.json and save it.
        if len(diffs):
            launch.update(new_launch)
            launch.save()

            # Show the differences
            for key, (default, current) in diffs:
                print(f"\t{key}: {default} -> {current}")

          
            

if __name__ == "__main__":
    main()