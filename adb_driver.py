"""
Module for interfacing with the Android Debug Bridge (ADB) executable from Python.

This is no more than a helper for creating an OOP handle over the native subprocess,
with some neat extensions like a state machine for remembering CLI switches.

The expunge module uses this for all ADB communication.
"""
import subprocess

class AdbDriver:
    """
    Class for interfacing with the Android SDK Debug Bridge executable.
    """
    adbExecutablePath: str
    device: str
    params: dict
    commandDebug: bool

    def __init__(self, adbExecutablePath: str) -> None:
        """
        Constructs an ADB driver using a path to a native ADB executable.
        """
        self.adbExecutablePath = adbExecutablePath
        self.device = None
        self.params = {}
        self.commandDebug = False

    def __build_runcommand(self, command: str) -> str:
        """
        Internal method to construct an ADB command.
        """
        out = self.adbExecutablePath
        if (self.device != None):
            out += " -s " + self.device
        out += "" if command == None else " " + command

        for arg, value in self.params.items():
            out += " "
            out += ("-" if len(arg) == 1 else "--") + arg
            if (value != None):
                out += " " + value
        
        return out

    def run_command(self, command: str, expected_retcode=0) -> str:
        """
        Runs an ADB command, throwing an exception if the return code doesn't match an expected value.
        """
        runcmd = self.__build_runcommand(command)
        if (self.commandDebug):
            print("Executing", runcmd)
        process = subprocess.Popen(runcmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        retval = process.communicate()
        if (process.returncode != expected_retcode):
            raise Exception("ADB failed with exit code " + str(process.returncode) + " stderr " + str(retval[1]))

        return str(retval[0])

    def test(self) -> bool:
        """
        Checks if the ADB executable is valid and working.
        """
        try:
            self.run_command(None, 1)
            return True
        except Exception as e:
            print("ADB test failed: " + str(e))
            return False
