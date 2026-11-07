from selenium import webdriver

from support import config


def make_driver(browser: str | None = None, headless: bool | None = None) -> webdriver.Remote:
    browser = (browser or config.BROWSER).lower()
    headless = config.HEADLESS if headless is None else headless
    w, h = config.WINDOW_SIZE

    if browser == "chrome":
        opts = webdriver.ChromeOptions()
        factory = webdriver.Chrome
    elif browser == "edge":
        opts = webdriver.EdgeOptions()
        factory = webdriver.Edge
    elif browser == "firefox":
        opts = webdriver.FirefoxOptions()
        factory = webdriver.Firefox
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    if headless:
        opts.add_argument("--headless=new" if browser != "firefox" else "-headless")
    if browser != "firefox":
        opts.add_argument(f"--window-size={w},{h}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--lang=en-US")
        opts.add_experimental_option("prefs", {"intl.accept_languages": "en-US"})

    driver = factory(options=opts)
    if browser == "firefox":
        driver.set_window_size(w, h)
    return driver
