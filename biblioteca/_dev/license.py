"""
License system - hardware fingerprint + HMAC-SHA256 + base32 encoding.
Keys are short, readable, typeable, and machine-locked.
"""
import hashlib, hmac, base64, uuid, platform, json
from datetime import date

LICENSE_SECRET = b'biblio-lic-secret-2026-!@#XkP9m'


def get_machine_id() -> str:
    """Generate unique machine fingerprint."""
    raw = '|'.join([hex(uuid.getnode()), platform.node(), platform.system(), platform.machine()])
    h = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    return '-'.join([h[i:i+4] for i in range(0, 16, 4)])


def generate_license_key(machine_id: str, institution: str, valid_days: int = 365) -> str:
    """Generate a machine-locked license key with random nonce to prevent reuse."""
    exp = date.today().toordinal() + valid_days

    # Nonce aleatório de 3 bytes — garante que cada geração produz chave única
    nonce = uuid.uuid4().bytes[:3]

    # Payload: machine hash(4) + exp(4) + nonce(3) = 11 bytes
    mid_hash = hashlib.sha256(machine_id.encode()).digest()[:4]
    exp_bytes = exp.to_bytes(4, 'big')

    payload = mid_hash + exp_bytes + nonce
    sig = hmac.new(LICENSE_SECRET, payload, hashlib.sha256).digest()[:4]

    combined = payload + sig  # 15 bytes → base32 = 24 chars → 4 grupos de 6
    encoded = base64.b32encode(combined).decode().rstrip('=')
    groups = [encoded[i:i+6] for i in range(0, len(encoded), 6)]
    return '-'.join(groups)


def validate_license_key(license_key: str, machine_id: str) -> dict:
    """Validate a license key against the current machine."""
    try:
        clean = license_key.replace('-', '').replace(' ', '').upper()
        if not clean:
            return {'valid': False, 'error': 'Chave vazia'}

        pad = (8 - len(clean) % 8) % 8
        try:
            decoded = base64.b32decode(clean + '=' * pad)
        except Exception:
            return {'valid': False, 'error': 'Formato de chave inválido. Verifique se copiou a chave completa.'}

        if len(decoded) < 12:
            return {'valid': False, 'error': 'Chave muito curta ou incompleta'}

        # Suporte a dois formatos:
        # Novo (com nonce): payload=11 bytes (mid4+exp4+nonce3) + sig=4 bytes = 15 bytes
        # Antigo (sem nonce): payload=8 bytes (mid4+exp4) + sig=4 bytes = 12 bytes
        if len(decoded) >= 15:
            payload = decoded[:11]
            sig_stored = decoded[11:15]
        else:
            payload = decoded[:8]
            sig_stored = decoded[8:12]

        # Verify HMAC
        sig_expected = hmac.new(LICENSE_SECRET, payload, hashlib.sha256).digest()[:4]
        if not hmac.compare_digest(sig_stored, sig_expected):
            return {'valid': False, 'error': 'Assinatura inválida — chave adulterada ou incorreta'}

        # Verify machine ID (always first 4 bytes)
        mid_hash = hashlib.sha256(machine_id.encode()).digest()[:4]
        if payload[:4] != mid_hash:
            return {'valid': False, 'error': 'Licença não é válida para esta máquina'}

        # Extract expiration (bytes 4-8)
        exp_ordinal = int.from_bytes(payload[4:8], 'big')
        exp = date.fromordinal(exp_ordinal)
        if date.today() > exp:
            return {'valid': False, 'error': f'Licença expirada em {exp.strftime("%d/%m/%Y")}'}
        
        return {
            'valid': True,
            'institution': 'Ativada',
            'valid_until': exp.strftime('%d/%m/%Y'),
            'valid_until_date': exp,
            'error': None
        }
    except Exception as ex:
        return {'valid': False, 'error': f'Chave inválida: {ex}'}
