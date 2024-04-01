# - manage local file in tmp of system with last known version
# - provide last known version number 
# - auto update version from string at https://raw.githubusercontent.com/dimov-cz/python-panasonic-comfort-cloud/versionupdater/currentVersion.txt

import os
import requests
import time

class AppVersion:
    default_version = '1.20.1'
    update_url = 'https://raw.githubusercontent.com/dimov-cz/python-panasonic-comfort-cloud/versionupdater/currentVersion.txt'
    
    

    def __init__(self):
        self.version = self.default_version

        self.version_file = '/tmp/pcc_version.txt'
        self.version = self._get_saved_version()

    '''
    Get last known version from file. Checks for update if last check was more than 1 hour ago.
    '''
    def get_version(self):
        self._check_for_update()
        return self.version.strip()
    
    '''
    Force update of version file. Return True if new version was found, False otherwise.
    '''
    def force_update(self):
        return self._check_for_update(True)

    '''
    Get last known version from file.
    If file does not exist, return default version.
    '''
    def _get_saved_version(self):
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                return f.read().strip()
        else:
            # check for update if no file exists - fist run case
            if self._check_for_update():
                return self.version

        #fallback to default version if no file exists
        return self.default_version

    '''
    Check for update and save new version to file if available.
    Check for update only once per hour. Can be forced by setting force to True.
    Returns True if new version was found, False otherwise.
    ''' 
    def _check_for_update(self, force=False):
        if not force:
            #test mtime of version file, dont update if last update was less than 1 hour ago
            if os.path.exists(self.version_file):
                mtime = os.path.getmtime(self.version_file)
                if mtime + 3600 > time.time():
                    return False
            
        try:
            response = requests.get(self.update_url)
            response.raise_for_status()
            version = response.text.strip()
            if os.path.exists(self.version_file) and version == self.version:
                #update mtime is enough:
                os.utime(self.version_file)
            else:
                with open(self.version_file, 'w') as f:
                    f.write(version)
            
            self.version = version
            return True
        except requests.exceptions.RequestException:
            # TODO report? exception? silent error?
            # throw("Error while checking for update" + str(e))
            pass
            
        return False

    