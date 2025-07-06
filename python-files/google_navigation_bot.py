
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fp.fp import FreeProxy

class GoogleNavigationBot:
    def __init__(self, keyword, target_site, navigation_time=120):
        """
        Inicializa o bot de navegação

        Args:
            keyword (str): Palavra-chave para busca no Google
            target_site (str): Site específico para clicar nos resultados
            navigation_time (int): Tempo de navegação em segundos (padrão: 2 minutos)
        """
        self.keyword = keyword
        self.target_site = target_site
        self.navigation_time = navigation_time
        self.setup_logging()

    def setup_logging(self):
        """Configura o logging para acompanhar o funcionamento do bot"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_navigation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_random_proxy(self):
        """Obtém um proxy gratuito aleatório"""
        try:
            proxy = FreeProxy(
                timeout=1, 
                rand=True, 
                anonym=True
            ).get()
            self.logger.info(f"Proxy obtido: {proxy}")
            return proxy
        except Exception as e:
            self.logger.warning(f"Erro ao obter proxy: {e}")
            return None

    def create_driver_with_proxy(self, proxy=None):
        """Cria uma instância do Chrome com proxy e configurações stealth"""
        chrome_options = Options()

        # Configurações para parecer um usuário real
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent aleatório
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")

        # Configurações adicionais para anonimato
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Configurar proxy se fornecido
        if proxy:
            chrome_options.add_argument(f"--proxy-server={proxy}")

        driver = webdriver.Chrome(options=chrome_options)

        # Executa script para remover características de bot
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Cria delays aleatórios para simular comportamento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def random_mouse_movement(self, driver):
        """Simula movimentos aleatórios do mouse"""
        try:
            actions = ActionChains(driver)
            # Movimentos aleatórios
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.5))
            actions.perform()
        except Exception as e:
            self.logger.warning(f"Erro no movimento do mouse: {e}")

    def random_scroll(self, driver):
        """Simula rolagem aleatória na página"""
        try:
            # Scroll aleatório
            scroll_amount = random.randint(100, 500)
            direction = random.choice([1, -1])  # Para cima ou para baixo
            driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction});")
            self.human_like_delay(0.5, 2)
        except Exception as e:
            self.logger.warning(f"Erro na rolagem: {e}")

    def search_google(self, driver):
        """Realiza busca no Google"""
        try:
            self.logger.info("Acessando o Google...")
            driver.get("https://www.google.com")

            # Aguarda a página carregar
            self.human_like_delay(2, 4)

            # Localiza e clica na caixa de busca
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )

            # Simula digitação humana
            search_box.click()
            self.human_like_delay(0.5, 1)

            # Digita a palavra-chave caractere por caractere
            for char in self.keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

            self.human_like_delay(1, 2)
            search_box.send_keys(Keys.RETURN)

            self.logger.info(f"Busca realizada: {self.keyword}")
            return True

        except Exception as e:
            self.logger.error(f"Erro na busca do Google: {e}")
            return False

    def find_and_click_target_site(self, driver):
        """Localiza e clica no site especificado nos resultados"""
        try:
            self.logger.info(f"Procurando por links do site: {self.target_site}")

            # Aguarda os resultados carregarem
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )

            # Simula movimento do mouse antes de procurar
            self.random_mouse_movement(driver)
            self.human_like_delay(2, 4)

            # Procura por links que contenham o site especificado
            results = driver.find_elements(By.CSS_SELECTOR, "div.g a[href*='" + self.target_site + "']")

            if results:
                # Clica no primeiro resultado encontrado
                target_link = results[0]
                self.logger.info(f"Site encontrado. Clicando no link...")

                # Movimento do mouse para o link
                actions = ActionChains(driver)
                actions.move_to_element(target_link).perform()
                self.human_like_delay(1, 2)

                target_link.click()
                return True
            else:
                self.logger.warning(f"Site {self.target_site} não encontrado nos resultados")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao procurar site: {e}")
            return False

    def navigate_website(self, driver):
        """Navega pelo site por um tempo determinado"""
        try:
            self.logger.info(f"Iniciando navegação por {self.navigation_time} segundos...")

            start_time = time.time()
            actions_performed = 0

            while time.time() - start_time < self.navigation_time:
                # Lista de ações possíveis
                actions = [
                    self.random_scroll,
                    self.random_mouse_movement,
                    self.click_random_element
                ]

                # Executa ação aleatória
                action = random.choice(actions)
                try:
                    action(driver)
                    actions_performed += 1
                except:
                    pass

                # Delay entre ações
                self.human_like_delay(3, 8)

            self.logger.info(f"Navegação concluída. {actions_performed} ações realizadas.")

        except Exception as e:
            self.logger.error(f"Erro durante navegação: {e}")

    def click_random_element(self, driver):
        """Clica em elementos aleatórios da página"""
        try:
            # Procura por elementos clicáveis seguros
            clickable_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                "a:not([href*='logout']):not([href*='exit']):not([href*='download']), button:not([type='submit'])"
            )

            if clickable_elements:
                # Filtra elementos visíveis
                visible_elements = [elem for elem in clickable_elements if elem.is_displayed()]

                if visible_elements:
                    element = random.choice(visible_elements[:5])  # Limita aos primeiros 5
                    actions = ActionChains(driver)
                    actions.move_to_element(element).pause(1).click().perform()
                    self.logger.info("Clique em elemento aleatório realizado")

        except Exception as e:
            self.logger.warning(f"Erro ao clicar em elemento: {e}")

    def run_single_session(self):
        """Executa uma sessão completa de navegação"""
        driver = None
        proxy = None

        try:
            # Obtém proxy aleatório
            proxy = self.get_random_proxy()

            # Cria driver com proxy
            driver = self.create_driver_with_proxy(proxy)

            self.logger.info("=== INICIANDO NOVA SESSÃO ===")
            if proxy:
                self.logger.info(f"Usando proxy: {proxy}")

            # Executa busca no Google
            if not self.search_google(driver):
                return False

            self.human_like_delay(2, 4)

            # Procura e clica no site especificado
            if not self.find_and_click_target_site(driver):
                return False

            self.human_like_delay(3, 5)

            # Navega pelo site
            self.navigate_website(driver)

            self.logger.info("=== SESSÃO CONCLUÍDA COM SUCESSO ===")
            return True

        except Exception as e:
            self.logger.error(f"Erro na sessão: {e}")
            return False

        finally:
            if driver:
                driver.quit()
                self.logger.info("Driver fechado")

    def run_continuous(self, max_sessions=None):
        """Executa o bot continuamente"""
        session_count = 0

        self.logger.info(f"Iniciando bot de navegação para '{self.keyword}' -> '{self.target_site}'")

        try:
            while True:
                session_count += 1

                if max_sessions and session_count > max_sessions:
                    break

                self.logger.info(f"\n--- SESSÃO {session_count} ---")

                success = self.run_single_session()

                if success:
                    self.logger.info(f"Sessão {session_count} executada com sucesso")
                else:
                    self.logger.warning(f"Sessão {session_count} falhou")

                # Pausa entre sessões para mudar IP
                if max_sessions is None or session_count < max_sessions:
                    wait_time = random.randint(60, 180)  # 1-3 minutos
                    self.logger.info(f"Aguardando {wait_time} segundos antes da próxima sessão...")
                    time.sleep(wait_time)

        except KeyboardInterrupt:
            self.logger.info("Bot interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro fatal: {e}")


# Exemplo de uso
if __name__ == "__main__":
    # Configurações do bot
    KEYWORD = "python programming tutorial"
    TARGET_SITE = "python.org"
    NAVIGATION_TIME = 120  # 2 minutos

    # Cria e executa o bot
    bot = GoogleNavigationBot(
        keyword=KEYWORD,
        target_site=TARGET_SITE,
        navigation_time=NAVIGATION_TIME
    )

    # Executa 5 sessões como exemplo
    bot.run_continuous(max_sessions=5)
