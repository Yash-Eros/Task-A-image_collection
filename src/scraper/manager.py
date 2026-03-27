from src.sources.pexels import PexelsAPI
from src.sources.pixabay import PixabayAPI
from src.sources.unsplash import UnsplashAPI
from src.sources.smithsonian import SmithsonianAPI

# ✅ SCRAPING SOURCES
from src.sources.wikimedia import WikimediaAPI
from src.sources.rawpixel import RawpixelScraper
from src.sources.bing import BingCrawler
from src.sources.playwright_scraper import PlaywrightScraper
from src.sources.simple_scraper import SimpleScraper
from src.sources.nypl import NYPLAPI
from src.sources.crawl4ai_scraper import Crawl4AIScraper
from src.sources.europeana import EuropeanaAPI


class SourceManager:

    def __init__(self):
        self.sources = [

            # 🔥 PRIMARY (API) - Reliable and working
            PexelsAPI(),
            PixabayAPI(),
            UnsplashAPI(),

            # ⚠️ SCRAPING tools - Use as secondary sources
            BingCrawler(),  # ✅ Fixed to handle local files
            Crawl4AIScraper(),  # Additional web scraper
            WikimediaAPI(),
            RawpixelScraper(),  # Not reliable
            PlaywrightScraper(),
            SimpleScraper(),

            # ❌ Problematic/Incomplete
            #NYPLAPI(),  # Not returning results
            #EuropeanaAPI(),  # Invalid API key

            # 🔥 Fallback archive
            SmithsonianAPI(),
        ]

    def get_sources(self):
        return self.sources