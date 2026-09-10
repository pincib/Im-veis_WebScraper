import csv
import os
import re
import time
from typing import Dict, List, Set
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URLS = {
    "zap_venda": "https://www.zapimoveis.com.br/venda/imoveis/rj+niteroi++s-francisco/",
    "vivareal_venda": "https://www.vivareal.com.br/venda/rj/niteroi/bairros/sao-francisco/",
    "zap_aluguel": "https://www.zapimoveis.com.br/aluguel/imoveis/rj+niteroi++s-francisco/",
    "vivareal_aluguel": "https://www.vivareal.com.br/aluguel/rj/niteroi/bairros/sao-francisco/",
}

OUTPUT_FOLDER = os.path.join("WebScrap", "Second", "saida")


def clean_text(value: str) -> str:
    if value is None:
        return ""
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def build_browser(browser_name: str):
    browser_name = (browser_name or "edge").lower()

    if browser_name in {"edge", "msedge", "microsoftedge"}:
        options = EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1500,1200")
        return webdriver.Edge(options=options)

    if browser_name in {"firefox", "ff"}:
        options = FirefoxOptions()
        options.add_argument("--width=1500")
        options.add_argument("--height=1200")
        return webdriver.Firefox(options=options)

    if browser_name == "zen":
        options = FirefoxOptions()
        zen_paths = [
            r"C:\Program Files\Zen Browser\zen.exe",
            r"C:\Program Files (x86)\Zen Browser\zen.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Zen\zen.exe",
        ]
        expanded = [os.path.expandvars(p) for p in zen_paths]
        for path in expanded:
            if os.path.exists(path):
                options.binary_location = path
                break
        options.add_argument("--width=1500")
        options.add_argument("--height=1200")
        return webdriver.Firefox(options=options)

    raise ValueError(f"Navegador não suportado: {browser_name}")


def parse_card_text(text: str, href: str = "") -> Dict[str, str]:
    text = clean_text(text)
    if not text:
        return {"titulo": "", "preco": "", "endereco": "", "quartos": "", "banheiros": "", "area": "", "link": ""}

    titulo = ""
    if href:
        path = href.split("/imovel/")[-1].split("?", 1)[0]
        path = path.replace("-id-", " ")
        path = re.sub(r"^venda-|^aluguel-", "", path)
        path = path.replace("-sao-francisco", " São Francisco")
        path = path.replace("-niteroi", " Niterói")
        path = path.replace("-rj", " RJ")
        path = re.sub(r"-(\d+)m2", r" \1m²", path, flags=re.I)
        path = re.sub(r"-", " ", path)
        path = re.sub(r"\s+", " ", path).strip()
        titulo = path

    if not titulo:
        titulo = text[:220]
        if len(titulo) > 180:
            titulo = titulo[:180].rsplit(" ", 1)[0]

    preco = ""
    match = re.search(r"R\$\s*([\d\.,]+)", text, flags=re.I)
    if match:
        preco = match.group(1)

    endereco = ""
    # Prioridade: rua/avenida/travessa/etc. em texto do cartão
    street_match = re.search(r"(?:Rua|Avenida|Travessa|Alameda|Praça|Estrada|Bairro)\s+[A-Za-zÀ-ÿ0-9\s\.\-]+", text)
    if street_match:
        endereco = street_match.group(0)
    elif "São Francisco, Niterói" in text:
        endereco = "São Francisco, Niterói"

    quartos = ""
    match = re.search(r"(?:Quantidade de quartos|quartos?)[^\d]*(\d+)", text, flags=re.I)
    if match:
        quartos = match.group(1)
    else:
        match = re.search(r"(\d+)\s*quarto", text, flags=re.I)
        if match:
            quartos = match.group(1)

    banheiros = ""
    match = re.search(r"(?:Quantidade de banheiros|banheiros?)[^\d]*(\d+)", text, flags=re.I)
    if match:
        banheiros = match.group(1)
    else:
        match = re.search(r"(\d+)\s*banheiro", text, flags=re.I)
        if match:
            banheiros = match.group(1)

    area = ""
    match = re.search(r"(?:Tamanho do imóvel|Área|área)[^\d]*(\d+)\s*(?:m²|m2|m\^2)", text, flags=re.I)
    if match:
        area = match.group(1)
    else:
        match = re.search(r"(\d+)\s*(?:m²|m2|m\^2)", text, flags=re.I)
        if match:
            area = match.group(1)

    return {
        "titulo": clean_text(titulo),
        "preco": clean_text(preco),
        "endereco": clean_text(endereco),
        "quartos": clean_text(quartos),
        "banheiros": clean_text(banheiros),
        "area": clean_text(area),
        "link": "",
    }


def deduplicate(properties: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: Set[str] = set()
    unique: List[Dict[str, str]] = []
    for prop in properties:
        signature = (
            clean_text(prop.get("titulo", "")),
            clean_text(prop.get("preco", "")),
            clean_text(prop.get("endereco", "")),
            clean_text(prop.get("link", "")),
        )
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(prop)
    return unique


def export_csv(properties: List[Dict[str, str]], filename: str) -> None:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["titulo", "preco", "endereco", "quartos", "banheiros", "area", "link", "site"])
        writer.writeheader()
        for prop in properties:
            writer.writerow({
                "titulo": prop.get("titulo", ""),
                "preco": prop.get("preco", ""),
                "endereco": prop.get("endereco", ""),
                "quartos": prop.get("quartos", ""),
                "banheiros": prop.get("banheiros", ""),
                "area": prop.get("area", ""),
                "link": prop.get("link", ""),
                "site": prop.get("site", ""),
            })
    print(f"CSV exportado em: {path} | total: {len(properties)}")


def build_page_url(base_url: str, page_number: int) -> str:
    if page_number <= 1:
        return base_url

    parsed = urlparse(base_url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    params["pagina"] = str(page_number)
    new_query = urlencode(params)
    return urlunparse(parsed._replace(query=new_query))


def collect_listing_links(driver, base_url: str, max_scrolls: int = 40, max_pages: int = 200) -> List[str]:
    seen_links: Set[str] = set()
    page_number = 1
    stable_pages = 0

    while page_number <= max_pages:
        url = build_page_url(base_url, page_number)
        driver.get(url)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        previous_count = len(seen_links)
        for _ in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.8)

        page_hrefs: Set[str] = set()
        for link in driver.find_elements(By.CSS_SELECTOR, 'a[href*="/imovel/"]'):
            href = (link.get_attribute("href") or "").strip()
            if href and "/imovel/" in href:
                page_hrefs.add(href)

        if not page_hrefs:
            break

        count_before = len(seen_links)
        seen_links.update(page_hrefs)
        count_after = len(seen_links)

        if count_after == count_before:
            stable_pages += 1
            if stable_pages >= 2:
                break
        else:
            stable_pages = 0

        next_page_href = None
        for link in driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="página "], a[href*="&pagina="]'):
            href = (link.get_attribute("href") or "").strip()
            if not href:
                continue
            match = re.search(r"[?&]pagina=(\d+)", href)
            if not match:
                continue
            candidate = int(match.group(1))
            if candidate > page_number:
                next_page_href = href
                break

        if not next_page_href:
            if count_after == previous_count:
                break
            page_number += 1
            continue

        page_number += 1

    return list(seen_links)


def scrape_site(name: str, url: str, browser_name: str) -> None:
    print(f"\n>>> Coletando {name}: {url} usando {browser_name}")
    driver = build_browser(browser_name)
    try:
        driver.get(url)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
        )

        links = collect_listing_links(driver, url, max_scrolls=40, max_pages=150)
        print(f"Links de imóveis encontrados: {len(links)}")

        props: List[Dict[str, str]] = []
        seen_links: Set[str] = set()
        for href in links:
            href = href.strip()
            if not href or "/imovel/" not in href:
                continue
            if href in seen_links:
                continue
            seen_links.add(href)

            element = driver.execute_script(
                """
                const items = [...document.querySelectorAll('a[href*="/imovel/"]')];
                for (const el of items) {
                    if ((el.href || '').trim() === arguments[0]) return el.textContent || '';
                }
                return '';
                """,
                href,
            )

            text = clean_text(element)
            if not text:
                continue

            parsed = parse_card_text(text, href)
            parsed["link"] = href if href.startswith("http") else "https://www.zapimoveis.com.br" + href
            parsed["site"] = url
            props.append(parsed)

        final_props = deduplicate(props)
        export_csv(final_props, f"{name}.csv")
    finally:
        driver.quit()


def main() -> None:
    browser_name = os.environ.get("SELENIUM_BROWSER", "edge")
    for name, url in URLS.items():
        try:
            scrape_site(name, url, browser_name)
        except Exception as exc:
            print(f"Erro ao processar {name}: {exc}")


if __name__ == "__main__":
    main()
