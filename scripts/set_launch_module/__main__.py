#!/usr/bin/env python3
import argparse
import os

from .codelaunch import CodeLaunchJson


def argparser():
    parser = argparse.ArgumentParser(description="Set the launch module for the current project.")
    parser.add_argument("module", help="The module to launch.", default=None)
    parser.add_argument("--env-root", help="The root of the virtual environment.", default=None)
    parser.add_argument("--env-name", help="The name of the virtual environment.", default=None)
    parser.add_argument("--python", help="The python executable to use.", default=None)
    parser.add_argument("--config", help="The config file to use. Mostly for testing purposes.", default=None)
    
    return parser


def script_args(args):
    # Launch defaults
    l_defs = {
        "config": ".vscode/launch.json",
        "module": "vs_assembler",
        "env-root": "~",
        "env-name": "py311",
        "python": "python3.11"
    }

    # Environment launch defaults
    el_defs = {
        "config": ".vscode/launch.json",
        "module": os.getenv("VSA_LAUNCH_MODULE"),
        "env-root": os.getenv("VSA_ENV_ROOT"),
        "env-name": os.getenv("VSA_ENV_NAME"),
        "python": os.getenv("VSA_PYTHON")
    }

    # Argument launch defaults
    al_defs = {
        "config": args.config,
        "module": args.module,
        "env-root": args.env_root,
        "env-name": args.env_name,
        "python": args.python
    }

    args.module = al_defs["module"] or el_defs["module"] or l_defs["module"]
    args.env_root = al_defs["env-root"] or el_defs["env-root"] or l_defs["env-root"]
    args.env_name = al_defs["env-name"] or el_defs["env-name"] or l_defs["env-name"]
    args.python = al_defs["python"] or el_defs["python"] or l_defs["python"]
    args.config = al_defs["config"] or el_defs["config"] or l_defs["config"]

    return args


def main():
    print("Welcome to set_launch_module.py\n"
          "This script will set the launch.json to the correct\n"
          "module and python path for the current project.\n")
    # Process arguments
    args = script_args(argparser().parse_args())

    # Get current launch.json
    try:
        launch = CodeLaunchJson(args.config)
    except FileNotFoundError:
        launch = None

    # Create new launch.json
    if any([args.module, args.env_root, args.env_name, args.python]):
        new_launch = CodeLaunchJson(args.config).build(module=args.module, env_root=args.env_root, env_name=args.env_name, python=args.python)

    # Update the launch.json
    if launch is None:
        new_launch.save()
    elif new_launch is not None:
        launch.diff_and_saveupdate(new_launch)
    else:
        print("No changes needed.")

          
if __name__ == "__main__":
    main()