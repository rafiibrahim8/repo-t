import gnupg
import os

class GPGSigner:
    def __init__(self, gnupghome, keyid):
        self.__gpg = gnupg.GPG(gnupghome=gnupghome)
        self.__keyid = keyid

    def sign(self, file_path, sig_path=None):
        file_path = os.path.expanduser(file_path)
        r = self.__gpg.sign_file(file_path, keyid=self.__keyid, detach=True, binary=True)
        assert r.fingerprint.endswith(self.__keyid), f'Can not sign wth key: {self.__keyid}'
        sig_path = sig_path or f'{file_path}.sig'
        sig_path = os.path.expanduser(sig_path)
        with open(sig_path, 'wb') as f:
            f.write(r.data)

class GPGVerifier:
    def __init__(self, gnupghome, keyid):
        self.__gpg = gnupg.GPG(gnupghome=gnupghome)
        self.__keyid = keyid
        self.__gpg.recv_keys('keyserver.ubuntu.com', keyid)

    def verify(self, file_path, sig_path=None):
        file_path = os.path.expanduser(file_path)
        sig_path = sig_path or f'{file_path}.sig'
        sig_path = os.path.expanduser(sig_path)
        with open(sig_path, 'rb') as f:
            r = self.__gpg.verify_file(f, file_path)
        if not r.valid:
            return False
        if not r.fingerprint.endswith(self.__keyid):
            return False
        return True

class GPG:
    def __init__(self, gnupghome=None):
        self.__gnupghome = gnupghome or os.environ.get('GPGHOME', './.gnupg')
        os.makedirs(self.__gnupghome, exist_ok=True)
    
    def signer(self, keyid):
        return GPGSigner(self.__gnupghome, keyid)
    
    def verifier(self, keyid):
        return GPGVerifier(self.__gnupghome, keyid)
    
    def get_default_keyid(self):
        gpg = gnupg.GPG(gnupghome=self.__gnupghome)
        return gpg.list_keys()[0]['keyid']

class Resigner:
    def __init__(self, signkeyid, gpghome):
        self.__gpg = GPG(gpghome)
        self.__keyid = signkeyid

    def resign(self, file_path, old_sig_path, old_keyid, new_sig_path):
        file_path = os.path.expanduser(file_path)
        old_sig_path = os.path.expanduser(old_sig_path)
        new_sig_path = os.path.expanduser(new_sig_path)
        self.__gpg.verifier(old_keyid).verify(file_path, old_sig_path)
        self.__gpg.signer(self.__keyid).sign(file_path, new_sig_path)
