import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# settings for webdriver
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(chrome_options=options, service=Service(ChromeDriverManager().install()))

# sets the target website to test
driver.get("http://127.0.0.1:8000/")

# maximizes the window
driver.maximize_window()


# finds element for find room button and clicks it
elem = driver.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/a[2]")
elem.click()

# tells selenium to wait/sleep for specified amount of seconds
time.sleep(2)

# tests the timerange
timeRange = driver.find_element(By.XPATH, "//*[@id='timeStart']")
timeRange.send_keys("0200PM")
timeRange.send_keys(Keys.TAB)
timeRange = driver.find_element(By.XPATH, "//*[@id='timeEnd']")
timeRange.send_keys("0315PM")
timeRange = driver.find_element(By.XPATH, "//*[@id='apply']")
timeRange.click()

time.sleep(2)

# tests the navigation to add courses tab
searchCourse = driver.find_element(By.XPATH, "//*[@id='navbarToggle']/div[1]/a[2]")
searchCourse.click()

# tests courses search bar
searchCourse = driver.find_element(By.XPATH, "//*[@id='q']")
searchCourse.send_keys("MATH")
searchCourse.send_keys(Keys.ENTER)

time.sleep(2)

# tests show and hide sections feature
minimize = driver.find_element(By.XPATH, "//*[@id='hide-sections']")
minimize.click()

time.sleep(2)

minimize = driver.find_element(By.XPATH, "//*[@id='show-sections']")
minimize.click()

time.sleep(2)

# quits the selenium browser
driver.quit()


