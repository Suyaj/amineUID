import hashlib


def get_md5(string: str):
    md5 = hashlib.md5()
    md5.update(string.encode('utf-8'))
    hex_digest = md5.hexdigest()
    while len(hex_digest) <32:
        hex_digest = '0$'+hex_digest
    return hex_digest
