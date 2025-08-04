import requests

try:
    ip = requests.get("https://api.ipify.org").text
    print("✅ IP Pubblico del Container Railway:", ip)
except Exception as e:
    print("❌ Errore nel recupero IP:", e)
