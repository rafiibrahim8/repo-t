import subprocess
import requests
import shutil
import os
import re

from ._common import UpdateCheckerCommon
from utils import get_temp_dir

class GitUpdateChecker(UpdateCheckerCommon):
    def __init__(self, git_url=None, pkgbuild_url=None):
        if(not pkgbuild_url and not git_url):
            raise ValueError('At least one of the arguments must be specified')
        self.__git_url = git_url
        self.__pkgbuild_url = pkgbuild_url
        self.__prepare()
    
    def __prepare(self):
        if self.__pkgbuild_url:
            try:
                self.__dict = self.__get_dict_from_pkgbuild()
            except:
                self.__dict = self.__get_dict_from_git()
        else:
            self.__dict = self.__get_dict_from_git()
    
    def __get_dict_from_pkgbuild(self):
        res = requests.get(self.__pkgbuild_url)
        assert res.status_code//100 == 2
        return self.__parse_pkgbuild(res.text)
    
    def __get_dict_from_git(self):
        temp_dir = get_temp_dir()
        subprocess.check_call(['git', 'clone', '-q', self.__git_url, temp_dir])
        temp_var = {}
        try:
            with open(os.path.join(temp_dir, 'PKGBUILD')) as f:
                temp_var = self.__parse_pkgbuild(f.read())
        finally:
            shutil.rmtree(temp_dir)
        return temp_var
    
    def __parse_pkgbuild(self, pkgbuild):
        name = re.findall(r'pkgname\s?=\s?([^\n\s#]+)', pkgbuild)[0].strip()
        version = re.findall(r'pkgver\s?=\s?([^\n\s#]+)', pkgbuild)[0].strip()
        pkgrel = re.findall(r'pkgrel\s?=\s?(\d{1,})', pkgbuild)[0].strip()
        return {name: {'version': f'{version}-{pkgrel}', 'name': name}}
    
    @property
    def _dict(self):
        return self.__dict
