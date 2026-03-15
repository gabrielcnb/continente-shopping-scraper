from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from fuzzywuzzy import fuzz
import requests

chrome_options = Options()
chrome_options.add_experimental_option("detach", True) # Mantém o navegador abertooooooooo
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()

lista_compras = """
Água continente 6 litros
peito de frango 700g continente
batata palha continente
feijão continente
açúcar continente
arroz continente
mel continente
ovo 12 unidades
sal grosso
iogurte continente morango
banana
laranja
brócolos
cenoura
pasta de dente continente
lenço incontinencia
lenço de rosto água micelar
chocolate continente
spray glade
picanha américa do sul
""".strip().splitlines()

# Acessa o site principal
driver.get("https://www.continente.pt/")
time.sleep(3)

# Aceita os cookies
try:
    cookies_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    cookies_button.click()
    time.sleep(2)  # Tempo para o banner sumir
except:
    print("Botão de cookies não encontrado.")

# Para cada item da lista
for item in lista_compras:
    # Limpa e pesquisa o item na barra de pesquisa
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-custom-label-search"))
    )
    search_input.clear()
    search_input.send_keys(item)
    search_input.send_keys(Keys.RETURN)

    # Aguarda os resultados carregarem
    time.sleep(3)

    # Encontra o produto mais próximo utilizando fuzzy matching
    produtos = driver.find_elements(By.CLASS_NAME, "product-tile")
    produto_encontrado = None
    melhor_score = 0

    if produtos:
        for produto in produtos:
            try:
                nome_produto = produto.find_element(By.CLASS_NAME, "product-title").text
            except Exception as e:
                print(f"Erro ao obter o nome do produto: {e}")
                continue

            score = fuzz.token_set_ratio(item.lower(), nome_produto.lower())
            if score > melhor_score:
                melhor_score = score
                produto_encontrado = produto

        if not produto_encontrado or melhor_score < 60:
            produto_encontrado = produtos[0]
            print("Nenhum produto com score adequado encontrado. Usando o primeiro produto como fallback.")

        try:
            # Localiza todos os botões de "CARRINHO" utilizando o atributo aria-label, pois o texto interno pode estar vazio
            botoes_carrinho = driver.find_elements(By.XPATH, "//button[contains(@class, 'js-add-to-cart') and contains(@aria-label, 'Carrinho')]")
            
            melhor_botao = None
            melhor_botao_score = 0
            
            for botao in botoes_carrinho:
                try:
                    # Utiliza o atributo aria-label para comparação, pois o texto do botão pode não estar visível
                    botao_label = botao.get_attribute("aria-label").strip().lower()
                    score_botao = fuzz.token_set_ratio(item.lower(), botao_label)

                    if score_botao > melhor_botao_score:
                        melhor_botao_score = score_botao
                        melhor_botao = botao

                except Exception as e:
                    print(f"Erro ao comparar o texto do botão: {e}")
                    continue

            if melhor_botao:
                # Clica no botão com a melhor correspondência
                melhor_botao.click()
                print(f"Produto '{item}' adicionado ao carrinho com sucesso! Score do botão: {melhor_botao_score}")
            else:
                # Se nenhum botão com boa correspondência for encontrado, clica no primeiro botão disponível
                if botoes_carrinho:
                    botoes_carrinho[0].click()
                    print(f"Produto '{item}' adicionado ao carrinho (primeiro botão de carrinho clicado).")
                else:
                    print(f"Não encontrou botões de carrinho para '{item}'.")
            
            # Aguarda o carrinho ser atualizado
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao adicionar o produto '{item}' ao carrinho: {e}")
    else:
        print(f"Nenhum produto encontrado para '{item}'.")

input("Pressione Enter para encerrar o script e fechar o navegador...")
driver.quit()
