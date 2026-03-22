#!/usr/bin/env python3

import os
import runpy

project_root = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(project_root, "contractG", "src", "launcher.py"), run_name="__main__")
