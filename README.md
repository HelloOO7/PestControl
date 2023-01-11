# PestControl Universal Android Webdev Trash Expunger

PestControl is a simple Python program that is, at its core, designed to allow scanning and filtering application packages on a remote Android device,
and uninstalling them if a filter is triggered. However, its surface-level purpose is to use that functionality to purge your mobile device of sin,
i. e. applications that were built using the React Native framework. If you want to, though, you could make it remove all Adobe apps or everything that
starts with S. Imagination is the only limit!

## Requirements

- Python 3.x runtime (not quite sure which one at minimum, but 3.10 is sure to work).
- ADB executable and AdbWinApi + AdbWinUsbApi DLLs if on Windows.
- Android device (root not required) with USB debugging enabled.
- A keyboard.

## Usage guide

Using PestControl could not be more easy! First, obviously, you need to set up your device and environment:

1. Download the Android SDK or another ADB distribution and either add the executable to your PATH, or copy it to PestControl's root directory. Alternatively,
you can also specify the ADB path using a command line parameter, however, is isn't recommended outside of embedded contexts.
2. On your mobile device, activate USB debugging and connect it *over USB* (not wireless) to your computer. Trust the RSA fingerprint if necessary.
3. Open a shell and run `adb devices`. If you did everything right, your device will be listed in the output. Otherwise, check you have the proper drivers installed and that
there isn't another ADB server running.

Afterwards, you can simply run the expunge module, that is:

```
py -3 expunge.py <args>
```

If you don't provide any arguments, PestControl will automatically connect to your device (or prompt a selection if more than one are connected) and mercilessly uninstall all
React Native based applications. If you want to modify that behavior, you can:

- Use the `-g` or `--gracelist` parameter to specify a list of programs that should never be uninstalled regardless of the filters' verdict. The list should be a newline-separated plain text file with the package IDs (f.e. `com.skype.raider`) of the APKs to be spared.
- Change the `--analyze-mode` to use a different filter than React Native. If you added your own custom filter (see below), this is where you'd put its tag. You can also combine multiple filters together with the OR operator, as in `filter1|filter2`. This will uninstall the app if *either* of the filters is triggered. Don't get too excited, though, it's just the OR operator. No AND, no XOR. Wouldn't make much sense, really.
- Set `--analyze-only` to only scan your device without uninstalling any packages. Useful for previewing results and making sure that everything is in order. If you want to speed up the subsequent run without the flag set, you can also use `--keep-temp-dir` to not delete the pulled APKs directory after scan, which will prevent PestControl from redownloading the packages with every iteration.
- Specify additional parameters if you really want everything tailored to your own configuration. That is:
    - `--adb-path` - absolute or relative (or system) path to the ADB executable to be driven by PestControl. Most of the time this can be left as is with the default value of `adb`.
    - `-d` or `--device` - if you have multiple devices connected and don't want to go through the selection prompt (such as when using a batch file), you can use this parameter to specify the serial device ID of the one to be used by PestControl.

## Custom filters

Should you desire to use a custom filter for any reason:

1. Declare it in a new module as a child class of `analyze.IAnalyzer` and implement the `check_apk_dangerous` and `get_tag` methods according to their documentation.
2. Go to expunge.py and import the new class (`from your_module import YourIAnalyzerSubclass`) in the `#imports for ANALYZERS mapping` block.
3. Now use 'tag' as a parameter to `analyze-mode` to use your filter during analysis!