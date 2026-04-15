import pandas as pd
import json

df = pd.read_csv('filtered_targets.csv')

with open('app_store_apps_details.json') as f:
    apple_data = {item.get('url'): item for item in json.load(f).get('results', []) if item.get('url')}

with open('google_play_apps_details.json') as f:
    google_data = {item.get('url'): item for item in json.load(f).get('results', []) if item.get('url')}
    
def get_web_url(url):
    if url in apple_data: return apple_data[url].get('url', url)
    if url in google_data: return google_data[url].get('url', url)
    return url

def get_subscription_cost(url):
    if url in apple_data:
        item = apple_data[url]
        price = item.get('price', 0)
        # Check if there is inAppPurchases or something similar for iOS
        if price == 0: price = 'Free'
        return str(price)
    if url in google_data:
        item = google_data[url]
        price = item.get('priceText', 'Free')
        iap = item.get('IAPRange')
        if iap:
            return f"{price} (IAP: {iap})"
        return str(price)
    return "Unknown"

def get_languages(url):
    if url in apple_data:
        langs = apple_data[url].get('languages', [])
        return ", ".join(langs) if isinstance(langs, list) else str(langs)
    if url in google_data:
        return "English" # typical fallback for Google Play if None
    return "Unknown"

df['web_url'] = df['URL/ID'].apply(get_web_url)
df['subscription_cost'] = df['URL/ID'].apply(get_subscription_cost)
df['languages_supported'] = df['URL/ID'].apply(get_languages)

df.to_csv('FINAL_PERFECT_DATASET.csv', index=False)
print("Done creating FINAL_PERFECT_DATASET.csv")
