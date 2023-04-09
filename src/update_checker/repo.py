import subprocess
import shutil
import os

from utils import get_temp_dir
from ._common import UpdateCheckerCommon

class DescParser:
    def __init__(self, desc_path):
        with open(os.path.expanduser(desc_path), 'r') as f:
            self.__parse(f.read())
    
    def __parse(self, desc):
        self.__dict = {}
        desc = [i.strip() for i in desc.split('\n\n') if i.strip()]
        for i in desc:
            name, values = self.__parse_section(i)
            self.__dict[name] = values
    
    def __parse_section(self, section):
        section = [i.strip() for i in section.split('\n') if i.strip()]
        section_name = section[0].lower().strip('%')
        section = section[1:]
        return section_name, section[0] if len(section) == 1 else section
    
    def get(self, section_name):
        return self.__dict.get(section_name)
    
    def get_all(self):
        return self.__dict
    
    def get_name(self):
        return self.get('name')
    
    def get_version(self):
        return self.get('version')


class RepoUpdateChecker(UpdateCheckerCommon):
    def __init__(self, repo_db_url):
        self.__repo_db_url = repo_db_url
        self.__temp_dir = get_temp_dir()
        self.__prepare()
    
    def __prepare(self):
        self.__dict = {}
        try:
            self.__prepare_impl()
        finally:
            shutil.rmtree(self.__temp_dir)
    
    def __prepare_impl(self):
        if self.__repo_db_url.startswith('https://') or self.__repo_db_url.startswith('http://'):
            subprocess.check_call(['curl', '-Lso', os.path.join(self.__temp_dir, 'repo.db'), self.__repo_db_url])
        else:
            if not os.path.exists(self.__repo_db_url):
                return
            shutil.copy(self.__repo_db_url, os.path.join(self.__temp_dir, 'repo.db'))
        
        subprocess.check_call(['bsdtar', '-xf', os.path.join(self.__temp_dir, 'repo.db'), '-C', self.__temp_dir])
        os.remove(os.path.join(self.__temp_dir, 'repo.db'))
        for dir in os.listdir(self.__temp_dir):
            desc_path = os.path.join(self.__temp_dir, dir, 'desc')
            parser = DescParser(desc_path)
            self.__dict[parser.get_name()] = parser.get_all()
    
    @property
    def _dict(self):
        return self.__dict

