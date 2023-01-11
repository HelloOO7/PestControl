"""
Module for converting ADB output into friendlier Python objects.

Currently, this is implemented as a class that uses AdbDriver to
communicate with the ADB executable, calling its commands when functions
request it to and returning ADB's standard output as a function-specific
object that is easier to handle than a basic string.

It also provides shortcuts for imperative commands (uninstall, pull) for use
through native Python methods instead of building CLI parameters.
"""

from adb_driver import AdbDriver

class AdbControl:
    """
    High-level interface for obtaining application data over ADB.
    """

    driver: AdbDriver

    def __init__(self, driver: AdbDriver) -> None:
        """
        Binds a new AdbControl instance onto an ADB driver.
        """
        self.driver = driver

    def poll_devices(self) -> list[str]:
        """
        Polls ADB for devices and returns their serial IDs as a list.
        """
        out = list()
        stuff = self.driver.run_command("devices").split("\n")
        for i in range(1, len(stuff)):
            if (stuff[i].strip() == ""):
                continue
            params = stuff[i].split()
            out.append(params[0])
        return out

    @staticmethod
    def __strip_package_str(s: str):
        """
        Internal method to remove "package:" prefix.
        """
        return s.strip()[len("package:"):]

    def get_package_list(self) -> list[str]:
        """
        Fetches a list of all Android packages on the target device.
        """
        out = list()
        for package in self.run_command("shell pm list packages").split():
            out.append(AdbControl.__strip_package_str(package))
        return out

    def get_package_paths(self, packageId) -> list[str]:
        """
        Gets the paths to a package's APK files.
        The list may contain multiple elements if the APK is split.
        """
        return list(AdbControl.__strip_package_str(x) for x in self.run_command("shell pm path " + packageId).split())

    def get_file_from_device(self, pathOnDevice, pathOnHost) -> None:
        """
        Downloads a local file from the target device onto a host filesystem path.
        """
        self.run_command("pull \"" + pathOnDevice + "\" \"" + pathOnHost + "\"")

    def uninstall_package(self, packageId) -> None:
        """
        Uninstalls a package from the target device by its ID.
        """
        self.run_command("uninstall " + packageId)

    def set_device(self, deviceaddr: str):
        """
        Sets a serial device address for subsequent ADB operations.
        """
        self.driver.device = deviceaddr

    def set_param(self, tag: str, value: object = None):
        """
        Sets a parameter or flag for subsequent operations. A value of None will treat "tag" as a standalone boolean flag.
        """
        self.driver.params[tag] = value

    def clear_params(self):
        """
        Removes all previously set (with set_param) parameters.
        """
        self.driver.params.clear()

    def run_command(self, command: str) -> str:
        """
        Executes a command directly.
        """
        return self.driver.run_command(command)