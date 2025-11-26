import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import re
import random
import logging
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_salary(text: str) -> str:
    if not text:
        return ""
    pattern = r"\$[\d,]+(?:\.\d+)?\s*(K|k|M|m)?\s*(?:-\s*\$[\d,]+(?:\.\d+)?\s*(K|k|M|m)?)?(?:/(year|yr|hour|hr))?"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""

def extract_skills(text: str):
    if not text:
        return []
    text = text.lower()
    skills = {
        "python", "sql", "aws", "azure", "gcp", "docker", "kubernetes", "tensorflow", "pytorch",
        "pandas", "numpy", "spark", "hadoop", "tableau", "power bi", "excel", "machine learning",
        "deep learning", "nlp", "llm", "scikit-learn", "git", "airflow", "kafka", "react", "javascript",
        "typescript", "node.js", "java", "scala", "r", "statistics", "data visualization", "django", "flask",
        "fastapi", "html", "css", "tailwind", "bootstrap", "sass", "less", "redux", "graphql", "rest api"
    }
    found = {s for s in skills if s in text}
    return [s.title() for s in sorted(found)]

async def human_like_scroll(page, times=4):
    for _ in range(times):
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight / 4)")
        await asyncio.sleep(random.uniform(1.2, 2.5))

async def scrape_job_detail(browser, job_url):
    if not job_url or "linkedin.com" not in job_url:
        return "", "", []

    try:
        page = await browser.new_page()
        await page.goto(job_url, wait_until="networkidle", timeout=35000)

        try:
            btn = await page.query_selector("button.show-more-less-html__button--more")
            if btn and await btn.is_visible():
                await btn.click()
                await asyncio.sleep(2)
        except:
            pass

        await human_like_scroll(page, times=3)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        desc = soup.select_one("div.show-more-less-html__markup, div.jobs-description__content")
        if desc:
            for bad in desc.select("button, script, style"):
                bad.decompose()
            text = desc.get_text(separator=" ", strip=True)
            salary = extract_salary(text)
            skills = extract_skills(text)
            await page.close()
            return text, salary, skills

        await page.close()
    except Exception as e:
        logger.warning(f"Detail failed: {e}")

    return "", "", []

async def _scrape_linkedin_async(role: str, location: str = "", max_jobs: int = 10):
    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")

            search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote(role)}&location={quote(location or 'Worldwide')}&f_TPR=r604800"
            logger.info(f"LinkedIn URL: {search_url}")
            
            await page.goto(search_url, wait_until="networkidle")
            await asyncio.sleep(4)
            await human_like_scroll(page, times=4)

            cards = await page.query_selector_all("ul.jobs-search__results-list > li")
            logger.info(f"Found {len(cards)} LinkedIn cards")

            jobs_data = []
            for card in cards[:max_jobs]:
                try:
                    title_elem = await card.query_selector("h3")
                    company_elem = await card.query_selector("h4")
                    loc_elem = await card.query_selector("span.job-search-card__location")
                    link_elem = await card.query_selector("a.base-card__full-link")
                    
                    if not (title_elem and company_elem and link_elem):
                        continue

                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text()
                    location_text = await loc_elem.inner_text() if loc_elem else location
                    link = await link_elem.get_attribute("href")
                    link = urljoin("https://www.linkedin.com", link.split("?")[0])

                    jobs_data.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location_text.strip(),
                        "url": link,
                        "source": "LinkedIn",
                        "description": "",
                        "salary": "",
                        "skills_extracted": [],
                        "match_score": 0
                    })
                except Exception as e:
                    continue

            for job in jobs_data[:5]:
                desc, salary, skills = await scrape_job_detail(browser, job["url"])
                job["description"] = desc
                job["salary"] = salary
                job["skills_extracted"] = skills

            await browser.close()
            results = jobs_data
    except Exception as e:
        logger.error(f"LinkedIn Scraper Failed: {e}")
    
    return results

async def _scrape_remoteok_async(role: str, max_jobs: int = 10):
    results = []
    try:
        url = "https://remoteok.com/api"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    filtered = [j for j in data if isinstance(j, dict) and role.lower() in j.get('position', '').lower()]
                    
                    for item in filtered[:max_jobs]:
                        desc = item.get('description', '')
                        soup = BeautifulSoup(desc, "html.parser")
                        clean_desc = soup.get_text(separator=" ", strip=True)
                        
                        results.append({
                            "title": item.get('position'),
                            "company": item.get('company'),
                            "location": item.get('location', 'Remote'),
                            "url": item.get('url'),
                            "source": "RemoteOK",
                            "description": clean_desc[:500] + "...",
                            "salary": extract_salary(clean_desc),
                            "skills_extracted": item.get('tags', []) + extract_skills(clean_desc),
                            "match_score": 0
                        })
    except Exception as e:
        logger.error(f"RemoteOK Scraper Failed: {e}")
    
    return results

def scrape_jobs(role: str, location: str = "", max_jobs: int = 20):
    logger.info(f"Scraping: {role} | {location}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    tasks = [
        _scrape_linkedin_async(role, location, max_jobs),
        _scrape_remoteok_async(role, max_jobs)
    ]
    
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    
    all_jobs = []
    for res in results:
        all_jobs.extend(res)
        
    seen = set()
    unique = []
    for j in all_jobs:
        key = (j['title'], j['company'])
        if key not in seen:
            seen.add(key)
            unique.append(j)
    
    logger.info(f"Total unique jobs: {len(unique)}")
    return unique