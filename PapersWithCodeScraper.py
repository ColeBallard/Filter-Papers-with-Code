import os
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

sys.stderr = open(os.devnull, 'w')

class PapersWithCodeScraper:
    def __init__(self, driver_path, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        # Set Chrome to only show fatal errors.
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        # Exclude extra logging switches.
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        # Redirect service logs to NUL (Windows) or /dev/null (Linux/Mac)
        service = Service(driver_path, service_log_path="NUL")
        self.driver = webdriver.Chrome(service=service, options=options)
        print("Initialized Chrome WebDriver.")

    def _parse_date(self, date_str):
        """
        Parses a date string into a datetime object.
        Expected format based on sample: "03 Feb 2025" -> "%d %b %Y"
        """
        try:
            parsed_date = datetime.strptime(date_str.strip(), "%d %b %Y")
            return parsed_date
        except Exception as e:
            print(f"Failed to parse date '{date_str}': {e}")
            return None

    def get_latest_links(self, start_date: datetime, top_n: int = 10, pause_time=2, max_scrolls=50):
        """
        Retrieves the top_n papers (sorted by stars) with a publication date less than or equal to start_date.
        Returns a 2D list where each row is: [stars, paper title, link].
        
        The function scrolls until one of these conditions is met:
         - No new content is loaded,
         - A paper with a date older than or equal to start_date is found,
         - Or max_scrolls is reached.
        """
        print("Navigating to https://paperswithcode.com/latest")
        self.driver.get("https://paperswithcode.com/latest")
        
        scrolls = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        print(f"Initial scroll height: {last_height}")
        
        while scrolls < max_scrolls:
            print(f"Scroll attempt {scrolls + 1}")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            print(f"New scroll height after attempt {scrolls + 1}: {new_height}")
            
            if new_height == last_height:
                print("No change in scroll height; stopping scroll.")
                break
            
            last_height = new_height
            scrolls += 1

            # Check if any loaded paper has a date that is older than or equal to start_date.
            paper_elements = self.driver.find_elements(By.CSS_SELECTOR, ".infinite-item")
            print(f"After scroll {scrolls}, found {len(paper_elements)} paper elements.")
            
            paper_dates = []
            for paper in paper_elements:
                try:
                    # Updated selector for date.
                    date_elements = paper.find_elements(By.CSS_SELECTOR, ".stars-accumulated.text-center")
                    if date_elements:
                        date_text = date_elements[0].text.strip()
                        paper_date = self._parse_date(date_text)
                        if paper_date:
                            paper_dates.append(paper_date)
                    else:
                        print("Warning: Paper date element not found for one paper; skipping date check for it.")
                except Exception as e:
                    print(f"Error extracting date from a paper element: {e}")
            
            if paper_dates:
                oldest_date = min(paper_dates)
                print(f"Oldest paper date found: {oldest_date}")
                if oldest_date <= start_date:
                    print("Found a paper older than or equal to start_date; stopping scroll.")
                    break
            else:
                print("No paper dates found in this batch.")
        
        print("Finished scrolling. Now processing papers.")
        
        # Collect paper elements once more after scrolling.
        paper_elements = self.driver.find_elements(By.CSS_SELECTOR, ".infinite-item")
        print(f"Total paper elements collected: {len(paper_elements)}")
        
        papers = []
        for idx, paper in enumerate(paper_elements, start=1):
            print(f"Processing paper element {idx}/{len(paper_elements)}")
            try:
                # Extract title and link using the new structure.
                # Target the <a> inside the <h1> within the container.
                title_element = paper.find_element(By.CSS_SELECTOR, "div.col-lg-9.item-content h1 a")
                paper_title = title_element.text.strip()
                paper_link = title_element.get_attribute("href")

                # Extract star count using the new structure.
                # Look for the <span> inside the div with class "entity-stars".
                stars_element = paper.find_element(By.CSS_SELECTOR, "div.entity-stars span.badge.badge-secondary")
                stars_text = stars_element.text.strip()
                try:
                    # The text might include non-numeric characters (from the icon), so extract digits.
                    stars_number = stars_text.split()[-1].replace(',', '')  # Get the last token, which should be the number.
                    stars = int(stars_number)
                except Exception as e:
                    print(f"Error converting stars '{stars_text}' to int: {e}")
                    stars = 0

                # Extract publication date.
                date_elements = paper.find_elements(By.CSS_SELECTOR, ".stars-accumulated.text-center")
                if date_elements:
                    date_text = date_elements[0].text.strip()
                    paper_date = self._parse_date(date_text)
                else:
                    print("Warning: Paper date element not found; skipping this paper.")
                    continue

                papers.append({
                    "stars": stars,
                    "title": paper_title,
                    "date": paper_date,
                    "link": paper_link
                })

            except Exception as e:
                print(f"Error processing paper element {idx}: {e}")
                continue
        
        print(f"Collected {len(papers)} papers after filtering by date.")
        
        # Sort by stars (descending) and take the top_n.
        sorted_papers = sorted(papers, key=lambda x: x["stars"], reverse=True)
        top_papers = sorted_papers[:top_n]
        print(f"Returning top {len(top_papers)} papers.")
        
        # Convert to a 2D list.
        result = [[paper["stars"], paper["title"], paper["link"]] for paper in top_papers]
        return result

    def close(self):
        print("Closing the WebDriver.")
        self.driver.quit()
