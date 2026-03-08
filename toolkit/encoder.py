# Advanced Encoder/Decoder
import base64
import urllib.parse
import binascii

class AdvancedEncoder:
    @staticmethod
    def encode(data, e_type):
        if e_type == "base64":
            return base64.b64encode(data.encode()).decode()
        elif e_type == "hex":
            return binascii.hexlify(data.encode()).decode()
        elif e_type == "url":
            return urllib.parse.quote(data)
        elif e_type == "binary":
            return ' '.join(format(ord(c), '08b') for c in data)
        return "ERROR: Unsupported encoding."

    @staticmethod
    def decode(data, e_type):
        try:
            if e_type == "base64":
                return base64.b64decode(data).decode()
            elif e_type == "hex":
                return binascii.unhexlify(data).decode()
            elif e_type == "url":
                return urllib.parse.unquote(data)
        except:
            return "ERROR: Decoding failure."
        return "ERROR: Unsupported decoding."
