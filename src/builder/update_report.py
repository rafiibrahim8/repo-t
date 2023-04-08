import os

from ..update_checker import RepoUpdateChecker

class UpdateReport:
    def __init__(self, local_db_path):
        self.__local_db = RepoUpdateChecker(local_db_path)
    
    def report(self):
        report = {}
        
