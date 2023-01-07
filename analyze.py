from zipfile import ZipFile

class IAnalyzer:
    def check_apk_dangerous(self, apk: ZipFile) -> bool:
        return False