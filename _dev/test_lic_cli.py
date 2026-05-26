import sys, os, hashlib, hmac, base64, uuid, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.license import generate_license_key, validate_license_key, get_machine_id

# 1. Verify the secret used by this bundle
import app.license as lic_mod
print('SECRET=' + repr(lic_mod.LICENSE_SECRET))

# 2. Generate key for this machine
mid = get_machine_id()
key = generate_license_key(mid, 'Test', 365)
print('MACHINE_ID=' + mid)
print('KEY=' + key)

# 3. Validate
r = validate_license_key(key, mid)
print('VALID=' + str(r['valid']))
if not r['valid']:
    print('ERROR=' + r.get('error', ''))
