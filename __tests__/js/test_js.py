import asyncio
from pyppeteer import launch

async def main():
    # Launch a headless Chromium browser
    browser = await launch()

    # Open a new page and navigate to the local Flask server
    page = await browser.newPage()
    await page.goto('http://localhost:5000/decelium_wallet1/__tests__/js/index.html')
    await page.waitForSelector('body')

    # Get the body of the root
    html = await page.content()
    text = await page.evaluate('document.body.textContent')

    # Assert some information about the body
    expected_text = 'Hello, world!'
    if expected_text in text:
        print(f'Body contains "{expected_text}"')
    else:
        print(f'Body does not contain "{expected_text}"')

    # Close the browser
    await browser.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())