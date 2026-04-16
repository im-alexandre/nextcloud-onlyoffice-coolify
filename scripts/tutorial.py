"""
Navega o Nextcloud via Selenium e captura screenshots para o tutorial.
Usuário 'bob' e grupo 'equipe' já foram criados via occ (scripts/occ_setup.ps1).
"""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

NC_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "troque_esta_senha_admin"
BOB_USER = "bob"
BOB_PASS = "senhaBob123!"

SHOT_DIR = Path(__file__).parent.parent / "docs" / "tutorial-screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

# Limpa screenshots antigos
for f in SHOT_DIR.glob("*.png"):
    f.unlink()

counter = {"n": 0}


def shot(driver, name):
    counter["n"] += 1
    fname = f"{counter['n']:02d}-{name}.png"
    driver.save_screenshot(str(SHOT_DIR / fname))
    print(f"[shot] {fname}")
    return fname


def dismiss_firstrun_modal(driver):
    """Dispensa o modal 'Nextcloud Hub' e similares."""
    time.sleep(2)
    for _ in range(5):
        # Procura botões de fechar/pular modais
        selectors = [
            "button.first-run-wizard__close",
            "button[aria-label*='Fechar' i]",
            "button[aria-label*='Close' i]",
            ".modal-container button.primary",
            "button.button-vue--vue-primary",
        ]
        for sel in selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
                    break
            except NoSuchElementException:
                continue
        # Se não tem mais modal-wrapper, sai
        try:
            driver.find_element(By.CSS_SELECTOR, ".modal-wrapper")
            time.sleep(1)
        except NoSuchElementException:
            return
    # Última tentativa: Escape
    from selenium.webdriver.common.action_chains import ActionChains
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(1)


def login(driver, user, pwd):
    driver.get(NC_URL)
    wait = WebDriverWait(driver, 30)
    user_field = wait.until(EC.presence_of_element_located((By.ID, "user")))
    user_field.clear()
    user_field.send_keys(user)
    pwd_field = driver.find_element(By.ID, "password")
    pwd_field.clear()
    pwd_field.send_keys(pwd)
    pwd_field.send_keys(Keys.RETURN)
    time.sleep(5)


def main():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--lang=pt-BR")
    driver = webdriver.Chrome(options=opts)

    try:
        # 1. Tela de login
        driver.get(NC_URL)
        time.sleep(3)
        shot(driver, "tela-login")

        # 2. Login como admin
        login(driver, ADMIN_USER, ADMIN_PASS)
        shot(driver, "apos-login-modal")

        dismiss_firstrun_modal(driver)
        time.sleep(1)
        shot(driver, "dashboard")

        # 3. Arquivos
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(4)
        dismiss_firstrun_modal(driver)
        shot(driver, "files-vazio")

        # 4. Configurações → Contas (Users)
        driver.get(f"{NC_URL}/index.php/settings/users")
        time.sleep(4)
        dismiss_firstrun_modal(driver)
        shot(driver, "contas-com-bob")

        # 5. Contas → grupo equipe
        try:
            driver.get(f"{NC_URL}/index.php/settings/users/equipe")
            time.sleep(3)
            shot(driver, "grupo-equipe")
        except Exception as e:
            print(f"[warn] grupo equipe: {e}")

        # 6. Apps — lista
        driver.get(f"{NC_URL}/index.php/settings/apps")
        time.sleep(5)
        dismiss_firstrun_modal(driver)
        shot(driver, "apps-lista")

        # 7. Apps → escritório (onde fica ONLYOFFICE)
        driver.get(f"{NC_URL}/index.php/settings/apps/office")
        time.sleep(4)
        shot(driver, "apps-categoria-office")

        # 8. Admin settings (visão geral)
        driver.get(f"{NC_URL}/index.php/settings/admin")
        time.sleep(4)
        dismiss_firstrun_modal(driver)
        shot(driver, "admin-visao-geral")

        # 9. Compartilhamento — criar arquivo de teste via WebDAV? Via UI é chato.
        #    Aqui só navega a tela de Files novamente com o sidebar do usuário.
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(3)
        # Tenta abrir menu "+" para mostrar criação de arquivo
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Novo' i], button[aria-label*='New' i]")
            btn.click()
            time.sleep(1)
            shot(driver, "files-menu-novo")
            # Fecha menu
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
        except Exception as e:
            print(f"[warn] menu novo: {e}")

        # 10. Logout
        driver.get(f"{NC_URL}/index.php/logout")
        time.sleep(4)

        # 11. Login como bob
        login(driver, BOB_USER, BOB_PASS)
        dismiss_firstrun_modal(driver)
        time.sleep(2)
        shot(driver, "bob-dashboard")

        # 12. Bob em Files
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(4)
        dismiss_firstrun_modal(driver)
        shot(driver, "bob-files")

    finally:
        driver.quit()

    print(f"\n{counter['n']} screenshots em {SHOT_DIR}")


if __name__ == "__main__":
    main()
