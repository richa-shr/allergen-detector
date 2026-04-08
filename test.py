from scrapers.nykaa import scrape_nykaa

# Pick any real Nykaa skincare/beauty product URL
url = "https://www.nykaa.com/mamaearth-ubtan-face-wash-with-turmeric-saffron-for-tan-removal/p/7355638?ptype=product&utm_content=ads&utm_source=GooglePaid&utm_medium=PLA&utm_campaign=PerformanceMaxNCA_LowCAC_1Day&gad_source=1&gad_campaignid=23440573430&gbraid=0AAAABBsUhjRHQgau3Td70Q4R4hyS5G7qO&gclid=Cj0KCQjwmunNBhDbARIsAOndKpkBgtCF3xvk_ItgUuqtOGMVJ9vzFH2BtUWYJMI9zemu25ZfZa8GMeIaArUtEALw_wcB&skuId=6049664"

result = scrape_nykaa(url)

if result:
    print("\n--- INGREDIENTS FOUND ---")
    print(result)
else:
    print("No ingredients found")