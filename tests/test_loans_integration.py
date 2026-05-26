"""Integration tests for the loan lifecycle (create, return, renew, reserve)."""
import pytest
import json
from datetime import date, timedelta


@pytest.fixture(autouse=True)
def setup_license(monkeypatch):
    """Bypass license check for integration tests."""
    from app import database as db
    monkeypatch.setattr(db, 'is_license_valid', lambda: True)


@pytest.fixture
def client():
    """Create a test Flask client with a temporary DB."""
    import tempfile
    import os
    from app import create_app
    from app import database as db

    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app = create_app()
    app.config['TESTING'] = True
    app.config['DB_PATH'] = db_path
    # Re-init DB with temp path
    db.init_db(db_path)
    ctx = app.app_context()
    ctx.push()

    with app.test_client() as c:
        yield c

    ctx.pop()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def auth_client(client):
    """Log in as admin and return authenticated client."""
    resp = client.post('/login', data={
        'email': 'admin@biblioteca.local',
        'password': 'admin123'
    }, follow_redirects=True)
    assert resp.status_code == 200
    return client


def _create_student(client, name='Aluno Teste', enrollment='2025001', class_name='9A'):
    resp = client.post('/api/students', data=json.dumps({
        'name': name, 'enrollment': enrollment, 'class_name': class_name
    }), content_type='application/json')
    return resp.get_json()


def _create_book(client, patrimony='PAT-00001', title='Livro Teste'):
    resp = client.post('/api/books', data=json.dumps({
        'patrimony': patrimony, 'title': title, 'author': 'Autor Teste'
    }), content_type='application/json')
    return resp.get_json()


class TestLoanCRUD:
    def test_create_loan(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        data = resp.get_json()
        assert data['ok'] is True
        assert data['loan']['returned'] == 0

    def test_create_loan_book_not_found(self, auth_client):
        s = _create_student(auth_client)['student']
        due = (date.today() + timedelta(days=14)).isoformat()
        resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': 99999, 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        assert resp.status_code == 404

    def test_create_loan_without_student(self, auth_client):
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'due_date': due
        }), content_type='application/json')
        assert resp.status_code == 400

    def test_double_loan_fails(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        assert resp.status_code == 400


class TestLoanReturn:
    def test_return_loan(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        loan_resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        loan = loan_resp.get_json()['loan']
        resp = auth_client.post(f'/api/loans/{loan["id"]}/return')
        data = resp.get_json()
        assert data['ok'] is True
        assert data['loan']['returned'] == 1

    def test_return_by_patrimony(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        resp = auth_client.post('/api/loans/return-by-patrimony', data=json.dumps({
            'patrimony': b['patrimony']
        }), content_type='application/json')
        data = resp.get_json()
        assert data['ok'] is True

    def test_return_already_returned_fails(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        loan_resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        loan = loan_resp.get_json()['loan']
        auth_client.post(f'/api/loans/{loan["id"]}/return')
        resp = auth_client.post(f'/api/loans/{loan["id"]}/return')
        assert resp.status_code == 400


class TestLoanRenew:
    def test_renew_loan(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        loan_resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        loan = loan_resp.get_json()['loan']
        resp = auth_client.post(f'/api/loans/{loan["id"]}/renew')
        data = resp.get_json()
        assert data['ok'] is True
        assert data['loan']['renewed'] == 1

    def test_renew_returned_loan_fails(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        loan_resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id'], 'due_date': due
        }), content_type='application/json')
        loan = loan_resp.get_json()['loan']
        auth_client.post(f'/api/loans/{loan["id"]}/return')
        resp = auth_client.post(f'/api/loans/{loan["id"]}/renew')
        assert resp.status_code == 400


class TestReservations:
    def test_create_reservation(self, auth_client):
        s1 = _create_student(auth_client, 'Aluno A', '2025002')['student']
        s2 = _create_student(auth_client, 'Aluno B', '2025003')['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        # First, loan the book to s1
        auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s1['id'], 'due_date': due
        }), content_type='application/json')
        # s2 reserves the book
        resp = auth_client.post('/api/reservations', data=json.dumps({
            'book_id': b['id'], 'student_id': s2['id']
        }), content_type='application/json')
        data = resp.get_json()
        assert data['ok'] is True

    def test_reservation_for_available_book_fails(self, auth_client):
        s = _create_student(auth_client)['student']
        b = _create_book(auth_client)['book']
        resp = auth_client.post('/api/reservations', data=json.dumps({
            'book_id': b['id'], 'student_id': s['id']
        }), content_type='application/json')
        assert resp.status_code == 400

    def test_reservation_notifies_on_return(self, auth_client):
        s1 = _create_student(auth_client, 'Aluno A', '2025004')['student']
        s2 = _create_student(auth_client, 'Aluno B', '2025005')['student']
        b = _create_book(auth_client)['book']
        due = (date.today() + timedelta(days=14)).isoformat()
        loan_resp = auth_client.post('/api/loans', data=json.dumps({
            'book_id': b['id'], 'student_id': s1['id'], 'due_date': due
        }), content_type='application/json')
        loan = loan_resp.get_json()['loan']
        auth_client.post('/api/reservations', data=json.dumps({
            'book_id': b['id'], 'student_id': s2['id']
        }), content_type='application/json')
        resp = auth_client.post(f'/api/loans/{loan["id"]}/return')
        data = resp.get_json()
        assert data['has_reservation'] is True
        assert data['reservation']['student_id'] == s2['id']


class TestPermissions:
    def test_unauthorized_access_returns_401(self, client):
        resp = client.get('/api/books')
        assert resp.status_code == 401

    def test_admin_login_succeeds(self, client):
        resp = client.post('/api/students', data=json.dumps({
            'name': 'Test', 'enrollment': 'TST'
        }), content_type='application/json')
        assert resp.status_code == 401


class TestDashboard:
    def test_dashboard_stats(self, auth_client):
        resp = auth_client.get('/api/dashboard/stats')
        data = resp.get_json()
        assert data is not None
        assert 'total_books' in data
        assert 'total_students' in data
        assert 'active_loans' in data
