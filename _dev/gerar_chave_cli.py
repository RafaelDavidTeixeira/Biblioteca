import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.license import generate_license_key, get_machine_id

machine_id = input("Machine ID: ").strip().upper()
if not machine_id:
    machine_id = get_machine_id()
    print(f"Usando Machine ID local: {machine_id}")

key = generate_license_key(machine_id, "Instituicao", 365)
print(f"Chave gerada: {key}")
print("Copie a chave acima e cole no campo de ativacao.")
