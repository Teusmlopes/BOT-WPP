# TESTE
import os.path
import random
from urllib.parse import quote
import time
from datetime import datetime, date

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# TEMPOS ALEATÓRIOS
ciclo_navegador = random.randint(30, 50)
ciclo_envio_mensagem = random.randint(30, 50)
reiniciar_ciclo = random.randint(30, 40)



# CHROME 
servico = Service(ChromeDriverManager().install())
# INICIANDO NAVEGOR CHROME 
navegador = webdriver.Chrome(service=servico)



# IDs DE CONEXÃO COM O GOOGLE SHEETS
ESCOPO = ['https://www.googleapis.com/auth/spreadsheets.readonly']
IDGOOGLESHEETS = 'ID PLANILHA AQUI'
IDTABELA = 'TESTE!A2:Z1000'
#CONEXÃO GOOGLE SHEETS 
def GOOGLESHEETS():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ESCOPO)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ESCOPO)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=IDGOOGLESHEETS,
                                    range=IDTABELA).execute()
        return result.get('values', [])
    except HttpError as err:
        print(err)
        return []



# INICIO DA AUTOMOÇÃO DE ENVIO DE MENSAGEM
def enviar_mensagens():
    dados = GOOGLESHEETS()
    if not dados:
        print("ERRO01")
        return    ##### ERRO01 - VERIFIQUE A CONEXÃO COM O GOOGLE SHEETS

    contador = 0
    for coluna in dados:
        if len(coluna) < 3:
            print(f"Dados insuficientes para a linha: {coluna}")
            continue

        nome = coluna[0]
        telefone = coluna[1]
        data = coluna[2]

        try:
            data = datetime.strptime(data, "%d/%m/%Y").date()
            print(f"DATA ATUAL: {date.today()}")
            print(f"DATA INDICADA NA TABELA: {data}  ")
        except ValueError:
            print(f"DATA INVALIDA {data}")
            continue

        if date.today() == data:
            mensagens = [
                f"Oii {nome},\n\nMe chamo Tais sou consultora de vendas na 299/Ducati Brasília.\nSelecionei algumas pessoas em potencial pra enviar as novidades e ofertas de equipamentos aqui da loja.\n\nVou te mandar aqui pelo WhatsApp !!",
                f"Além disso, {nome}, temos uma promoção especial em equipamentos que você pode gostar!",
                f"Por último, não esqueça de verificar nosso site para mais novidades!"
            ]

            for mensagem in mensagens:
                linkWpp = f"https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}"
                navegador.get(linkWpp)

                try:
                    wait = WebDriverWait(navegador, 120)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
                except TimeoutException:
                    print(f"Número inválido: {telefone}")
                    break  # Para sair do loop de mensagens se o número for inválido

                time.sleep(2)
                navegador.find_element(By.XPATH, '//span[@data-icon="send"]').click()
                time.sleep(ciclo_envio_mensagem)  # Aguarda antes de enviar a próxima mensagem

            contador += 1

            if contador == 5:
                time.sleep(reiniciar_ciclo)
                contador = 0


#PROSSEGUIR MESMO APÓS O CHORME IDENTIFICAR A AUTOMATIZAÇÃO 
def main():
    navegador.get("https://web.whatsapp.com/")
    if "WhatsApp" not in navegador.title:
        input("Por favor, faça o login no WhatsApp Web e pressione Enter para continuar...")

    wait = WebDriverWait(navegador, 60)
    wait.until(EC.presence_of_element_located((By.ID, 'side')))

    #ENVIAR MENSAGEM 
    enviar_mensagens()

    # FECHAR NAVEGADOR APOS EXECUTAR O CODIGO - CORRIGIR DEPOIS PARA DESCONECTAR O WHATSAPP 
    navegador.quit()

if __name__ == '__main__':
    main()