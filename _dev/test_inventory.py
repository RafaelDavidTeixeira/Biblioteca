import subprocess
import time
import urllib.request
import json
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

proc = subprocess.Popen(
    [sys.executable, 'run.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(6)

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/reports/inventory',
        headers={'Accept': 'application/json'}
    )
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read())
    print(f'Status: {resp.status}')
    print(f'Response type: {type(data).__name__}')
    if isinstance(data, list):
        print(f'Items: {len(data)}')
        if data:
            print(f'First: patrimony={data[0].get("patrimony")}, title={data[0].get("title")}')
            print(f'Keys: {list(data[0].keys())}')
    else:
        print(f'Response: {str(data)[:300]}')
except Exception as e:
    print(f'Error: {e}')
    stdout, stderr = proc.communicate(timeout=3)
    print(f'Server stdout: {stdout.decode()[-500:]}')
    print(f'Server stderr: {stderr.decode()[-500:]}')
finally:
    proc.terminate()
    proc.wait()
