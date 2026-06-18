# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import urllib.request, json

def api_call(method, path, token=None, data=None):
    url = f"http://127.0.0.1:8000{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "msg": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}

# Login
login = api_call("POST", "/auth/login", data={"email": "staff1@smarttutor.local", "password": "staff123"})
token = login.get("access_token")
print(f"Login: {'OK' if token else 'FAIL'}")

if token:
    for req_id in [122, 124]:
        print(f"\n=== GET /learning-requests/{req_id}/suggested-tutors ===")
        res = api_call("GET", f"/learning-requests/{req_id}/suggested-tutors", token=token)
        if "error" in res:
            print(f"  ERROR {res.get('error')}: {res.get('msg','')[:200]}")
        else:
            sugs = res.get('suggestions', []) if isinstance(res, dict) else res
            print(f"  → {len(sugs)} suggestions")
            for s in (sugs or [])[:5]:
                print(f"    Tutor #{s.get('tutor_id')} {s.get('full_name')} | score={s.get('score')} | area={s.get('area')} | {s.get('experience_years')}y")
