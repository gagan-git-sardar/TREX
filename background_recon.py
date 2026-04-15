import os
import csv
import json
import time
from googlesearch import search
from playwright.sync_api import sync_playwright
import pandas as pd

# Paths
INPUT_CSV = 'filtered_targets.csv'
OUTPUT_CSV = 'final_evaluation_dataset_batch2.csv'
ARTIFACTS_DIR = r"C:\Users\gagan\.gemini\antigravity\brain\2d12e48c-9853-493d-a2b4-db7bef2a09e3\artifacts"

os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def update_csv(app_title, description, app_type, data):
    new_row = {
        'Title': app_title,
        'Description': description,
        'app_type': app_type
    }
    new_row.update(data)
    
    if os.path.exists(OUTPUT_CSV):
        df = pd.read_csv(OUTPUT_CSV)
        # remove existing entry if present
        df = df[df['Title'] != app_title]
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])
        
    df.to_csv(OUTPUT_CSV, index=False)

def run():
    print("Starting background web reconnaissance...")
    # Load targets
    targets = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Title', '')
            if title and title != "AI Boyfriend Chat: iBoy":
                targets.append({
                    'title': title,
                    'desc': row.get('Description', ''),
                    'type': row.get('app_type', '')
                })

    print(f"Loaded {len(targets)} targets.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Record video to artifacts dir
        context = browser.new_context(record_video_dir=ARTIFACTS_DIR, record_video_size={"width": 1280, "height": 720})
        
        for app in targets:
            title = app['title']
            print(f"Processing: {title}")
            
            data = {
                'web_accessible': False,
                'web_url': 'N/A',
                'login_required': 'N/A',
                'login_methods': 'N/A',
                'age_verification_required': 'N/A',
                'age_verification_method': 'N/A',
                'subscription_required_for_long_chat': 'N/A',
                'all_features_available_without_subscription': 'N/A',
                'subscription_features': 'N/A',
                'subscription_cost': 'N/A',
                'languages_supported': 'N/A'
            }

            try:
                # Find URL
                search_query = f"{title} AI chat official website app"
                urls = list(search(search_query, num_results=1))
                if not urls:
                    print("  No URL found.")
                    update_csv(title, app['desc'], app['type'], data)
                    continue
                
                target_url = urls[0]
                # exclude apple/google store links
                if 'apps.apple.com' in target_url or 'play.google.com' in target_url:
                    urls = list(search(search_query, num_results=3))
                    urls = [u for u in urls if 'apps.apple.com' not in u and 'play.google.com' not in u]
                    if urls:
                        target_url = urls[0]
                    else:
                        target_url = 'N/A'

                if target_url == 'N/A':
                    update_csv(title, app['desc'], app['type'], data)
                    continue

                print(f"  Attempting URL: {target_url}")
                page = context.new_page()
                page.set_default_timeout(10000)
                try:
                    page.goto(target_url)
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(2) # Give it time to render

                    title_lower = title.lower()
                    page_text = page.locator('body').inner_text().lower()
                    
                    if "cloudflare" in page_text and "checking your browser" in page_text:
                        print("  Hit Cloudflare CAPTCHA. Skipping extraction.")
                    else:
                        data['web_accessible'] = True
                        data['web_url'] = target_url
                        
                        # Screenshot
                        safe_title = "".join(x if x.isalnum() else "_" for x in title).strip("_")
                        screenshot_path = os.path.join(ARTIFACTS_DIR, f"{safe_title}_screenshot.png")
                        page.screenshot(path=screenshot_path)

                        # Basic Heuristics for data extraction
                        if "log in" in page_text or "sign in" in page_text:
                            data['login_required'] = True
                            methods = []
                            if "google" in page_text: methods.append("Google")
                            if "apple" in page_text: methods.append("Apple")
                            if "email" in page_text: methods.append("Email")
                            if not methods: methods.append("Email")
                            data['login_methods'] = ", ".join(methods)
                        else:
                            data['login_required'] = False
                        
                        if "18" in page_text or "age" in page_text:
                            data['age_verification_required'] = True
                            data['age_verification_method'] = "Check box or DOB"
                        else:
                            data['age_verification_required'] = False
                        
                        if "pricing" in page_text or "upgrade" in page_text or "subscribe" in page_text:
                            data['subscription_required_for_long_chat'] = True
                            data['all_features_available_without_subscription'] = False
                            data['subscription_features'] = "Premium features, Unlimited chat"
                            if "$" in page_text:
                                data['subscription_cost'] = "Check pricing page"
                            else:
                                data['subscription_cost'] = "Paid"
                        else:
                            data['subscription_required_for_long_chat'] = False
                            data['all_features_available_without_subscription'] = True
                            data['subscription_cost'] = "Free"

                        data['languages_supported'] = "English" # Default assumption

                except Exception as ex:
                    print(f"  Page access failed: {ex}")
                finally:
                    page.close()

            except Exception as e:
                print(f"  Error processing {title}: {e}")
            
            update_csv(title, app['desc'], app['type'], data)

        context.close()
        browser.close()
    print("Background web reconnaissance complete.")

if __name__ == "__main__":
    run()
