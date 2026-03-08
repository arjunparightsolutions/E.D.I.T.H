# Local CVE Lookup Engine
class CVELookup:
    def __init__(self):
        # Mock CVE database
        self.db = {
            "CVE-2021-44228": "Log4Shell: Remote Code Execution in Apache Log4j",
            "CVE-2017-0144": "EternalBlue: SMBv1 exploit used in WannaCry",
            "CVE-2020-0601": "CurveBall: Windows CryptoAPI spoofing",
            "CVE-2023-32311": "Openfire Remote Code Execution"
        }

    def search(self, query):
        results = {}
        for cve, desc in self.db.items():
            if query.lower() in cve.lower() or query.lower() in desc.lower():
                results[cve] = desc
        return results

    def get_latest(self):
        return list(self.db.keys())[:5]
