from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.workana.com/es/jobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(8)

    # Capturar todo el texto visible
    body = page.inner_text("body")
    print("=== PRIMERAS 2000 CARACTERES DEL BODY ===")
    print(body[:2000])
    print()
    print("=== LINKS CON /job/ ===")
    links = page.query_selector_all("a[href*='/job/']")
    print(f"Count: {len(links)}")
    for l in links[:10]:
        print(f"  {l.get_attribute('href')}  |  {(l.inner_text() or '').strip()[:60]}")

    print()
    print("=== TODOS LOS LINKS (primeros 30 con texto) ===")
    all_links = page.query_selector_all("a[href]")
    count = 0
    for l in all_links:
        text = (l.inner_text() or "").strip()
        href = l.get_attribute("href") or ""
        if len(text) > 15 and "http" in href:
            print(f"  {href[:70]}  |  {text[:60]}")
            count += 1
            if count >= 30:
                break

    input("Presiona Enter para cerrar...")
    browser.close()
