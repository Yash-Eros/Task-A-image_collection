import json
from playwright.async_api import async_playwright


class PlaywrightScraper:
    def __init__(self):
        self.name = "playwright"

    async def paginate(self, query, limit=20):
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
            await page.goto(url)

            # ✅ SCROLL to load dynamic content
            for _ in range(5):
                await page.mouse.wheel(0, 5000)
                await page.wait_for_timeout(1500)

            # ✅ SELECT CORRECT ELEMENTS (Bing image cards)
            elements = await page.query_selector_all("a.iusc")

            for el in elements:
                try:
                    meta = await el.get_attribute("m")

                    if not meta:
                        continue

                    data = json.loads(meta)
                    img_url = data.get("murl")

                    if not img_url:
                        continue

                    results.append({
                        "id": img_url,
                        "url": img_url,
                        "source": "playwright"
                    })

                    if len(results) >= limit:
                        break

                except Exception:
                    continue

            await browser.close()
       # print(len(results))
        return results