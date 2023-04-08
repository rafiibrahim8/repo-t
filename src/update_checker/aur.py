import requests

from ._common import UpdateCheckerCommon

class AURUpdateChecker(UpdateCheckerCommon):
    def __init__(self, packages):
        self.__packages = packages
        self.__dict = {}
        if packages:
            self.__prepare()
    
    def __prepare(self):
        url = 'https://aur.archlinux.org/rpc/?v=5&type=info'
        for i in self.__packages:
            url += f'&arg[]={i}'
        results = requests.get(url).json()['results']
        for i in results:
            lowered_key = zip(map(lambda x: x.lower(), i.keys()), i.values())
            self.__dict[i['Name']] = dict(lowered_key)
        
    @property
    def _dict(self):
        return self.__dict
