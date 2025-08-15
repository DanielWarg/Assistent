#!/usr/bin/env python3
import os, sys, time, json, uuid, statistics, threading
from datetime import datetime
import requests

# ---------- Konfig ----------
BASE_URL      = os.getenv("CORE_BASE_URL", "http://127.0.0.1:8000")
API_KEY       = os.getenv("API_KEY", "")
SLA_P95_MS    = int(os.getenv("SLA_P95_MS", "500"))     # e2e p95 budget i ms
SSE_MIN_EVENTS= int(os.getenv("SSE_MIN_EVENTS", "5"))   # min event som måste ses
SSE_WINDOW_S  = int(os.getenv("SSE_WINDOW_S", "5"))     # hur länge vi lyssnar på SSE
LOAD_REQUESTS = int(os.getenv("LOAD_REQUESTS", "200"))  # last för p95-test
HEADERS_JSON  = {"Accept": "application/json"}
RID           = f"go-no-go-{uuid.uuid4()}"

out_dir = os.getenv("GO_NO_GO_OUT", "./logs")
os.makedirs(out_dir, exist_ok=True)

# ---------- Hjälpfunktioner ----------
def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

def check(status, msg, details=None):
    return {"ok": bool(status), "msg": msg, "details": details or {}}

def sse_count_events(stop_after_s=SSE_WINDOW_S):
    """
    Lyssnar på /logs/stream och räknar SSE 'data:'-rader under en tid.
    Verifierar att anslutningen inte hänger.
    """
    url = f"{BASE_URL}/logs/stream"
    headers = {"Accept": "text/event-stream", "Cache-Control": "no-cache"}
    seen = {"count": 0, "lines": 0, "errors": 0}
    start = time.time()
    try:
        with requests.get(url, headers=headers, stream=True, timeout=10) as r:
            r.raise_for_status()
            for raw in r.iter_lines(chunk_size=1024, decode_unicode=True):
                if raw is None: 
                    continue
                seen["lines"] += 1
                if raw.startswith("data:"):
                    seen["count"] += 1
                if time.time() - start >= stop_after_s:
                    break
    except Exception as e:
        seen["errors"] += 1
        seen["error"] = str(e)
    return seen

def measure_latency(n=LOAD_REQUESTS, path="/health/live"):
    lat = []
    url = f"{BASE_URL}{path}"
    for _ in range(n):
        t0 = time.perf_counter()
        r = requests.get(url, headers=HEADERS_JSON, timeout=5)
        r.raise_for_status()
        lat.append((time.perf_counter() - t0) * 1000.0)  # ms
    return {
        "count": len(lat),
        "p50_ms": statistics.median(lat) if lat else None,
        "p95_ms": (sorted(lat)[int(0.95*len(lat))-1] if lat else None),
        "samples": min(len(lat), 5)
    }

def write_reports(results):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(out_dir, f"go_no_go_{ts}.json")
    md_path   = os.path.join(out_dir, f"go_no_go_{ts}.md")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    # Markdown
    ok = "✅" if results["overall_ok"] else "❌"
    md = [
        f"# Go/No-Go Rapport ({ok})",
        f"- Timestamp: {results['ts']}",
        f"- Base URL: {results['base_url']}",
        f"- SLA p95 budget: {SLA_P95_MS} ms",
        "",
        "## Sammanfattning",
        f"- OpenAPI: {'OK' if results['openapi']['ok'] else 'FAIL'}",
        f"- API-nyckel (muterande endpoint): {'OK' if results['auth']['ok'] else 'FAIL'}",
        f"- SSE events: {results['sse']['details'].get('count',0)} (min {SSE_MIN_EVENTS}) → {'OK' if results['sse']['ok'] else 'FAIL'}",
        f"- E2E p95: {results['latency']['details'].get('p95_ms')} ms (budget {SLA_P95_MS}) → {'OK' if results['latency']['ok'] else 'FAIL'}",
        "",
        "## Detaljer",
        "### OpenAPI",
        f"```json\n{json.dumps(results['openapi'], indent=2)}\n```",
        "### Auth",
        f"```json\n{json.dumps(results['auth'], indent=2)}\n```",
        "### SSE",
        f"```json\n{json.dumps(results['sse'], indent=2)}\n```",
        "### Latens",
        f"```json\n{json.dumps(results['latency'], indent=2)}\n```",
    ]
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    return json_path, md_path

# ---------- Tester ----------
def test_openapi():
    try:
        r = requests.get(f"{BASE_URL}/openapi.json", headers=HEADERS_JSON, timeout=5)
        ok = r.status_code == 200 and "info" in r.json()
        return check(ok, "OpenAPI svarar 200 och innehåller .info",
                     {"status": r.status_code})
    except Exception as e:
        return check(False, "OpenAPI fel", {"error": str(e)})

def test_auth_mutating():
    # Utan key -> 401
    try:
        r1 = requests.post(f"{BASE_URL}/selftest/run", timeout=5)
        no_key_ok = r1.status_code in (401, 403)
    except Exception as e:
        return check(False, "Auth test misslyckades (utan key)", {"error": str(e)})

    # Med key -> 200
    try:
        hdr = {"X-API-Key": API_KEY} if API_KEY else {}
        r2 = requests.post(f"{BASE_URL}/selftest/run", headers=hdr, timeout=5)
        with_key_ok = (API_KEY != "") and (r2.status_code == 200)
        return check(no_key_ok and with_key_ok,
                     "Muterande endpoint kräver API-nyckel",
                     {"no_key_status": r1.status_code, "with_key_status": r2.status_code, "api_key_present": API_KEY != ""})
    except Exception as e:
        return check(False, "Auth test misslyckades (med key)", {"error": str(e)})

def test_sse():
    # Kör två parallella lyssnare för att detektera häng
    results = {}
    def worker(name):
        results[name] = sse_count_events(SSE_WINDOW_S)

    t1 = threading.Thread(target=worker, args=("a",))
    t2 = threading.Thread(target=worker, args=("b",))
    t1.start(); t2.start(); t1.join(); t2.join()

    total = results["a"]["count"] + results["b"]["count"]
    ok = (results["a"]["errors"] == 0 and results["b"]["errors"] == 0 and total >= SSE_MIN_EVENTS)
    return check(ok, "SSE stabilitet & backpressure",
                 {"a": results["a"], "b": results["b"], "count": total, "min_required": SSE_MIN_EVENTS})

def test_latency():
    # mät e2e på GET /health/live
    m = measure_latency(LOAD_REQUESTS, "/health/live")
    p95 = m["p95_ms"] if m["p95_ms"] is not None else float("inf")
    ok = p95 <= SLA_P95_MS
    return check(ok, f"E2E p95 <= {SLA_P95_MS} ms", m)

def main():
    ts = now_iso()
    summary = {
        "ts": ts,
        "base_url": BASE_URL,
        "rid": RID,
        "sla": {"p95_ms": SLA_P95_MS, "sse_min_events": SSE_MIN_EVENTS, "sse_window_s": SSE_WINDOW_S},
    }

    results = {
        "openapi": test_openapi(),
        "auth":    test_auth_mutating(),
        "sse":     test_sse(),
        "latency": test_latency(),
    }
    overall_ok = all(v["ok"] for v in results.values())
    results["overall_ok"] = overall_ok
    results.update(summary)

    json_path, md_path = write_reports(results)
    print(json.dumps({
        "overall_ok": overall_ok,
        "json_report": json_path,
        "md_report": md_path,
        "base_url": BASE_URL,
        "sla_p95_ms": SLA_P95_MS
    }, indent=2))
    sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()
