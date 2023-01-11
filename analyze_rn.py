"""
Module containing the Analyzer implementation for filtering React Native packages.

The filter will scan through the native library folder (/lib) within the APK and search for occurences
of 'react_native' or 'reactnative' in file names case insensitively. If either is found, the APK is flagged
as dangerous.
"""

from zipfile import ZipFile
from analyze import IAnalyzer
import os

class RNAnalyzer(IAnalyzer):
    
    def check_apk_dangerous(self, apk: ZipFile) -> bool:
        for finfo in apk.filelist:
            if (finfo.filename.startswith("lib/")):
                basename = os.path.basename(finfo.filename).lower()
                if ("react_native" in basename or "reactnative" in basename): #e.g. libreactnativejni or libreact_native_jni
                    return True

        return False

    @staticmethod
    def get_tag() -> str:
        return 'react'