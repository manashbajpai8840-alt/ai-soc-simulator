"""
Generates realistic-looking, entirely synthetic security log lines:
  - brute_force     : repeated failed SSH/web logins from one IP
  - sql_injection   : malicious query strings in HTTP access logs
  - malware_c2      : periodic "beacon" callbacks to a suspicious host
  - benign          : normal traffic mixed in, so the pipeline has to
                       actually distinguish signal from noise (this is
                       what makes the false-positive-vs-real-threat
                       problem meaningful; without benign noise the
                       "AI analysis" step would be trivial).

No real network traffic is sent anywhere by this module — it only
emits strings shaped like log lines.
"""
import random
import time

FAKE_USERS = ["admin", "root", "administrator", "test", "backup", "deploy", "oracle"]
FAKE_PATHS = ["/login", "/wp-admin", "/api/v1/users", "/checkout", "/search", "/account"]
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' UNION SELECT username,password FROM users--",
    "1; DROP TABLE users--",
    "admin'--",
    "' OR 1=1#",
    "\" OR \"\"=\"",
]
C2_DOMAINS = ["185.220.101.7", "update-check-cdn.net", "telemetry-sync.biz", "45.148.10.22"]
BENIGN_PATHS = ["/", "/about", "/products", "/images/logo.png", "/api/v1/health", "/blog"]
BENIGN_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) Safari/605.1",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0",
]


def _rand_ip(private=False):
    if private:
        return f"192.168.1.{random.randint(2, 254)}"
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def gen_benign():
    ip = _rand_ip(private=random.random() < 0.5)
    path = random.choice(BENIGN_PATHS)
    ua = random.choice(BENIGN_UAS)
    ts = time.strftime("%d/%b/%Y:%H:%M:%S +0000")
    line = f'{ip} - - [{ts}] "GET {path} HTTP/1.1" 200 {random.randint(200,5000)} "-" "{ua}"'
    return {"category": "benign", "source_ip": ip, "raw_log": line}


def gen_brute_force(ip=None):
    ip = ip or _rand_ip()
    user = random.choice(FAKE_USERS)
    ts = time.strftime("%d/%b/%Y:%H:%M:%S +0000")
    line = (
        f'sshd[{random.randint(1000,9999)}]: Failed password for {user} '
        f'from {ip} port {random.randint(1024,65000)} ssh2 [{ts}]'
    )
    return {"category": "brute_force", "source_ip": ip, "raw_log": line}


def gen_sql_injection(ip=None):
    ip = ip or _rand_ip()
    path = random.choice(FAKE_PATHS)
    payload = random.choice(SQLI_PAYLOADS)
    ts = time.strftime("%d/%b/%Y:%H:%M:%S +0000")
    line = (
        f'{ip} - - [{ts}] "GET {path}?id={payload} HTTP/1.1" 500 1123 '
        f'"-" "sqlmap/1.7.11#stable"'
    )
    return {"category": "sql_injection", "source_ip": ip, "raw_log": line}


def gen_malware_c2(ip=None):
    ip = ip or _rand_ip()
    dest = random.choice(C2_DOMAINS)
    proc = random.choice(["svchost.exe", "explorer.exe", "python3", "updated_.tmp"])
    ts = time.strftime("%d/%b/%Y:%H:%M:%S +0000")
    line = (
        f'[{ts}] conn: local_process={proc} pid={random.randint(1000,60000)} '
        f'src={ip} dst={dest} dst_port=443 bytes_out={random.randint(40,400)} '
        f'interval_s={random.choice([30,60,120])} note="periodic beacon pattern"'
    )
    return {"category": "malware_c2", "source_ip": ip, "raw_log": line}


GENERATORS_WEIGHTED = [
    (gen_benign, 0.70),
    (gen_brute_force, 0.12),
    (gen_sql_injection, 0.10),
    (gen_malware_c2, 0.08),
]


def next_event(sticky_ips=None):
    """
    Produce one synthetic event. `sticky_ips` (dict category->ip) lets the
    caller keep reusing the same attacker IP across several calls, which is
    what makes brute-force *bursts* (many failures from one IP) realistic
    instead of one-off noise.
    """
    r = random.random()
    cum = 0.0
    for fn, weight in GENERATORS_WEIGHTED:
        cum += weight
        if r <= cum:
            if sticky_ips is not None and fn.__name__ != "gen_benign":
                cat_key = fn.__name__
                ip = sticky_ips.get(cat_key)
                if ip is None or random.random() < 0.15:  # occasionally rotate attacker IP
                    ip = _rand_ip()
                    sticky_ips[cat_key] = ip
                return fn(ip=ip)
            return fn()
    return gen_benign()
