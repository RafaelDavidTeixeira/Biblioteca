"""Unit tests for the license system."""
import sys
import os
import pytest
from datetime import date, timedelta


@pytest.fixture(autouse=True)
def setup_config(monkeypatch, tmp_path):
    """Ensure config_manager returns deterministic values for tests."""
    from app import config_manager
    cfg_path = tmp_path / 'config.json'
    monkeypatch.setattr(config_manager, '_CONFIG_PATH', str(cfg_path))
    monkeypatch.setattr(config_manager, '_CONFIG', None)
    import app.license as lic
    # Reload license module to pick up new config
    monkeypatch.setattr(lic, 'LICENSE_SECRET', b'test-secret-key-1234567890')
    yield


class TestMachineID:
    def test_get_machine_id_returns_string(self):
        from app.license import get_machine_id
        mid = get_machine_id()
        assert isinstance(mid, str)
        assert len(mid) > 0
        assert '-' in mid

    def test_get_machine_id_is_consistent(self):
        from app.license import get_machine_id
        assert get_machine_id() == get_machine_id()

    def test_get_machine_id_format(self):
        from app.license import get_machine_id
        mid = get_machine_id()
        groups = mid.split('-')
        assert len(groups) == 4
        assert all(len(g) == 4 for g in groups)
        assert all(all(c in '0123456789ABCDEF' for c in g) for g in groups)


class TestLicenseKeyGeneration:
    def test_generates_valid_key_format(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test School', valid_days=365)
        assert isinstance(key, str)
        assert len(key) > 20
        assert '-' in key

    def test_generated_key_validates_against_same_machine(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test School', valid_days=365)
        result = validate_license_key(key, mid)
        assert result['valid'] is True
        assert result['error'] is None

    def test_generated_key_rejected_for_different_machine(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        other_mid = 'ABCD-1234-EFGH-5678'
        key = generate_license_key(mid, 'Test School', valid_days=365)
        result = validate_license_key(key, other_mid)
        assert result['valid'] is False
        assert 'máquina' in result['error'].lower()


class TestLicenseValidation:
    def test_empty_key_is_invalid(self):
        from app.license import validate_license_key
        result = validate_license_key('', 'some-machine-id')
        assert result['valid'] is False

    def test_garbage_key_is_invalid(self):
        from app.license import validate_license_key
        result = validate_license_key('ZZZZZZZZZZZZZZZZZZZZZZZZ', 'some-machine-id')
        assert result['valid'] is False

    def test_key_with_wrong_format_is_invalid(self):
        from app.license import validate_license_key
        result = validate_license_key('abc', 'some-machine-id')
        assert result['valid'] is False

    def test_expired_key_is_invalid(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        # Generate a key valid for -1 days (already expired)
        key = generate_license_key(mid, 'Test', valid_days=-1)
        result = validate_license_key(key, mid)
        assert result['valid'] is False
        assert 'expirada' in result['error'].lower()


class TestLicenseKeyCleanup:
    def test_key_with_spaces_is_accepted(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test', valid_days=30)
        key_with_spaces = '  ' + key.replace('-', ' - ') + '  '
        result = validate_license_key(key_with_spaces, mid)
        assert result['valid'] is True

    def test_key_with_lowercase_is_accepted(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test', valid_days=30)
        result = validate_license_key(key.lower(), mid)
        assert result['valid'] is True


class TestLicenseDateValidation:
    def test_valid_until_date_correct(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test', valid_days=30)
        result = validate_license_key(key, mid)
        assert result['valid'] is True
        exp = date.fromisoformat(result['valid_until'].split('/')[2] + '-' +
                                  result['valid_until'].split('/')[1] + '-' +
                                  result['valid_until'].split('/')[0])
        # Should be approximately 30 days from now
        diff = (exp - date.today()).days
        assert 28 <= diff <= 32

    def test_365_day_key(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test', valid_days=365)
        result = validate_license_key(key, mid)
        assert result['valid'] is True

    def test_7_day_key(self):
        from app.license import generate_license_key, validate_license_key, get_machine_id
        mid = get_machine_id()
        key = generate_license_key(mid, 'Test', valid_days=7)
        result = validate_license_key(key, mid)
        assert result['valid'] is True
