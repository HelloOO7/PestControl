"""
Base module for interfaces used by PestControl's expunge module.

This module contains the base class for all analyzers. It is technically not mandatory
thanks to duck typing (note: "thanks to" is a natural language element, I don't actually like duck typing),
but it is strongly encouraged to utilize it.
"""

from zipfile import ZipFile

class IAnalyzer:
    """
    PestControl Analyzer interface.
    """

    def check_apk_dangerous(self, apk: ZipFile) -> bool:
        """
        Performs an user defined filtering routine on the input APK and returns True if it is potentially dangerous/to be uninstalled.
        """
        return False

    @staticmethod
    def get_tag() -> str:
        """
        Gets the tag string which should be used as the filter's identifier in the CLI's analyze-mode parameter.
        """
        return ''