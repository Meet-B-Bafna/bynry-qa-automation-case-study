"""Small reusable gesture helpers for native-app mobile tests (Appium).
Kept separate from browserstack_driver.py so gesture logic can be unit-style
tested independent of session/capability setup."""


def swipe_up(driver, start_pct=0.8, end_pct=0.2, duration_ms=400):
    size = driver.get_window_size()
    width = size["width"]
    height = size["height"]
    driver.swipe(
        start_x=width // 2,
        start_y=int(height * start_pct),
        end_x=width // 2,
        end_y=int(height * end_pct),
        duration=duration_ms,
    )


def tap_by_accessibility_id(driver, accessibility_id: str):
    element = driver.find_element("accessibility id", accessibility_id)
    element.click()
