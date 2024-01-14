import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Ref: https://selenium-python.readthedocs.io/locating-elements.html

AMAZON_URL = "https://www.amazon.com/gp/goldbox"
WAIT_TIMEOUT = 3  # 3 seconds

# Allow a pop-up window to be in cognito mode
chrome_options = Options()
chrome_options.add_argument("--incognito")  # incognito mode
driver = webdriver.Chrome(options=chrome_options)

# Specify the URL to get the data from
driver.get(AMAZON_URL)

# Scroll down to load all products
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

# Wait for a while to be fully loaded
time.sleep(WAIT_TIMEOUT)
# Let's see what we have

products = []

for idx in range(3):  # load first 4 pages
    logger.info(f"Current URL: {driver.current_url}")
    # Scrape the current page by BeautifulSoup
    page = BeautifulSoup(driver.page_source, features="html.parser")

    # Find the deals container containing all the deals available
    deals_container = page.find_all(
        "div", {"data-testid": "grid-deals-container"}
    )
    deals_container = deals_container[0]

    # Extract all deals from the container using the <img> tag
    deals = deals_container.find_all("img")
    logger.info(f"Num of deals from page {idx+1}: {len(deals)}")

    for deal in deals:
        product_name = deal["alt"]
        img_url = deal["src"]
        products.append({"product_name": product_name, "img_url": img_url})

    next_button = driver.find_element("xpath", '//*[@class="a-last"]')
    next_button.click()
    # Wait for a while to be fully loaded
    time.sleep(WAIT_TIMEOUT)
    # Scroll down to load all products
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

# Convert the list of products to dataframe
df = pd.DataFrame.from_dict(products)

# Write the new products to a products.csv file
dest = os.path.join("data", "products.csv")
if os.path.exists(dest):
    # If this file already exists, append
    df.to_csv(dest, mode="a", index=False, header=False)
else:
    # Else, create it
    df.to_csv(dest, mode="w", index=False, header=False)
