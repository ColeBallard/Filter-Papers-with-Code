import yaml
from datetime import datetime

from PapersWithCodeScraper import PapersWithCodeScraper

# Load YAML configuration file
def load_config(config_path="config.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

if __name__ == '__main__':
    # Example usage
    config = load_config()

    # Adjust the driver_path as needed
    driver_path = config.get('ChromeDriverPath', '')
    scraper = PapersWithCodeScraper(driver_path=driver_path, headless=False)
    
    # Define date range (adjust the dates to match the website's date format)
    start_date = datetime(2025, 1, 4)
    
    # Scrape the top 5 papers with the most stars within the date range.
    top_papers = scraper.get_latest_links(start_date, top_n=25)
    for paper in top_papers:
        print(paper)
    
    # Close the scraper
    scraper.close()