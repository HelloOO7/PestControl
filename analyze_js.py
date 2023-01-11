"""
Module containing the Analyzer implementation for filtering packages containing JavaScript resources.

This is more of a tech demo than an actual filter, as there are valid reasons for including JS files
in APKs (for example webview extensions), however, it can serve as a straightforward reference implementation
of IAnalyzer.
"""

from zipfile import ZipFile
from analyze import IAnalyzer

class JSAnalyzer(IAnalyzer):
    
    def check_apk_dangerous(self, apk: ZipFile) -> bool:
        for finfo in apk.filelist:
            if (finfo.filename.endswith(".js")):
                return True

        return False

    @staticmethod
    def get_tag() -> str:
        return 'jsfile'