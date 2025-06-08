#!/usr/bin/env python3
"""查找依赖 NumPy 的包"""

import pkg_resources

for package in pkg_resources.working_set:
    try:
        requires = package.requires()
        for req in requires:
            if "numpy" in req.name.lower():
                print(f"{package.project_name} depends on {req}")
    except Exception as e:
        print(f"Error checking {package.project_name}: {e}")