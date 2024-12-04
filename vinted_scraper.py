# vinted_scraper.py

import tkinter as tk
from tkinter import messagebox
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_vinted(base_url, max_pages, output_file):
    # Setup the WebDriver
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    scraped_data = []  # List to store scraped data
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        
        # Update URL for the next page
        paginated_url = f"{base_url}&page={page}"
        driver.get(paginated_url)
        
        # Wait for grid items to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="grid-item"]'))
            )
            print(f"Grid items loaded for page {page}")
        except Exception as e:
            print(f"Error loading page {page}: {e}")
            break
        
        # Scrape items
        items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="grid-item"]')
        print(f"Found {len(items)} items on page {page}")
        
        # Extract data
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, '[data-testid*="description-title"]').text
                price = item.find_element(By.CSS_SELECTOR, '[data-testid*="price-text"]').text
                favourites = item.find_element(By.CSS_SELECTOR, '[data-testid*="favourite"] .web_ui__Text__caption').text
                
                # Find all links within the grid item
                links = item.find_elements(By.TAG_NAME, 'a')
                item_url = None
                
                # Filter to find the /items/ URL
                for link in links:
                    href = link.get_attribute("href")
                    if "/items/" in href:  # Ensure the link contains "/items/"
                        item_url = href
                        break
                
                # Append the data only if an item URL is found
                if item_url:
                    scraped_data.append({
                        "Title": title,
                        "Price": price,
                        "Favourites": favourites,
                        "Link": item_url
                    })
            except Exception as e:
                print(f"Error extracting item data: {e}")
        
        # Optional delay to avoid triggering anti-bot protections
        time.sleep(2)
    
    # Close the browser
    driver.quit()
    
    # Save the data to a CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Price", "Favourites", "Link"])
        writer.writeheader()
        writer.writerows(scraped_data)
    
    print(f"Data saved to {output_file}")
    return scraped_data

class VintedScraperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vinted Scraper")

        url_label = tk.Label(self.root, text="Base URL:")
        url_label.grid(row=0, column=0, padx=5, pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        pages_label = tk.Label(self.root, text="Max Pages:")
        pages_label.grid(row=1, column=0, padx=5, pady=5)
        self.pages_entry = tk.Entry(self.root, width=10)
        self.pages_entry.grid(row=1, column=1, padx=5, pady=5)

        file_label = tk.Label(self.root, text="Output File:")
        file_label.grid(row=2, column=0, padx=5, pady=5)
        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.grid(row=2, column=1, padx=5, pady=5)

        start_button = tk.Button(self.root, text="Start Scraping", command=self.start_scraping)
        start_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def start_scraping(self):
        base_url = self.url_entry.get()
        max_pages = int(self.pages_entry.get())
        output_file = self.file_entry.get()
        
        if not base_url or not output_file:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            scraped_data = scrape_vinted(base_url, max_pages, output_file)
            messagebox.showinfo("Success", "Data saved to file")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = VintedScraperGUI()
    gui.run()