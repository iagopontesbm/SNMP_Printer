import snmp
import email_send as email

MIB_COD = '1.3.6.1.2.1.43.18.1.1.8.1.1'  # Descrição alerta

# Lista de impressoras, dicionário com chave IP e valor descrição equipamento. {'127.0.0.1': 'LOCAL'}
impressoras = []

# Parte inicial do email
corpo_email = 'Bom dia,\n\nSegue status das impressoras com alerta.\n' \
              'Entrar em contato com a loja e proceder com a melhor tratativa.\n'

# Verificação da informação em cada impressora e concatenação da mensagem para o email.
for dict_imp in impressoras:
    for ip_imp, nome_imp in dict_imp.items():
        imp = snmp.Snmp(ip_imp, MIB_COD)
        try:
            # Executa conexão
            imp.snmp_connection()
        except:
            # Verifica se houve falha na conexão.
            corpo_email += f"\n{ip_imp}: {nome_imp}\nFalha de conexão!\n"
        else:
            if imp.cod_alert not in ['Imprimindo', 'Em espera', 'Pronta']:
                corpo_email += f"\n{ip_imp}: {nome_imp}\n{imp.cod_alert}\n"


print(corpo_email)

# Enviar email
email.send_email(corpo_email)
print("Email enviado!")
