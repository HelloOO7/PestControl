"""
Main module of the PestControl program.

This module can be run from the command line and used to uninstall packages filtered through
its underlying analyzers from the target device.

Command line parameters can be used to fine-tune the behavior of the program, but running it without
any user input is also possible, baring situations when there are multiple devices connected, in which
the program will prompt the user to select a device.
"""

import os
import platform
import shutil
import adb_driver
import argparse
import sys
from zipfile import ZipFile
from zipfile import BadZipFile
from adb_control import AdbControl

import analyze

#imports for ANALYZERS mapping
from analyze_js import JSAnalyzer
from analyze_rn import RNAnalyzer

import sys

def is_debug() -> bool:
    return hasattr(sys, 'gettrace') and sys.gettrace() != None

PLATFORM_WIN32 = any(platform.win32_ver())
DEBUG = is_debug()
ACCESSIBLE_APP_PREFIX = "/data/app"

TMPDIR_NAME = "temp"

ANALYZERS = {}

for analyzer_class in analyze.IAnalyzer.__subclasses__():
    ANALYZERS[analyzer_class.get_tag()] = analyzer_class()

DEFAULT_PARAMS = {
    'adbpath': 'adb',
    'device': None,
    'keep-temp-dir': False,
    'analyze-mode': 'react',
    'analyze-only': False,
    'gracelist': None
}

DEBUG_PARAMS = {
    'adbpath': 'adb',
    'device': None,
    'keep-temp-dir': True,
    'analyze-mode': 'react',
    'analyze-only': True,
    'gracelist': 'gracelist.txt'
}

if (DEBUG):
    print("[Running in debug mode]")

params = DEBUG_PARAMS if DEBUG else DEFAULT_PARAMS

def parse_args():
    parser = argparse.ArgumentParser(
        prog="expunge.py",
        epilog="PestControl Universal Android Webdev Trash Expunger (C) ČŘ @ MFF 2022/2023"
    )
    parser.add_argument("--adb-path", type=str, default=params['adbpath'], help="Path to the ADB executable.")
    parser.add_argument("-d", "--device", type=str, default=params['device'], help="Specify the device to target over ADB.")
    parser.add_argument("-m", "--analyze-mode", type=str, default=params['analyze-mode'], help="List of filters for analysis, chained with the OR (|) operator. (f. e. react|js)")
    parser.add_argument("-g", "--gracelist", type=str, default=params['device'], help="Path to a file with package IDs (as separate lines) to never uninstall (f. e. mobile banking apps).")
    parser.add_argument("--keep-temp-dir", default=params['keep-temp-dir'], action='store_true', help="Do not delete the temp directory on exit.")
    parser.add_argument("--analyze-only", default=params['analyze-only'], action='store_true', help="Analyze, but do not uninstall anything.")
    args = parser.parse_args()
    params['adbpath'] = args.adb_path
    params['device'] = args.device
    params['analyze-mode'] = args.analyze_mode
    params['gracelist'] = args.gracelist
    params['keep-temp-dir'] = args.keep_temp_dir
    params['analyze-only'] = args.analyze_only

def create_analyzer_instances() -> list:
    analyzers = []
    for analyzer_name in params['analyze-mode'].split('|'):
        analyzers.append(ANALYZERS[analyzer_name])
    return analyzers

def read_gracelist(path: str) -> set:
    gracelist = set()
    if (path != None):
        with open(path) as file:
            for line in file:
                gracelist.add(line.rstrip())

    return gracelist

def request_device_selection(adb: AdbControl):
    devices = adb.poll_devices()
    if (len(devices) == 0):
        raise Exception("No devices found!")
    
    selDev = 0
    if (len(devices) != 1):
        print("Please select the target device (default = [0]):")
        devIndex = 0
        for device in devices:
            print(f"[{devIndex}]: {device}")
            devIndex += 1

        selDev = -1
        while (selDev == -1):
            try:
                selDev = int(input())
                if (selDev >= len(devices) or selDev < 0):
                    print("Invalid index!")
                    selDev = -1
            except ValueError:
                print("Not a valid number!")

    adb.set_device(devices[selDev])

def safe_uninstall(packageId: str, adb: AdbControl):
    try:
        print("Uninstalling", packageId)
        adb.uninstall_package(packageId)
        pass
    except Exception:
        print("Failed to uninstall " + packageId + "!")

def analyze_package(zip: ZipFile, analyzers: list) -> tuple[bool, object]:
    for analyzer in analyzers:
        if (analyzer.check_apk_dangerous(zip)):
            return (True, analyzer)
    return (False, None)

def scan_packages(pkglist: list[str], adb: AdbControl, analyzers: list, analyze_only:bool = False, gracelist: list[str] = []):
    pkgIndex = 0
    for pkg in pkglist:
        print("Processing package", pkg, "(" + str(pkgIndex) + "/" + str(len(pkglist)) + ")")
        pkgPaths = adb.get_package_paths(pkg)
        index = 0
        for pkgPath in pkgPaths:
            if (pkgPath.startswith(ACCESSIBLE_APP_PREFIX)): #some apps keep split code in /mnt/asec, which we can not access
                tmpfile = os.path.join(TMPDIR_NAME, pkg + ("" if index == 0 else "-" + str(index)) + ".apk")
                if not os.path.exists(tmpfile): #do not needlessly pull files that we've already pulled
                    adb.get_file_from_device(pkgPath, tmpfile)

                dangerous = False
                zip:ZipFile = None
                try:
                    zip = ZipFile(tmpfile)
                except BadZipFile:
                    print("Could not open APK " + tmpfile + " as ZIP file!! Skipping...")

                if (zip != None):
                    analysis_result = analyze_package(zip, analyzers)
                    dangerous = analysis_result[0]
                    if (dangerous):
                        print("Analyzer", analysis_result[1].__class__.__name__, "deemed application", pkg, "to be dangerous.")
                    
                    if ((not analyze_only) and dangerous):
                        if pkg not in gracelist:
                            safe_uninstall(pkg, adb)
                        else:
                            print("However, as the package is present in the gracelist, it will not be uninstalled.")

                if (dangerous):
                    break #already uninstalled, pointless to continue

                index += 1
        pkgIndex += 1

def cli_main():
    driver = adb_driver.AdbDriver(params['adbpath'])
    driver.commandDebug = DEBUG
    if not driver.test():
        raise Exception("ADB backend is broken!")

    analyzers = create_analyzer_instances()
    gracelist = read_gracelist(params['gracelist'])

    analyze_only = params['analyze-only'] == True

    adb = AdbControl(driver)

    if params['device'] != None:
        print("Using device ", params['device'])
        adb.set_device(params['device'])
    else:
        request_device_selection(adb)

    # device selection done

    adb.set_param("3") #can only uninstall 3rd party apps without superuser
    pkglist = adb.get_package_list()
    adb.clear_params()

    scan_packages(pkglist, adb, analyzers, analyze_only, gracelist)

def cli_wrapper():
    parse_args()

    if not os.path.exists(TMPDIR_NAME):
        os.mkdir(TMPDIR_NAME)

    try:
        cli_main()
    finally:
        if (params['keep-temp-dir'] == False):
            shutil.rmtree(TMPDIR_NAME)
        pass

cli_wrapper()