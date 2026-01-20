import subprocess

class FirewallEnforcer:
    def __init__(self, dry_run=True):
        """
        dry_run=True  → tidak benar-benar block (AMAN untuk riset)
        dry_run=False → aktifkan iptables (butuh sudo)
        """
        self.dry_run = dry_run

    def block_ip(self, ip):
        if self.dry_run:
            print(f"[ENFORCEMENT] (DRY RUN) Block IP: {ip}")
            return

        cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(cmd, check=False)
        print(f"[ENFORCEMENT] IP {ip} BLOCKED")

    def unblock_ip(self, ip):
        if self.dry_run:
            print(f"[ENFORCEMENT] (DRY RUN) Unblock IP: {ip}")
            return

        cmd = ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(cmd, check=False)
        print(f"[ENFORCEMENT] IP {ip} UNBLOCKED")
