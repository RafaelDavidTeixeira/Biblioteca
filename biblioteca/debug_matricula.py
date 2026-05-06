from app.database import init_db, get_student, update_student, list_students
import sqlite3

# Initialize
init_db('instance/biblioteca.db')

# List first 5 students to find a valid ID
students = list_students('')
print("Alunos no banco:")
for s in students[:5]:
    print(f"  ID: {s['id']}, Nome: {s['name']}, Matrícula: {s['enrollment']}")

if students:
    sid = students[0]['id']
    old_enrollment = students[0]['enrollment']
    print(f"\nTestando com aluno ID {sid}")
    print(f"Matrícula atual: {old_enrollment}")
    
    # Try to update
    new_enrollment = old_enrollment + "_TEST"
    print(f"Tentando alterar para: {new_enrollment}")
    
    updated = update_student(sid, {
        'name': students[0]['name'],
        'enrollment': new_enrollment,
        'class_name': students[0].get('class_name', ''),
        'phone': students[0].get('phone', ''),
        'email': students[0].get('email', ''),
        'notes': students[0].get('notes', '')
    })
    
    print(f"Após atualização: {updated['enrollment']}")
    
    # Revert
    update_student(sid, {
        'name': students[0]['name'],
        'enrollment': old_enrollment,
        'class_name': students[0].get('class_name', ''),
        'phone': students[0].get('phone', ''),
        'email': students[0].get('email', ''),
        'notes': students[0].get('notes', '')
    })
    print(f"Revertido para: {old_enrollment}")
else:
    print("Nenhum aluno encontrado no banco.")
