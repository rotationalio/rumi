# rumi.version
# Maintains version and package information for deployment
#
# Author:   Tianshu Li
# Created:  Nov.19 2021

"""
Maintains version and package information for deployment
"""

##########################################################################
## Module Info
##########################################################################

__version_info__ = {
    "major": 0,
    "minor": 0,
    "micro": 1,
    "releaselevel": "alpha",
    "post": 8,
    "serial": 1,
}

##########################################################################
## Helper Functions
##########################################################################


def get_version(short=False):
    """
    Prints the version.
    """
    assert __version_info__["releaselevel"] in ("alpha", "beta", "final")
    vers = ["{major}.{minor}".format(**__version_info__)]

    if __version_info__["micro"]:
        vers.append(".{micro}".format(**__version_info__))

    if __version_info__["releaselevel"] != "final" and not short:
        vers.append(
            "{}{}".format(
                __version_info__["releaselevel"][0],
                __version_info__["serial"],
            )
        )

    if __version_info__["post"]:
        vers.append(".post{}".format(__version_info__["post"]))

    return "".join(vers)