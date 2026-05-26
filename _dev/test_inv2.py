import sys, os, subprocess, time, urllib.request, json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

proc = subprocess.Popen(
    [sys.executable, 'run.py'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=os.getcwd()
)

time.sleep(8)

# Check if process is still running
if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print(f"Server exited with code {proc.returncode}")
    print(f"STDOUT: {stdout.decode()[:500]}")
    print(f"STDERR: {stderr.decode()[:500]}")
else:
    try:
        # Test inventory without filters
        req = urllib.request.Request(
            'http://127.0.0.1:5477/api/reports/inventory',
            headers={'Accept': 'application/json'}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        print(f'Status: {resp.status}')
        print(f'Items: {len(data) if isinstance(data, list) else "N/A"}')
        
        # Test with status=available 
        req2 = urllib.request.Request(
            'http://127.0.0.1:5477/api/reports/inventory?status=available',
            headers={'Accept': 'application/json'}
        )
        resp2 = urllib.request.urlopen(req2, timeout=5)
        data2 = json.loads(resp2.read())
        print(f'With status=available: {len(data2) if isinstance(data2, list) else str(data2)[:200]}')
        
        # Test with status=borrowed
        req3 = urllib.request.Request(
            'http://127.0.0.1:5477/api/reports/inventory?status=borrowed',
            headers={'Accept': 'application/json'}
        )
        resp3 = urllib.request.urlopen(req3, timeout=5)
        data3 = json.loads(resp3.read())
        print(f'With status=borrowed: {len(data3) if isinstance(data3, list) else str(data3)[:200]}')
        
    except urllib.error.HTTPError as e:
        print(f'HTTP Error: {e.code}')
        print(f'Response: {e.read().decode()[:500]}')
    except Exception as e:
        print(f'Error: {e}')
        stdout, stderr = proc.communicate(timeout=3)
        print(f'Server stdout: {stdout.decode()[-500:]}')
        print(f'Server stderr: {stderr.decode()[-500:]}')
    finally:
        proc.terminate()
        proc.wait()

# Clean up
import atexit
try: proc.terminate()
except: pass
