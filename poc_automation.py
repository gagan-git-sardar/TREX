import asyncio
from playwright.async_api import async_playwright
import time

async def automate_chat():
    # List of 10 messages to send to fulfill the prompt's requirement
    messages = [
        "Hello! How are you doing today?",
        "I'm working on a research project right now.",
        "Can you tell me a bit about yourself?",
        "What is your favorite topic to talk about?",
        "Do you have any hobbies?",
        "That's interesting! Tell me more.",
        "How do you usually spend your day?",
        "If you could travel anywhere, where would you go?",
        "What kind of music do you like?",
        "Thanks for answering my questions. It's been fun!"
    ]

    print("Launching browser for AI Chat Automation...")
    # headless=False so you can record your screen for the demo!
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to AI companion web app (iBoy/Anima)...")
        target_url = "https://boyfriend.myanima.ai/app"
        await page.goto(target_url)
        
        await page.wait_for_load_state("networkidle")
        print("Page loaded. Waiting 5 seconds for any welcome popups...")
        time.sleep(5) 
        
        print("Starting automated messaging sequence...")
        
        for i, msg in enumerate(messages):
            print(f"[{i+1}/10] Sending: {msg}")
            
            # Locate standard chat input box
            chat_input = page.locator('textarea, input[type="text"]').first
            
            # Click and type the message
            await chat_input.click()
            await chat_input.fill(msg)
            
            # Hit Enter to send
            await page.keyboard.press("Enter")
            
            # Wait 6 seconds for the AI bot to generate its response
            time.sleep(6) 
            
        print("\nAll 10 messages sent successfully!")
        print("Leaving browser open for 10 seconds so you can capture the final screen...")
        time.sleep(10)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(automate_chat())