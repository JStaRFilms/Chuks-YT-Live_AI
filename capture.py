from playwright.sync_api import sync_playwright

def main():
    print("Capturing overlay screenshots...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a small viewport typical for an avatar overlay region in OBS
        page = browser.new_page(viewport={"width": 400, "height": 400})
        page.goto('http://localhost:8000/overlay/index.html')
        page.wait_for_timeout(1000)
        
        # Idle screenshot (omit_background=True gives transparent background)
        page.screenshot(path='overlay_idle.png', omit_background=True)
        print("Captured overlay_idle.png")
        
        # Force Thinking state
        page.evaluate("document.getElementById('avatar').className = 'thinking'")
        page.wait_for_timeout(500)
        page.screenshot(path='overlay_thinking.png', omit_background=True)
        print("Captured overlay_thinking.png")

        # Force Talking state
        page.evaluate("document.getElementById('avatar').className = 'talking'")
        page.wait_for_timeout(500)
        page.screenshot(path='overlay_talking.png', omit_background=True)
        print("Captured overlay_talking.png")
        
        browser.close()
    print("Done catching screenshots.")

if __name__ == "__main__":
    main()
