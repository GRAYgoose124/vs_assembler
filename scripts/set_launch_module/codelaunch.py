from copy import deepcopy
import functools
import json
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


def guarded_other(func):
    """ guarded_other wraps a CodeLaunchJson.method(self, other) to ensure that the other argument is a dict or CodeLaunchJson object."""
    @functools.wraps(func)
    def wrapper(self, other):
        if isinstance(other, CodeLaunchJson):
            return func(self, other._launch)
        elif not isinstance(other, dict):
            raise TypeError("other must be a dict or CodeLaunchJson object.")
        elif 'configurations' not in other:
            raise KeyError("other must have a 'configurations' key.")
        
        return func(self, other)
    return wrapper


class CodeLaunchJson:
    """ This class is an OOP implementation of the functions above. """
    def __init__(self, json_path=None):
        self.json_path = json_path
        self._launch = None

        self.load(json_path)

    def load(self, json_path):
        """ Update the json path and load the json. """
        with open(json_path, 'r') as f:
            self._launch = json.load(f)
    
        self.json_path = json_path
        return self

    def save(self):
        """ Save the launch object to the launch.json file. """
        with open(self.json_path, 'w') as f:
            json.dump(self._launch, f, indent=2)

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


    @guarded_other
    def diff(self, other):
        """
            See DEFAULT_LAUNCH above for an example of the format VSCode uses.

            This function will compare the two launch dicts and yield the differences.
        """ 

        for key, value in self._launch['configurations'][0].items():
            if other['configurations'][0][key] != value:

                yield key, (value, other['configurations'][0][key])

    def update_keys(self, **kwargs):
        """ Update the launch.json with the given kwargs. """
        for key, value in kwargs.items():
            if key in self._launch['configurations'][0]:
                self._launch['configurations'][0][key] = value
        
        return self

    @guarded_other
    def update(self, other):
        """ Update the launch.json with the values from other. """
        print("Updating launch.json...")
        self.update_keys(**other['configurations'][0])

        return self

    @guarded_other
    def diff_and_saveupdate(self, new):
        print("Diffing and saving...")
        diffs = list(self.diff(new))

        # If there is an original config, but there are no differences, we don't need to do anything
        # otherwise, we need to update the launch.json and save it.
        if len(diffs):
            self.update(new)
            self.save()

        # Show the differences
        for key, (s, n) in diffs:
            print(f"\t{key}: {s} -> {n}")
        
        return self

    def __eq__(self, other):
        return not any(self.diff(other))
    
    def __gt__(self, other):
        sum = 0
        for _, (a, b) in self.diff(other):
            sum += len(a) + len(b)
        
        return sum > 0

    def __str__(self) -> str:
        # print launch dict pretty
        return json.dumps(self._launch, indent=2)
