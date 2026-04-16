"""Captura Bob logado vendo arquivo compartilhado."""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

NC_URL = "http://localhost:8080"
SHOT_DIR = Path(__file__).parent.parent / "docs" / "tutorial-screenshots"

def js_click(driver, el):
    driver.execute_script("arguments[0].click();", el)

def dismiss_modals(driver):
    time.sleep(1)
    for _ in range(5):
        dismissed = False
        for sel in ["button.first-run-wizard__close", ".modal-wrapper button.primary",
                     "button[aria-label*='Fechar' i]", "button[aria-label*='Close' i]"]:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    js_click(driver, btn)
                    time.sleep(1)
                    dismissed = True
                    break
            except (NoSuchElementException, ElementClickInterceptedException):
                continue
        if not dismissed:
            break
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(0.5)

def shot(name):
    p = SHOT_DIR / name
    driver.save_screenshot(str(p))
    print(f"[shot] {name}")

opts = webdriver.ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1400,900")
opts.add_argument("--lang=pt-BR")
driver = webdriver.Chrome(options=opts)

try:
    driver.get(NC_URL)
    wait = WebDriverWait(driver, 30)
    u = wait.until(EC.presence_of_element_located((By.ID, "user")))
    u.send_keys("bob")
    driver.find_element(By.ID, "password").send_keys("senhaBob123!" + Keys.RETURN)
    time.sleep(6)
    dismiss_modals(driver)

    driver.get(f"{NC_URL}/index.php/apps/files/")
    time.sleep(4)
    dismiss_modals(driver)
    shot("21-bob-files-com-compartilhamento.png")

    # Navega para "Compartilhados comigo"
    try:
        for sel in ["a[data-cy-files-navigation-item='shareoverview']",
                     "a[href*='sharingin']", "a[href*='shareoverview']"]:
            try:
                link = driver.find_element(By.CSS_SELECTOR, sel)
                js_click(driver, link)
                time.sleep(3)
                break
            except NoSuchElementException:
                continue
        shot("22-bob-compartilhados-comigo.png")
    except Exception as e:
        print(f"[warn] nav compartilhados: {e}")

    # Abre o documento compartilhado no editor
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "[data-cy-files-list-row-name], .files-list__row")
        for r in rows:
            txt = r.get_attribute("data-cy-files-list-row-name") or r.text or ""
            if "Relatorio" in txt:
                link = r.find_element(By.CSS_SELECTOR, ".files-list__row-name-link, a")
                js_click(driver, link)
                time.sleep(12)
                shot("23-bob-editando-documento.png")
                break
    except Exception as e:
        print(f"[warn] abrir doc: {e}")

finally:
    driver.quit()
