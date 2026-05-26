"""Test inventory endpoint with proper auth session"""
import sys, os, subprocess, time, urllib.request, json, http.cookiejar

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

proc = subprocess.Popen(
    [sys.executable, 'run.py'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=os.getcwd()
)

time.sleep(8)

if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print(f"Server exited with code {proc.returncode}")
    print(f"STDERR: {stderr.decode()[:1000]}")
    exit(1)

try:
    # Create cookie jar for session
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # First, do login
    login_data = json.dumps({"email": "admin@biblioteca.local", "password": "admin123"}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:5477/api/login',
        data=login_data,
        headers={'Content-Type': 'application/json'}
    )
    resp = opener.open(req)
    print(f'Login: {resp.status}')
    if resp.status != 200:
        print(f'Login failed')
        
        # Try getting login page
        req2 = urllib.request.Request('http://127.0.0.1:5477/login')
        resp2 = opener.open(req2)
        html = resp2.read().decode()
        # Extract any csrf token or form info
        print(f'Login page: {html[:500]}')
        exit(1)

    # Try inventory
    req3 = urllib.request.Request(
        'http://127.0.0.1:5477/api/reports/inventory?status=available',
        headers={'Accept': 'application/json'}
    )
    resp3 = opener.open(req3)
    print(f'Inventory (available): {resp3.status}')
    data = json.loads(resp3.read())
    print(f'  Items: {len(data)}')
    if data:
        print(f'  First: {data[0]}')

    req4 = urllib.request.Request(
        'http://127.0.0.1:5477/api/reports/inventory?status=borrowed',
        headers={'Accept': 'application/json'}
    )
    resp4 = opener.open(req4)
    print(f'Inventory (borrowed): {resp4.status}')
    data4 = json.loads(resp4.read())
    print(f'  Items: {len(data4)}')

    req5 = urllib.request.Request(
        'http://127.0.0.1:5477/api/reports/inventory',
        headers={'Accept': 'application/json'}
    )
    resp5 = opener.open(req5)
    print(f'Inventory (all): {resp5.status}')
    data5 = json.loads(resp5.read())
    print(f'  Items: {len(data5)}')

    print('ALL TESTS PASSED!')

except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    body = e.read().decode()
    print(f'Response body: {body[:500]}')
except Exception as e:
    print(f'Error: {e}')
    stdout, stderr = proc.communicate(timeout=3)
    print(f'Server stderr: {stderr.decode()[-1000:]}')
finally:
    proc.terminate()
    proc.wait()
