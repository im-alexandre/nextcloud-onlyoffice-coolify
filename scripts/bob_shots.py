"""Sessão separada para login como bob e screenshots."""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NC_URL = "http://localhost:8080"
SHOT_DIR = Path(__file__).parent.parent / "docs" / "tutorial-screenshots"

opts = webdriver.ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1400,900")
opts.add_argument("--lang=pt-BR")
driver = webdriver.Chrome(options=opts)

def shot(name):
    p = SHOT_DIR / name
    driver.save_screenshot(str(p))
    print(f"[shot] {name}")

try:
    driver.get(NC_URL)
    wait = WebDriverWait(driver, 30)
    u = wait.until(EC.presence_of_element_located((By.ID, "user")))
    u.send_keys("bob")
    driver.find_element(By.ID, "password").send_keys("senhaBob123!" + Keys.RETURN)
    time.sleep(6)
    # Dispensa modal
    for sel in ["button.first-run-wizard__close", ".modal-container button.primary"]:
        try:
            b = driver.find_element(By.CSS_SELECTOR, sel)
            if b.is_displayed():
                b.click()
                time.sleep(1)
        except Exception:
            pass
    time.sleep(1)
    shot("10-bob-dashboard.png")
    driver.get(f"{NC_URL}/index.php/apps/files/")
    time.sleep(4)
    shot("11-bob-files.png")
finally:
    driver.quit()
