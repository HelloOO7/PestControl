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