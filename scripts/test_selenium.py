from selenium import webdriver
opts = webdriver.ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1280,900")
d = webdriver.Chrome(options=opts)
print("OK", d.capabilities["browserVersion"])
d.quit()
