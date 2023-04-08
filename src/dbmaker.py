import subprocess
import shutil
import glob
import os

from utils import get_temp_dir

POSSIBLE_KEYS = {
    'FILENAME': 'filename', ## checked
    'NAME': 'pkgname', ## checked
    'BASE': 'pkgbase', ## checked
    'VERSION': 'pkgver', ## checked
    'DESC': 'pkgdesc', ## checked
    'GROUPS': 'group', ### NOT CHECKED
    'CSIZE': 'csize', ## checked
    'ISIZE': 'size', ## checked
    'MD5SUM': 'md5sum', ## checked
    'SHA256SUM': 'sha256sum', ## checked
    'PGPSIG': 'pgpsig', ## checked
    'URL': 'url', ## checked
    'LICENSE': 'license', ## checked
    'ARCH': 'arch', ## checked
    'BUILDDATE': 'builddate', ## checked
    'PACKAGER': 'packager', ## checked
    'REPLACES': 'replaces', ### NOT CHECKED
    'CONFLICTS': 'conflict', ## checked
    'PROVIDES': 'provides', ## checked
    'DEPENDS': 'depend', ## checked
    'OPTDEPENDS': 'optdepend', ## checked
    'MAKEDEPENDS': 'makedepend', ## checked
    'CHECKDEPENDS': 'checkdepend', ### NOT CHECKED
}

class DBEntry:
    def __init__(self, pkg_path, skip_md5=False) -> None:
        self.__path = os.path.expanduser(pkg_path)
        self.__skip_md5 = skip_md5
        self.__info = self.__read_pkginfo()
        self.__info['filename'] = os.path.basename(self.__path)
        self.__info.update(self.__get_extra_info())
    
    def __read_pkginfo(self):
        output = subprocess.check_output(['bsdtar', '-xOqf', self.__path, '.PKGINFO']).decode('utf-8')
        output = [i.strip() for i in output.split('\n') if i.strip() and not i.startswith('#')]
        info = {}
        for i in output:
            key, value = i.split('=', 1)
            key, value = key.strip(), value.strip()
            info[key] = info.get(key, [])
            info[key].append(value)
        
        for key, value in info.items():
            info[key] = value[0] if len(value) == 1 else '\n'.join(value)
        return info
    
    def __get_extra_info(self):
        info = {}
        info['csize'] = os.path.getsize(self.__path)
        info['pgpsig'] = subprocess.check_output(['base64', '-w0', self.__path + '.sig']).decode('utf-8')
        info['sha256sum'] = subprocess.check_output(['sha256sum', self.__path]).decode('utf-8').split(' ', 1)[0]
        if not self.__skip_md5:
            info['md5sum'] = subprocess.check_output(['md5sum', self.__path]).decode('utf-8').split(' ', 1)[0]
        return info

    def get_pkg_desc(self):
        desc = ''
        for k, v in POSSIBLE_KEYS.items():
            if v in self.__info:
                desc += f'%{k}%\n{self.__info[v]}\n\n'
        return desc
    
    def get_pkg_files(self):
        output =  subprocess.check_output(['bsdtar', '--exclude=^.*', '-tf', self.__path]).decode('utf-8')
        output = [i.strip() for i in output.split('\n') if i.strip()]
        output.sort()
        return '%FILES%\n' + '\n'.join(output) + '\n'
    
    @property
    def pkgname(self):
        return self.__info['pkgname']
    
    @property
    def pkgver(self):
        return self.__info['pkgver']


class DBMaker:
    def __init__(self, repo_dir:str, repo_name:str, **kwargs) -> None:
        self.__repo_dir = os.path.expanduser(repo_dir)
        self.__repo_name = repo_name
        self.__skip_md5 = kwargs.get('skip_md5', False)
        self.__temp_dir = get_temp_dir()
    
    def make_db(self):
        db = []
        for pkg in glob.glob(os.path.join(self.__repo_dir, '*.pkg.tar.zst')):
            db.append(DBEntry(pkg, self.__skip_md5))
        pkg_db = os.path.join(self.__temp_dir, 'pkgdb')
        
        os.makedirs(pkg_db)
        
        for pkg in db:
            pkg_dir = os.path.join(pkg_db, pkg.pkgname + '-' + pkg.pkgver)
            os.mkdir(pkg_dir)
            with open(os.path.join(pkg_dir, 'desc'), 'w') as f:
                f.write(pkg.get_pkg_desc())
        
        files_db = os.path.join(self.__temp_dir, 'filesdb')
        subprocess.check_call(['cp', '-a', pkg_db, files_db])

        for pkg in db:
            with open(os.path.join(files_db, pkg.pkgname + '-' + pkg.pkgver, 'files'), 'w') as f:
                f.write(pkg.get_pkg_files())
        
        call_list = [
            'bsdtar',
            '--uid', '0',
            '--gid', '0',
            '-czf',
            os.path.join(self.__repo_dir, f'{self.__repo_name}.db'),
            '-C',
            pkg_db,
            '.'
        ]
        subprocess.check_call(call_list)
        call_list[-4] = os.path.join(self.__repo_dir, f'{self.__repo_name}.files')
        call_list[-2] = files_db
        subprocess.check_call(call_list)
        shutil.rmtree(self.__temp_dir)
