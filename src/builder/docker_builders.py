import docker
import base64
import shutil
import os

from utils import logger, get_temp_dir
from errors import BuildFailedError

INIT_COMMAND = '''
pacman -Syu --noconfirm
pacman -S --noconfirm --needed git sudo base-devel
useradd -m -c 'Package Builder' -s /bin/bash builder  
echo 'builder ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers.d/builder
curl https://gist.githubusercontent.com/rafiibrahim8/e2734d312c086db757d12fd1c8367e11/raw/5236970d62b8c8f4ff0ce25c543dcf7e14689317/makepkg.conf -o /etc/makepkg.conf
echo PACKAGER='"###NAME### <###EMAIL###>"' >> /etc/makepkg.conf
echo PKGDEST=/output >> /etc/makepkg.conf
chown -R builder:builder /output
'''

class _Builder:
    def __init__(self, packer_name, packger_email, output_dir):
        self.__output_dir = os.path.expanduser(output_dir)
        self.__client = docker.from_env()
        self.__init_command = INIT_COMMAND.replace('###NAME###', packer_name).replace('###EMAIL###', packger_email)
        self.__temp_dir = get_temp_dir()
        os.makedirs(self.__output_dir, exist_ok=True)

    def build(self):
        raise NotImplementedError('Should be implemented by subclass')

    def __process_command(self, command):
        command = [i.strip() for i in command.split('\n') if i.strip() and not i.strip().startswith('#')]
        command.append(f'sudo chown -R {os.getuid()}:{os.getgid()} /output')
        command = '\n'.join(command) + '\n'

        processed = self.__init_command + '\n' + \
        f'sudo -u builder bash -c \'echo {base64.b64encode(command.encode("utf-8")).decode("utf-8")} | base64 -d | bash\'\n'
        processed = 'echo ' + base64.b64encode(processed.encode('utf-8')).decode('utf-8') + ' | base64 -d | bash'
        return f'bash -c "{processed}"\n'

    def _run(self, command):
        command = self.__process_command(command)
        logger.debug(f'Running command: {command}')
        streamer = self.__client.containers.run('archlinux:latest', command, remove=True, stdout=True,stream=True,detach=True, volumes=[f'{self.__temp_dir}:/output'])
        logger.debug('Command output:')
        for line in streamer.logs(stream=True):
            logger.info(line.decode('utf-8').strip())
        files = os.listdir(self.__temp_dir)
        if len(files) == 0:
            raise BuildFailedError('No files found in output directory')
        for file in files:
            shutil.move(os.path.join(self.__temp_dir, file), self.__output_dir)
        shutil.rmtree(self.__temp_dir)

class GitBuilder(_Builder):
    def __init__(self, packager_name, packger_email, output_dir, pkgbuild_git_url):
        super().__init__(packager_name, packger_email, output_dir)
        self.__pkgbuild_git_url = pkgbuild_git_url
    
    def build(self):
        logger.info(f'Building {self.__pkgbuild_git_url}')
        build_command = f'''
        cd /home/builder
        git clone {self.__pkgbuild_git_url}
        cd {self.__pkgbuild_git_url.split('/')[-1].split('.')[0]}
        makepkg --syncdeps --clean --needed --noconfirm
        '''
        self._run(build_command)

class AURBuilder:
    def __init__(self, packager_name, packger_email, output_dir, aur_package_name):
        if(aur_package_name.startswith('https://aur.archlinux.org/')):
            aur_package_name = aur_package_name.split('/')[-1].split('.')[0]
        aur_package_url =  f'https://aur.archlinux.org/{aur_package_name}.git'
        self.__pkgbuilder = GitBuilder(packager_name, packger_email, output_dir, aur_package_url)
    
    def build(self):
        return self.__pkgbuilder.build()
