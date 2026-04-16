"""
Cria documento via WebDAV, abre no OnlyOffice editor, edita, compartilha,
e captura screenshots.
"""
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, ElementClickInterceptedException
)

NC_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "troque_esta_senha_admin"

SHOT_DIR = Path(__file__).parent.parent / "docs" / "tutorial-screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

# Remove screenshots antigos (12+)
for f in SHOT_DIR.glob("*.png"):
    n = f.stem.split("-")[0]
    if n.isdigit() and int(n) >= 12:
        f.unlink()

counter = {"n": 11}


def shot(driver, name):
    counter["n"] += 1
    fname = f"{counter['n']:02d}-{name}.png"
    driver.save_screenshot(str(SHOT_DIR / fname))
    print(f"[shot] {fname}")
    return fname


def js_click(driver, el):
    driver.execute_script("arguments[0].click();", el)


def dismiss_modals(driver):
    time.sleep(1)
    for _ in range(5):
        dismissed = False
        for sel in [
            "button.first-run-wizard__close",
            ".modal-wrapper button.primary",
            "button[aria-label*='Fechar' i]",
            "button[aria-label*='Close' i]",
        ]:
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


def login(driver, user, pwd):
    driver.get(NC_URL)
    wait = WebDriverWait(driver, 30)
    u = wait.until(EC.presence_of_element_located((By.ID, "user")))
    u.clear()
    u.send_keys(user)
    p = driver.find_element(By.ID, "password")
    p.clear()
    p.send_keys(pwd + Keys.RETURN)
    time.sleep(6)
    dismiss_modals(driver)


def create_docx_webdav():
    """Cria um .docx mínimo via WebDAV e retorna o file id."""
    from io import BytesIO
    from zipfile import ZipFile

    # Constrói o menor .docx válido possível (Open XML)
    buf = BytesIO()
    with ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>')
        z.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')
        z.writestr("word/_rels/document.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        z.writestr("word/document.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body>'
            '<w:p>'
            '<w:pPr><w:jc w:val="center"/></w:pPr>'
            '<w:r>'
            '<w:rPr><w:b/><w:sz w:val="76"/><w:szCs w:val="76"/></w:rPr>'
            '<w:t>RECEBA CAPITA BOY</w:t>'
            '</w:r>'
            '</w:p>'
            '</w:body>'
            '</w:document>')

    data = buf.getvalue()
    filename = "Relatorio da equipe.docx"
    url = f"{NC_URL}/remote.php/dav/files/{ADMIN_USER}/{filename}"
    r = requests.put(url, auth=(ADMIN_USER, ADMIN_PASS), data=data,
                     headers={"Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})
    print(f"[webdav] PUT {filename}: {r.status_code}")

    # Pega o file id via PROPFIND
    propfind = requests.request("PROPFIND", url, auth=(ADMIN_USER, ADMIN_PASS),
                                headers={"Depth": "0", "Content-Type": "application/xml"},
                                data='<?xml version="1.0"?><d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns"><d:prop><oc:fileid/></d:prop></d:propfind>')
    import re
    m = re.search(r"<oc:fileid>(\d+)</oc:fileid>", propfind.text)
    fileid = m.group(1) if m else None
    print(f"[webdav] fileid={fileid}")
    return fileid


def main():
    # 1. Cria arquivo via WebDAV
    fileid = create_docx_webdav()

    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--lang=pt-BR")
    driver = webdriver.Chrome(options=opts)

    try:
        login(driver, ADMIN_USER, ADMIN_PASS)

        # --- Files com o documento criado ---
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(4)
        dismiss_modals(driver)
        shot(driver, "files-com-documento")

        # --- Menu + Novo (screenshot do menu, para referência) ---
        print("[info] screenshot menu Novo...")
        new_btn = driver.find_element(
            By.XPATH,
            "//button[contains(.,'Novo') or contains(@aria-label,'Novo')]"
        )
        js_click(driver, new_btn)
        time.sleep(2)
        shot(driver, "files-menu-novo")
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)

        # --- Abre o documento no editor OnlyOffice ---
        print("[info] abrindo documento no editor...")
        if fileid:
            driver.get(f"{NC_URL}/index.php/apps/onlyoffice/{fileid}")
        else:
            # Tenta pelo link do arquivo na listagem
            try:
                file_link = driver.find_element(
                    By.XPATH,
                    "//a[contains(@class,'filename')][contains(.,'Relatorio')] | //*[contains(@data-cy-files-list-row-name,'Relatorio')]//a"
                )
                js_click(driver, file_link)
            except NoSuchElementException:
                print("[warn] link do arquivo não encontrado")

        time.sleep(10)
        shot(driver, "editor-carregando")

        # Espera mais para o editor carregar completamente
        time.sleep(10)
        shot(driver, "editor-onlyoffice")

        # Procura iframe do OnlyOffice
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"[info] {len(iframes)} iframes na página")
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute("src") or ""
            print(f"  [{i}] src={src[:120]}")

        oo_frame = None
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if any(k in src.lower() for k in ["onlyoffice", "documentserver", "ds-vpath", "/web-apps/"]):
                oo_frame = iframe
                break

        if oo_frame:
            print("[info] entrando no iframe do editor...")
            driver.switch_to.frame(oo_frame)
            time.sleep(5)

            # OnlyOffice pode ter iframe interno
            inner = driver.find_elements(By.TAG_NAME, "iframe")
            if inner:
                driver.switch_to.frame(inner[0])
                time.sleep(2)

            # Digita texto
            try:
                canvas = driver.find_element(By.CSS_SELECTOR, "canvas")
                ActionChains(driver).move_to_element(canvas).click().perform()
                time.sleep(1)
                text = (
                    "Relatorio da Equipe - Projeto Nextcloud\n\n"
                    "Este documento foi criado e editado online,\n"
                    "usando OnlyOffice integrado ao Nextcloud.\n\n"
                    "Exemplo de edicao colaborativa em tempo real."
                )
                ActionChains(driver).send_keys(text).perform()
                time.sleep(3)
                print("[info] texto digitado no editor")
            except NoSuchElementException:
                print("[warn] canvas não encontrado")

            driver.switch_to.default_content()
            shot(driver, "editor-com-texto")
        else:
            # Screenshot genérico — pode ser que carregou full-page
            print("[info] nenhum iframe OO detectado, screenshot genérico")
            shot(driver, "editor-fullpage")
            # Dump page source para debug
            title = driver.title
            url = driver.current_url
            print(f"  title={title}, url={url}")

        # --- Volta a Files ---
        driver.switch_to.default_content()
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(4)
        shot(driver, "files-apos-edicao")

        # --- Compartilha com bob (via UI sidebar) ---
        print("[info] abrindo sidebar de compartilhamento...")
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "[data-cy-files-list-row-name]")
            target = None
            for r in rows:
                nm = r.get_attribute("data-cy-files-list-row-name") or ""
                if "Relatorio" in nm:
                    target = r
                    break

            if not target:
                # fallback
                rows2 = driver.find_elements(By.CSS_SELECTOR, ".files-list__row")
                for r in rows2:
                    if "Relatorio" in (r.text or ""):
                        target = r
                        break

            if target:
                # Clica no nome para abrir sidebar
                name_link = target.find_element(By.CSS_SELECTOR, ".files-list__row-name-link, a")
                js_click(driver, name_link)
                time.sleep(3)
                shot(driver, "sidebar-aberto")

                # Tab compartilhamento
                for sel in [
                    "a[data-tabid='sharing']",
                    "[data-cy-sidebar-tab='sharing']",
                    "li#tab-button-sharing a",
                    "button#tab-button-sharing",
                ]:
                    try:
                        tab = driver.find_element(By.CSS_SELECTOR, sel)
                        js_click(driver, tab)
                        time.sleep(2)
                        break
                    except NoSuchElementException:
                        continue

                shot(driver, "sidebar-compartilhamento")

                # Campo de busca de share
                share_input = None
                inputs = driver.find_elements(By.CSS_SELECTOR, "input")
                for inp in inputs:
                    label = inp.get_attribute("aria-label") or ""
                    ph = inp.get_attribute("placeholder") or ""
                    if any(k in (label + ph).lower() for k in ["compartilh", "share", "pesquis", "search", "nome"]):
                        if inp.is_displayed():
                            share_input = inp
                            break

                if share_input:
                    share_input.clear()
                    share_input.send_keys("bob")
                    time.sleep(3)
                    shot(driver, "compartilhamento-busca-bob")

                    # Seleciona
                    try:
                        options = driver.find_elements(By.CSS_SELECTOR, ".sharing-search--result, .vs__dropdown-menu li, [role='option'], .option")
                        for opt in options:
                            if "bob" in opt.text.lower() or "Bob" in opt.text:
                                js_click(driver, opt)
                                time.sleep(2)
                                break
                        shot(driver, "compartilhamento-bob-ok")
                    except Exception as e:
                        print(f"[warn] selecionar bob: {e}")
                        share_input.send_keys(Keys.RETURN)
                        time.sleep(2)
                        shot(driver, "compartilhamento-bob-enter")
                else:
                    print("[warn] input de compartilhamento não encontrado")
                    shot(driver, "sidebar-sem-input")
            else:
                print("[warn] arquivo Relatorio não encontrado na lista")
        except Exception as e:
            print(f"[warn] compartilhamento: {e}")

        # --- Login como bob ---
        print("[info] login como bob...")
        driver.delete_all_cookies()
        login(driver, "bob", "senhaBob123!")
        driver.get(f"{NC_URL}/index.php/apps/files/")
        time.sleep(4)
        dismiss_modals(driver)
        shot(driver, "bob-ve-arquivo-compartilhado")

    finally:
        driver.quit()

    print(f"\nScreenshots 12-{counter['n']} em {SHOT_DIR}")


if __name__ == "__main__":
    main()
