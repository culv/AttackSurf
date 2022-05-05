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
    """
    APP_REQUIRED_INFO = {"DisplayName", "VersionMajor", "VersionMinor", "Publisher"}
    """
    TODO: This doesnt seem to get all the apps. Other places to look for installed apps in the Windows Registry?
        * 32bit apps
            `HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall`
        * current user apps?
            `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall`
            `HKEY_CURRENT_USER\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall`
            `HKEY_CURRENT_USER\SOFTWARE\RegisteredApplications`
    """
    # Enumerate through all subkeys in the `HKLM/SOFTWARE/Microsoft/Windows/CurrentVersion/Uninstall` key
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ) as uninstall_key:
        num_subkeys, _, _ = winreg.QueryInfoKey(uninstall_key)
        apps = []
        for i in range(num_subkeys):
            subkey_name = winreg.EnumKey(uninstall_key, i)
            # Each subkey should be an app whose name, version, and vendor we will grab
            with winreg.OpenKey(uninstall_key, subkey_name, 0, winreg.KEY_READ) as subkey:
                subkey_dict = winreg_key_to_dict(subkey)
                apps.append(subkey_dict)

        # To search for CVEs we need at least the name, version, and vendor of each app
        apps = [app for app in apps if APP_REQUIRED_INFO.issubset(set(app.keys()))]

        for app in apps:
            print(f"name={app['DisplayName']}, version={app['VersionMajor']}.{app['VersionMinor']}")
        print(len(apps))
        return apps

if __name__ == '__main__':
    _ = get_apps_from_winreg()