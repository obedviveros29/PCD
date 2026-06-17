import re
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict


PATRON_HTTP = re.compile(r'''
    ^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})
    \s+\S+\s+\S+\s+
    \[(?P<timestamp>[^\]]+)\]
    \s+
    "(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/\d\.\d"
    \s+
    (?P<status>\d{3})
    \s+
    (?P<bytes>\d+)
    \s+
    "(?P<referer>[^"]*)"
    \s+
    "(?P<user_agent>[^"]*)"
''', re.VERBOSE)


def parse_http_log(linea: str) -> Optional[Dict]:
    m = PATRON_HTTP.match(linea.strip())
    if not m:
        return None
    d = m.groupdict()
    return {
        "ip": d["ip"],
        "timestamp": d["timestamp"],
        "method": d["method"],
        "path": d["path"],
        "status": int(d["status"]),
        "bytes": int(d["bytes"]),
        "referer": d["referer"],
        "user_agent": d["user_agent"],
    }


PATRON_ERROR = re.compile(r'''
    ^\[(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]
    \s+
    (?P<level>ERROR|WARNING|INFO|DEBUG|CRITICAL)
    \s+
    (?P<module>[\w.]+)
    \s+-\s+
    (?:(?P<error_type>\w+):\s+)?
    (?P<message>.+)$
''', re.VERBOSE)


def parse_error_log(linea: str) -> Optional[Dict]:
    m = PATRON_ERROR.match(linea.strip())
    if not m:
        return None
    d = m.groupdict()
    return {
        "timestamp": d["timestamp"],
        "level": d["level"],
        "module": d["module"],
        "error_type": d["error_type"] if d["error_type"] else "",
        "message": d["message"],
    }


PATRON_AUTH = re.compile(r'''
    ^\[AUTH\]\s+
    (?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})
    \s+\|\s+
    (?P<resto>.+)$
''', re.VERBOSE)

PATRON_USER = re.compile(r'(?<=user=)[^\s|]+')
PATRON_ACTION = re.compile(r'(?<=action=)[^\s|]+')
PATRON_STATUS = re.compile(r'(?<=status=)[^\s|]+')
PATRON_IP = re.compile(r'(?<=ip=)[^\s|]+')
PATRON_SESSION = re.compile(r'(?<=session=)[^\s|]+')
PATRON_ATTEMPTS = re.compile(r'(?<=attempts=)\d+')


def parse_auth_log(linea: str) -> Optional[Dict]:
    m = PATRON_AUTH.match(linea.strip())
    if not m:
        return None
    timestamp = m.group("timestamp")
    resto = m.group("resto")

    user = PATRON_USER.search(resto)
    action = PATRON_ACTION.search(resto)
    status = PATRON_STATUS.search(resto)
    ip = PATRON_IP.search(resto)
    session = PATRON_SESSION.search(resto)
    attempts = PATRON_ATTEMPTS.search(resto)

    extra = {}
    if session:
        extra["session"] = session.group(0)
    if attempts:
        extra["attempts"] = int(attempts.group(0))

    return {
        "timestamp": timestamp,
        "user": user.group(0) if user else "",
        "action": action.group(0) if action else "",
        "status": status.group(0) if status else "",
        "ip": ip.group(0) if ip else "",
        "extra": extra,
    }


PATRON_DB = re.compile(r'''
    ^\[DB-(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]
    \s+
    (?:
        (?P<tipo_query>QUERY)\s+executed\s+in\s+(?P<tiempo1>[\d.]+)s
        |
        (?P<tipo_slow>SLOW_QUERY)\s+\((?P<tiempo2>[\d.]+)s\)
    )
    :\s+
    (?P<query>.+)$
''', re.VERBOSE)


def parse_db_log(linea: str) -> Optional[Dict]:
    m = PATRON_DB.match(linea.strip())
    if not m:
        return None
    d = m.groupdict()
    if d["tipo_query"]:
        query_type = d["tipo_query"]
        execution_time = float(d["tiempo1"])
    else:
        query_type = d["tipo_slow"]
        execution_time = float(d["tiempo2"])
    return {
        "timestamp": d["timestamp"],
        "query_type": query_type,
        "execution_time": execution_time,
        "query": d["query"],
    }


def detectar_ataques_fuerza_bruta(logs_auth: List[Dict]) -> List[Dict]:
    fallidos = defaultdict(int)
    for log in logs_auth:
        if log["action"] == "LOGIN" and log["status"] == "FAILED":
            fallidos[log["ip"]] += 1
    resultado = []
    for ip, intentos in fallidos.items():
        if intentos > 3:
            resultado.append({"ip": ip, "intentos": intentos})
    resultado.sort(key=lambda x: x["intentos"], reverse=True)
    return resultado


PATRONES_SQL_INJECTION = [
    r"(?i)\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+",
    r"(?i)\bUNION\b.*\bSELECT\b",
    r"--",
    r"(?i)\bDROP\b\s+\bTABLE\b",
    r"(?i)\bDELETE\b\s+\bFROM\b.*\bWHERE\b\s+1\s*=\s*1",
]

_SQL_COMPILADOS = [re.compile(p) for p in PATRONES_SQL_INJECTION]


def detectar_sql_injection(logs_db: List[Dict]) -> List[Dict]:
    resultado = []
    for log in logs_db:
        query = log["query"]
        for patron in _SQL_COMPILADOS:
            if patron.search(query):
                resultado.append({
                    "timestamp": log["timestamp"],
                    "query": query,
                })
                break
    return resultado


PATRON_PATH_TRAVERSAL = re.compile(
    r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/)"
)


def detectar_path_traversal(logs_http: List[Dict]) -> List[Dict]:
    resultado = []
    for log in logs_http:
        if PATRON_PATH_TRAVERSAL.search(log["path"]):
            resultado.append({
                "ip": log["ip"],
                "path": log["path"],
                "user_agent": log["user_agent"],
            })
    return resultado


def detectar_errores_criticos(logs_error: List[Dict]) -> List[Dict]:
    criticos = [e for e in logs_error if e["level"] in ("ERROR", "CRITICAL")]
    criticos.sort(key=lambda x: x["timestamp"])
    return criticos


def clasificar_linea(linea: str) -> str:
    linea = linea.strip()
    if linea.startswith("[AUTH]"):
        return "auth"
    if linea.startswith("[DB-"):
        return "db"
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}\s", linea):
        return "http"
    if re.match(r"^\[\d{4}-\d{2}-\d{2}\s", linea):
        return "error"
    return "desconocido"


def generar_reporte(logs: str) -> Dict:
    lineas = [l for l in logs.strip().split("\n") if l.strip()]

    logs_http = []
    logs_error = []
    logs_auth = []
    logs_db = []
    por_tipo = {"http": 0, "error": 0, "auth": 0, "db": 0}

    for linea in lineas:
        tipo = clasificar_linea(linea)
        if tipo == "http":
            r = parse_http_log(linea)
            if r:
                logs_http.append(r)
                por_tipo["http"] += 1
        elif tipo == "error":
            r = parse_error_log(linea)
            if r:
                logs_error.append(r)
                por_tipo["error"] += 1
        elif tipo == "auth":
            r = parse_auth_log(linea)
            if r:
                logs_auth.append(r)
                por_tipo["auth"] += 1
        elif tipo == "db":
            r = parse_db_log(linea)
            if r:
                logs_db.append(r)
                por_tipo["db"] += 1

    por_status = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
    contador_rutas = Counter()
    contador_ips = Counter()
    for h in logs_http:
        clave = f"{h['status'] // 100}xx"
        if clave in por_status:
            por_status[clave] += 1
        ruta = h["path"].split("?")[0]
        contador_rutas[ruta] += 1
        contador_ips[h["ip"]] += 1

    por_nivel = Counter()
    por_modulo = Counter()
    for e in logs_error:
        por_nivel[e["level"]] += 1
        por_modulo[e["module"]] += 1

    queries_lentos = [d for d in logs_db if d["query_type"] == "SLOW_QUERY"]
    tiempos = [d["execution_time"] for d in logs_db]
    tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0.0

    return {
        "resumen": {
            "total_lineas": len(lineas),
            "por_tipo": por_tipo,
        },
        "http": {
            "total_requests": len(logs_http),
            "por_status": por_status,
            "top_rutas": contador_rutas.most_common(5),
            "top_ips": contador_ips.most_common(5),
        },
        "errores": {
            "total": len(logs_error),
            "por_nivel": dict(por_nivel),
            "por_modulo": dict(por_modulo),
        },
        "seguridad": {
            "alertas_fuerza_bruta": detectar_ataques_fuerza_bruta(logs_auth),
            "alertas_sql_injection": detectar_sql_injection(logs_db),
            "alertas_path_traversal": detectar_path_traversal(logs_http),
        },
        "rendimiento": {
            "queries_lentos": queries_lentos,
            "tiempo_promedio_queries": tiempo_promedio,
        },
    }


def mostrar_reporte(reporte: Dict) -> None:
    print("=" * 70)
    print("                    REPORTE DE ANÁLISIS DE LOGS")
    print("=" * 70)

    print("\n RESUMEN GENERAL")
    print("-" * 40)
    print(f"Total de líneas procesadas: {reporte['resumen']['total_lineas']}")
    print("Por tipo:")
    for tipo, count in reporte['resumen']['por_tipo'].items():
        print(f"  • {tipo.upper()}: {count}")

    if 'http' in reporte:
        print("\n LOGS HTTP")
        print("-" * 40)
        print(f"Total requests: {reporte['http']['total_requests']}")
        print("Por código de estado:")
        for status, count in reporte['http']['por_status'].items():
            print(f"  • {status}: {count}")
        print("Top 5 rutas más solicitadas:")
        for ruta, count in reporte['http'].get('top_rutas', [])[:5]:
            print(f"  • {ruta}: {count} requests")

    if 'errores' in reporte:
        print("\n ERRORES")
        print("-" * 40)
        print(f"Total errores: {reporte['errores']['total']}")
        print("Por nivel:")
        for nivel, count in reporte['errores']['por_nivel'].items():
            print(f"  • {nivel}: {count}")

    if 'seguridad' in reporte:
        print("\n ALERTAS DE SEGURIDAD")
        print("-" * 40)

        fb = reporte['seguridad'].get('alertas_fuerza_bruta', [])
        if fb:
            print(f"  Posibles ataques de fuerza bruta: {len(fb)}")
            for alerta in fb:
                print(f"     IP: {alerta['ip']} - {alerta['intentos']} intentos fallidos")

        sql = reporte['seguridad'].get('alertas_sql_injection', [])
        if sql:
            print(f"  Posibles SQL Injection: {len(sql)}")
            for alerta in sql[:3]:
                print(f"     Query: {alerta['query'][:60]}...")

        pt = reporte['seguridad'].get('alertas_path_traversal', [])
        if pt:
            print(f"  Posibles Path Traversal: {len(pt)}")
            for alerta in pt[:3]:
                print(f"     Ruta: {alerta['path']}")

    if 'rendimiento' in reporte:
        print("\n  RENDIMIENTO")
        print("-" * 40)
        print(f"Queries lentos detectados: {len(reporte['rendimiento'].get('queries_lentos', []))}")
        if 'tiempo_promedio_queries' in reporte['rendimiento']:
            print(f"Tiempo promedio de queries: {reporte['rendimiento']['tiempo_promedio_queries']:.3f}s")

    print("\n" + "=" * 70)


LOGS_PRUEBA = """
192.168.1.100 - - [15/Mar/2024:10:23:45 -0600] "GET /api/users HTTP/1.1" 200 1234 "https://ejemplo.com" "Mozilla/5.0 (Windows NT 10.0)"
192.168.1.101 - - [15/Mar/2024:10:23:46 -0600] "POST /api/login HTTP/1.1" 200 89 "-" "curl/7.68.0"
192.168.1.102 - - [15/Mar/2024:10:23:47 -0600] "GET /admin/../../../etc/passwd HTTP/1.1" 403 0 "-" "sqlmap/1.0"
[2024-03-15 10:24:00] INFO app.startup - Application started successfully on port 8080
[2024-03-15 10:25:12] ERROR app.database - DatabaseConnectionError: Connection refused to host db.server.com:5432
[2024-03-15 10:25:15] WARNING app.cache - CacheWarning: Redis connection timeout, using fallback
[2024-03-15 10:26:00] ERROR app.auth - AuthenticationError: Invalid token for user admin@empresa.com
[AUTH] 2024-03-15 10:30:00 | user=admin@empresa.com | action=LOGIN | status=SUCCESS | ip=10.0.0.5 | session=abc123xyz
[AUTH] 2024-03-15 10:31:00 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=1
[AUTH] 2024-03-15 10:31:30 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=2
[AUTH] 2024-03-15 10:32:00 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=3
[AUTH] 2024-03-15 10:32:30 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=4
[AUTH] 2024-03-15 10:33:00 | user=otro@empresa.com | action=LOGOUT | status=SUCCESS | ip=10.0.0.10 | session=def456uvw
[DB-2024-03-15 10:35:22] QUERY executed in 0.045s: SELECT * FROM users WHERE email = 'admin@empresa.com'
[DB-2024-03-15 10:35:25] QUERY executed in 0.012s: SELECT id, name FROM products WHERE active = 1
[DB-2024-03-15 10:36:00] SLOW_QUERY (2.5s): SELECT * FROM orders o JOIN products p ON o.product_id = p.id JOIN users u ON o.user_id = u.id
[DB-2024-03-15 10:37:00] QUERY executed in 0.001s: SELECT * FROM users WHERE username = 'admin' OR 1=1--'
[DB-2024-03-15 10:38:00] QUERY executed in 0.002s: SELECT * FROM users UNION SELECT * FROM passwords
192.168.1.200 - - [15/Mar/2024:10:40:00 -0600] "GET /products?id=1 HTTP/1.1" 200 5678 "https://tienda.com" "Mozilla/5.0"
192.168.1.200 - - [15/Mar/2024:10:40:05 -0600] "GET /products?id=2 HTTP/1.1" 200 4321 "https://tienda.com" "Mozilla/5.0"
192.168.1.201 - - [15/Mar/2024:10:41:00 -0600] "GET /api/users HTTP/1.1" 401 123 "-" "PostmanRuntime/7.26.8"
192.168.1.201 - - [15/Mar/2024:10:41:05 -0600] "GET /api/users HTTP/1.1" 500 0 "-" "PostmanRuntime/7.26.8"
[2024-03-15 10:42:00] ERROR app.api - NullPointerException: Cannot read property 'id' of undefined
[DB-2024-03-15 10:45:00] SLOW_QUERY (5.2s): SELECT COUNT(*) FROM logs WHERE date > '2024-01-01'
""".strip()


if __name__ == "__main__":
    print("PRUEBA DE PARSERS")
    print("=" * 50)

    linea_http = '192.168.1.100 - - [15/Mar/2024:10:23:45 -0600] "GET /api/users HTTP/1.1" 200 1234 "https://ejemplo.com" "Mozilla/5.0"'
    print("\n-- Parser HTTP --")
    print(f"Resultado: {parse_http_log(linea_http)}")

    linea_error = "[2024-03-15 10:25:12] ERROR app.database - DatabaseConnectionError: Connection refused"
    print("\n-- Parser Error --")
    print(f"Resultado: {parse_error_log(linea_error)}")

    linea_auth = "[AUTH] 2024-03-15 10:30:00 | user=admin@empresa.com | action=LOGIN | status=SUCCESS | ip=10.0.0.5 | session=abc123xyz"
    print("\n-- Parser Auth --")
    print(f"Resultado: {parse_auth_log(linea_auth)}")

    linea_db = "[DB-2024-03-15 10:35:22] QUERY executed in 0.045s: SELECT * FROM users"
    print("\n-- Parser DB --")
    print(f"Resultado: {parse_db_log(linea_db)}")

    print("\nGENERANDO REPORTE COMPLETO...\n")
    reporte = generar_reporte(LOGS_PRUEBA)
    mostrar_reporte(reporte)