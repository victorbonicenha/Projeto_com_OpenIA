import os
import re
import shutil
import requests
import pdfplumber
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from transformers import pipeline
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from main import IADividaAtiva
from langsmith import traceable
import os

load_dotenv()

CNPJ_BASE = os.getenv("CNPJ_BASE")
API_KEY = os.getenv("CHAVE_API")


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "CND_Divida_Ativa"

data_hoje = datetime.now().strftime('%d-%m-%Y')
base_path = r"C:\Users\vbonicenha\Desktop\ApiLira"
pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")

meses = {
        '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
        '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
        '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

mes_atual = datetime.now().strftime('%m')
pasta_mes = f"{mes_atual} - {meses[mes_atual]}"
ano_atual = datetime.now().strftime('%Y')

pasta_destino = os.path.join(base_path, "CND - Divida Ativa", ano_atual, pasta_mes)

@traceable
def iniciar_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service, options=chrome_options)
    return navegador

@traceable
def resolver_captcha_anticaptcha(api_key, site_key, site_url, navegador):
    url_create = "https://api.anti-captcha.com/createTask"
    url_result = "https://api.anti-captcha.com/getTaskResult"

    payload = {
        "clientKey": api_key,
        "task": {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key}}

    response = requests.post(url_create, json=payload)
    result = response.json()

    if result.get('errorId') != 0:
        print(f"[ERRO] AntiCaptcha: {result.get('errorDescription', 'Erro desconhecido')}")
        return None

    task_id = result.get('taskId')
    print(f"[INFO] Task criada. ID: {task_id}")
    for tentativa in range(20):
        sleep(3)
        res = requests.post(url_result, json={
            "clientKey": api_key,
            "taskId": task_id}).json()

        if res.get('status') == 'ready':
            token = res.get('solution', {}).get('gRecaptchaResponse')
            print(f"[INFO] Captcha resolvido com sucesso.")
            try:
                navegador.execute_script('document.getElementById("g-recaptcha-response").value = arguments[0];',token)
                navegador.execute_script("""
                    for (let i in ___grecaptcha_cfg.clients) {
                        for (let j in ___grecaptcha_cfg.clients[i]) {
                            let client = ___grecaptcha_cfg.clients[i][j];
                            if (client && client.callback) {
                                client.callback(arguments[0]);
                                return;
                            }
                        }
                    }
                """, token)

                print("[INFO] Token injetado e callback executado.")
                return True
            except Exception as e:
                print(f"[ERRO] Falha ao injetar token: {e}")
                return None

        print(f"[INFO] Tentativa {tentativa+1}: Captcha ainda não pronto...")

    print("[ERRO] Captcha não foi resolvido a tempo.")
    return None

@traceable
def extrair_info_ia(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto_pdf = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    ia = IADividaAtiva()
    respostas = ia.extrair_informacoes(texto_pdf)

    mensagem = (
        "Certidão Dívida Ativa - Extração IA\n\n" +
        "\n".join([f"{pergunta}: {resposta}" for pergunta, resposta in respostas.items()]))

    print(mensagem)
    return mensagem

@traceable
def cnd_divida_ativa():
    url_site = 'https://www.dividaativa.pge.sp.gov.br/sc/pages/home/home_novo.jsf'
    navegador = iniciar_selenium()
    navegador.get(url_site)
    sleep(3)

    try:
        navegador.find_element(By.XPATH, '//*[@id="modalPanelDebIpvaIDContentDiv"]/div').click()
        print("[INFO] Fechou pop-up.")
        sleep(1)
    except:
        print("[INFO] Sem pop-up.")

    navegador.find_element(By.XPATH, '//*[@id="menu:j_id99_span"]').click()
    sleep(1)

    try:
        wait = WebDriverWait(navegador, 10)
        elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menu:itemMenu3649:anchor"]')))
        elemento.click()
    except Exception as e:
        navegador.quit()
        return

    wait = WebDriverWait(navegador, 10)
    campo_cnpj = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="emitirCrda:crdaInputCnpjBase"]')))
    campo_cnpj.send_keys(CNPJ_BASE)

    site_key = navegador.find_element(By.XPATH, '//*[@id="recaptcha"]').get_attribute('data-sitekey')
    print(f"[INFO] Sitekey capturada: {site_key}")

    token = resolver_captcha_anticaptcha(API_KEY, site_key, url_site, navegador)
    if not token:
        navegador.quit()
        return

    try:
        navegador.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0];', token)
        sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="emitirCrda:j_id78_body"]/div[2]/input[2]').click()
        print("[INFO] Aguardando geração da certidão...")
        sleep(10)

        arquivos_encontrados = False
        for arquivo in os.listdir(pasta_downloads):
            if arquivo.endswith(".pdf") and "crda" in arquivo.lower():
                caminho_origem = os.path.join(pasta_downloads, arquivo)
                nome_novo = f"{os.path.splitext(arquivo)[0]}_validade_{data_hoje}.pdf"
                caminho_final = os.path.join(pasta_destino, nome_novo)
                try:
                    os.makedirs(pasta_destino, exist_ok=True)
                    shutil.move(caminho_origem, caminho_final)
                    print(f"[INFO] Arquivo movido para: {caminho_final}")
                    extrair_info_ia(caminho_final)
                    arquivos_encontrados = True
                    break
                except Exception as move_error:
                    print(f"Erro ao mover arquivo PDF: {str(move_error)}")

        if not arquivos_encontrados:
          print("Nenhum arquivo PDF com 'crda' encontrado na pasta de downloads.")

    except Exception as e:
        print(f"Erro ao gerar certidão: {str(e)}")

    navegador.quit()

if __name__ == "__main__":
    max_tentativas = 3
    tentativa = 0
    sucesso = False

    while tentativa < max_tentativas and not sucesso:
        tentativa += 1
        print(f"[INFO] Iniciando tentativa {tentativa}/{max_tentativas}...")

        try:
            cnd_divida_ativa()
            sucesso = True
            print("[INFO] Processo finalizado com sucesso.")
        except Exception as e:
            print(f"[ERRO] Tentativa {tentativa} falhou: {str(e)}")
            if tentativa < max_tentativas:
                print("[INFO] Tentando novamente...")
                sleep(5)
            else:
                print("[ERRO] Todas as tentativas falharam.")

