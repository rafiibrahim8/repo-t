class UpdateCheckerCommon:
    def get_all(self, package_name):
        return self._dict.get(package_name)
    
    def get(self, package_name, section_name):
        return self._dict.get(package_name, {}).get(section_name)
    
    def get_version(self, package_name):
        return self.get(package_name, 'version')
    
    def get_full_dict(self):
        return self._dict
