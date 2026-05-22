ANTI_DETECT_ARGS = [
    "--no-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--window-size=1280,800",
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

ANTI_DETECT_INIT_SCRIPT = (
    'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
)

VIEWPORT = {"width": 1280, "height": 800}
LOCALE = "en-US"


def create_browser_context(playwright_instance, headless=True, launch_kwargs=None, **context_kwargs):
    """Create a Playwright browser, context and page with anti-detection config.

    Args:
        playwright_instance: sync_playwright() context manager.
        headless: Run browser in headless mode.
        launch_kwargs: Extra args for browser.launch() (merged with ANTI_DETECT_ARGS).
        **context_kwargs: Extra kwargs for browser.new_context().

    Returns (browser, context, page) tuple.
    """
    launch = {"headless": headless, "args": ANTI_DETECT_ARGS}
    if launch_kwargs:
        launch.update(launch_kwargs)
    browser = playwright_instance.chromium.launch(**launch)

    kwargs = {"user_agent": UA, "viewport": VIEWPORT, "locale": LOCALE}
    kwargs.update(context_kwargs)
    context = browser.new_context(**kwargs)
    context.add_init_script(ANTI_DETECT_INIT_SCRIPT)
    page = context.new_page()
    return browser, context, page
