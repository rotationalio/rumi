# rumi
# Static site translation monitoring
#
# Author: Tianshu Li
# Created: Oct 28, 2021

"""
A static site translation monitoring tool that reads github history,
identifies new source files and displays the translation needs.
"""

##########################################################################
# Imports
##########################################################################

from rumi.file_rumi import reader
from rumi.file_rumi import reporter
