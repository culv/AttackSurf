from common import App

import json
import subprocess
import winreg

def winreg_key_to_dict(key):
    """ Converts a Windows Registry key to a dictionary containing its value names and corresponding data
    Args:
        key (winreg.HKEYType) = The Windows Registry key whose values are being gathered
    Returns:
        key_dict (dict) = Dictionary of the value names and data of the Windows Registry key
    """
    _, num_values, _ = winreg.QueryInfoKey(key)
    key_dict = {}
    for i in range(num_values):
        value_name, value_data, data_type = winreg.EnumValue(key, i)
        key_dict[value_name] = value_data
    return key_dict

def get_apps_from_winreg():
    """ Get all installed apps we can find in the Windows Registry, including app name, version, and vendor
    Args:
    Returns:
        apps (list[App]) = A list of App instances for all installed apps in the Windows Registry
    """
    APP_REQUIRED_INFO = {"DisplayName", "DisplayVersion", "Publisher"}
    """
    TODO: This doesnt seem to get all the apps. Other places to look for installed apps in the Windows Registry?
        * current user apps?
            `HKEY_CURRENT_USER\SOFTWARE\RegisteredApplications`
    """
    WINREG_KEYS_TO_SEARCH = [
        {"hive": winreg.HKEY_LOCAL_MACHINE, "key": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"},
        {"hive": winreg.HKEY_LOCAL_MACHINE, "key": r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"},
        {"hive": winreg.HKEY_CURRENT_USER, "key": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"},
        # {"hive": winreg.HKEY_CURRENT_USER, "key": r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"}
    ]
    # Enumerate through all subkeys of the Windows Registry keys we want to search
    apps = []
    for entry in WINREG_KEYS_TO_SEARCH:
        with winreg.OpenKey(entry["hive"], entry["key"], 0, winreg.KEY_READ) as key:
            num_subkeys, _, _ = winreg.QueryInfoKey(key)
            for i in range(num_subkeys):
                subkey_name = winreg.EnumKey(key, i)
                # Each subkey should be an app whose name, version, and vendor we will grab
                with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ) as subkey:
                    subkey_dict = winreg_key_to_dict(subkey)
                    apps.append(subkey_dict)

    # To search for CVEs we need at least the name, version, and vendor of each app
    apps = [app for app in apps if APP_REQUIRED_INFO.issubset(set(app.keys()))]
    apps = [App(app["DisplayName"], app["Publisher"], app["DisplayVersion"]) for app in apps]
    return apps

def get_apps_from_app_packages():
    """ Get all installed apps we can find from app packages (.appx) [https://docs.microsoft.com/en-us/previous-versions//hh856044(v=technet.10)?redirectedfrom=MSDN]
    Args:
    Returns:
        apps (list[App]) = A list of App instances based on the app packages installed across all users
    """
    # Command to get the Name/Publisher/Version of all app packages in JSON format
    POWERSHELL_COMMAND = "Get-AppxPackage -AllUsers | Select Name, Publisher, Version | ConvertTo-Json"
    powershell_output = subprocess.run(["powershell", "-Command", POWERSHELL_COMMAND], capture_output=True)
    apps = json.loads(powershell_output.stdout)
    apps = [App(app["Name"], app["Publisher"], app["Version"]) for app in apps]
    return apps


if __name__ == '__main__':
    apps_from_app_packages = get_apps_from_app_packages()
    print(f"Apps from app packages: {len(apps_from_app_packages)}")
    for app in apps_from_app_packages:
        print(app.cpe)
    
    apps_from_windows_registry = get_apps_from_winreg()
    print(f"Apps from windows registry: {len(apps_from_windows_registry)}")
    for app in apps_from_windows_registry:
        print(app.cpe)