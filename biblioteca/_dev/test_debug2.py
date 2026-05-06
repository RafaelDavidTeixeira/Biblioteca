from app.database import init_db, get_student, update_student, list_students
import sys

init_db('instance/biblioteca.db')

students = list_students('')
if students:
    sid = students[0]['id']
    old = students[0]['enrollment']
    print(f"Aluno: {students[0]['name']}")
    print(f"Matrícula atual: {old}")
    
    new_enrollment = old + "_TEST"
    print(f"Tentando alterar para: {new_enrollment}")
    
    result = update_student(sid, {
        'name': students[0]['name'],
        'enrollment': new_enrollment,
        'class_name': students[0].get('class_name', ''),
        'phone': students[0].get('phone', ''),
        'email': students[0].get('email', ''),
        'notes': students[0].get('notes', '')
    })
    
    print(f"Resultado: {result['enrollment']}")
    
    # Revert
    update_student(sid, {
        'name': students[0]['name'],
        'enrollment': old,
        'class_name': students[0].get('class_name', ''),
        'phone': students[0].get('phone', ''),
        'email': students[0].get('email', ''),
        'notes': students[0].get('notes', '')
    })
    print(f"Revertido para: {old}")
else:
    print("Nenhum aluno encontrado")
