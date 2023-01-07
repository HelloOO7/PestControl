from zipfile import ZipFile
from analyze import IAnalyzer

class JSAnalyzer(IAnalyzer):
    
    def check_apk_dangerous(self, apk: ZipFile) -> bool:
        for finfo in apk.filelist:
            if (finfo.filename.endswith(".js")):
                return True

        return False