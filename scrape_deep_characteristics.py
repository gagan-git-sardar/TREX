import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re

sem = asyncio.Semaphore(10) # process 10 at a time

async def fetch_page(context, url):
    async with sem:
        page = await context.new_page()
        text = ""
        try:
            # We don't need a heavy load, just domcontentloaded
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)
            # Some pages load text in body, but let's grab what we can
            text = await page.locator("body").inner_text()
        except Exception as e:
            pass # ignore timeouts and just return empty text to proceed quickly
        finally:
            await page.close()
        return text, url

def extract_features(text, url):
    text_lower = text.lower()
    
    login_required = False
    if any(k in text_lower for k in ["log in", "sign in", "account", "register", "sign up"]):
        login_required = True
        
    methods = []
    if "google" in text_lower: methods.append("Google")
    if "apple" in text_lower: methods.append("Apple")
    if "email" in text_lower: methods.append("Email")
    if "facebook" in text_lower: methods.append("Facebook")
    if not methods and login_required: methods.append("Email")
    login_methods = ", ".join(methods) if methods else "None"
    
    age_req = False
    if any(k in text_lower for k in ["18+", "17+", "requires 18", "adult", "age verification", "12+"]):
        age_req = True
        
    sub_required = False
    all_free = True
    sub_features = "None"
    sub_cost = []
    
    if any(k in text_lower for k in ["premium", "subscribe", "subscription", "in-app purchases", "upgrade"]):
        sub_required = True
        all_free = False
        sub_features = "Premium features, subscriptions, or IAPs"
        
    if "in-app purchases" in text_lower: sub_cost.append("In-App Purchases")
    if "premium" in text_lower: sub_cost.append("Premium")
        
    prices = re.findall(r'\$\d+\.\d+(?:/mo|/month|/week|/year| per)?', text_lower)
    if not prices:
        prices = re.findall(r'\$\d+\.\d+', text_lower)
        
    if prices:
        # Avoid putting the same price multiple times
        for p in prices:
            if p not in sub_cost:
                sub_cost.append(p)
                
    # limit sub_cost string length if many prices are found
    if len(sub_cost) > 5:
        sub_cost = sub_cost[:5] + ["..."]
        
    final_cost = ", ".join(sub_cost) if sub_cost else "Free"
    
    return {
        "login_required": login_required,
        "login_methods": login_methods,
        "age_verification_required": age_req,
        "subscription_required_for_long_chat": sub_required,
        "all_features_available_without_subscription": all_free,
        "subscription_features": sub_features,
        "subscription_cost": final_cost
    }

async def process_all(df):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Gather all tasks
        tasks = [fetch_page(context, url) for url in df['web_url']]
        total = len(tasks)
        print(f"Total tasks: {total}")
        
        # We can run gather on all tasks since Semaphore protects them
        chunk_size = 50
        for i in range(0, total, chunk_size):
            chunk = tasks[i:i+chunk_size]
            chunk_results = await asyncio.gather(*chunk)
            results.extend(chunk_results)
            print(f"Processed {min(i+chunk_size, total)}/{total}")
            
        await browser.close()
    return results

def main():
    df = pd.read_csv("final_app_evaluation_dataset.csv")
    
    # Optional: we can use original descriptions alongside page text to be safe
    # But instruction says "Scan the page text" so we prioritize page text
    
    loop = asyncio.get_event_loop()
    raw_results = loop.run_until_complete(process_all(df))
    
    # raw_results is list of (text, url) in same order as df
    features_list = []
    for (text, url), orig_desc in zip(raw_results, df['Description']):
        # Combine scraped text and the description we already have to ensure we don't miss anything if scrape fails
        combined_text = text + " " + (orig_desc if orig_desc and isinstance(orig_desc, str) else "")
        features = extract_features(combined_text, url)
        features_list.append(features)
        
    features_df = pd.DataFrame(features_list)
    
    df['login_required'] = features_df['login_required']
    df['login_methods'] = features_df['login_methods']
    df['age_verification_required'] = features_df['age_verification_required']
    df['subscription_required_for_long_chat'] = features_df['subscription_required_for_long_chat']
    df['all_features_available_without_subscription'] = features_df['all_features_available_without_subscription']
    df['subscription_features'] = features_df['subscription_features']
    df['subscription_cost'] = features_df['subscription_cost']
    
    df.to_csv("final_app_evaluation_dataset.csv", index=False)
    print("Dataset Rebuilt.")

if __name__ == "__main__":
    main()
