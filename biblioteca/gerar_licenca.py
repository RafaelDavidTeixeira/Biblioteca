"""
GERADOR DE LICENCAS - Biblioteca Sistema
Uso exclusivo do desenvolvedor/distribuidor.
Execute: python gerar_licenca.py
"""
import sys, os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.license import generate_license_key, validate_license_key, get_machine_id


def self_test():
    print("\n" + "-"*56)
    print("  AUTO-TESTE DO SISTEMA DE LICENCAS")
    print("-"*56)
    mid = get_machine_id()
    print(f"  Machine ID local: {mid}")
    key = generate_license_key(mid, "Teste Auto", 365)
    print(f"  Chave gerada: {key}")
    result = validate_license_key(key, mid)
    status = "VALIDA" if result['valid'] else "INVALIDA"
    print(f"  Validacao: {status}")
    if result['valid']:
        print(f"  Valida ate: {result['valid_until']}")
    else:
        print(f"  Erro: {result['error']}")
    print("-"*56)
    return result['valid']


def main():
    print("\n" + "="*56)
    print("  GERADOR DE LICENCAS - Biblioteca Sistema")
    print("="*56)
    print()

    while True:
        print("Opcoes:")
        print("  [0] Auto-teste (gera e valida localmente)")
        print("  [1] Gerar nova licenca")
        print("  [2] Validar/verificar uma chave")
        print("  [9] Sair")
        print()
        opt = input("Escolha: ").strip()

        if opt == '9':
            print("Saindo.")
            break

        elif opt == '0':
            self_test()
            print()

        elif opt == '1':
            print()
            machine_id = input("ID da Maquina do cliente (ex: A1B2-C3D4-E5F6-G7H8): ").strip().upper()
            if not machine_id:
                print("  ID da maquina e obrigatorio.\n")
                continue

            institution = input("Nome da instituicao: ").strip()
            if not institution:
                institution = "Instituicao"

            print("Validade:")
            print("  [1] 1 ano (365 dias)")
            print("  [2] 2 anos (730 dias)")
            print("  [3] 3 anos (1095 dias)")
            print("  [4] Personalizado (dias)")
            v = input("Opcao [1]: ").strip() or '1'

            days_map = {'1': 365, '2': 730, '3': 1095}
            if v in days_map:
                valid_days = days_map[v]
            elif v == '4':
                valid_days = int(input("Quantos dias? ").strip() or '365')
            else:
                valid_days = 365

            key = generate_license_key(machine_id, institution, valid_days)

            # Save key to file for easy copying
            key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chave_gerada.txt')
            with open(key_file, 'w', encoding='utf-8') as f:
                f.write(key)

            print()
            print("="*56)
            print("  LICENCA GERADA COM SUCESSO")
            print("="*56)
            print(f"  Instituicao : {institution}")
            print(f"  Machine ID  : {machine_id}")
            print(f"  Validade    : {valid_days} dias")
            print()
            print(f"  CHAVE DE LICENCA (copie TUDO abaixo):")
            print()
            print("  " + key)
            print()
            print("="*56)
            print()
            print(f"  Chave salva em: {key_file}")
            print(f"  (Voce pode abrir o arquivo e copiar de la)")
            print("  Envie a chave ao cliente para ativacao.\n")

        elif opt == '2':
            print()
            key = input("Chave a verificar: ").strip()
            machine_id = input("ID da Maquina: ").strip().upper()
            result = validate_license_key(key, machine_id)
            print()
            if result['valid']:
                print(f"  Licenca VALIDA")
                print(f"  Valida ate  : {result['valid_until']}")
            else:
                print(f"  Licenca INVALIDA: {result['error']}")
            print()

        else:
            print("Opcao invalida.\n")


if __name__ == '__main__':
    main()
