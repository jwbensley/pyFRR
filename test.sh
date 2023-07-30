#!/usr/bin/env

pylint ./pypaths/all_paths.py
# https://pylint.readthedocs.io/en/latest/

pydocstringformatter --max-summary-lines 2 ./pypaths/all_paths.py
#https://github.com/DanielNoord/pydocstringformatter
#https://pydocstringformatter.readthedocs.io/en/latest/usage.html
#https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists
