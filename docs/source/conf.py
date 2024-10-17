# -*- coding: utf-8 -*-
import os
import sys

project = "CLI"
copyright = "2024, Rapyuta Robotics"
author = "Rapyuta Robotics"

sys.path.insert(0, os.path.abspath("../.."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.ifconfig",
    "sphinx_click",
]

templates_path = ["_templates"]
autosummary_generate = True  # Turn on sphinx.ext.autosummary
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = []
todo_include_todos = False

html_theme = "furo"
html_favicon = "favicon.ico"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo-light-mode.svg",
    "dark_logo": "logo-dark-mode.svg",
}
html_css_files = ["css/rio-sphinx.css"]
html_js_files = ["js/rio-sphinx.js"]
htmlhelp_basename = "RIOdoc"
man_pages = [(master_doc, "cli", "Rapyuta IO CLI", [author], 1)]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
add_module_names = False
