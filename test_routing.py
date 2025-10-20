"""Test SPA routing after _redirects fix"""
import requests

BASE_URL = "https://foto-video-fantasias.onrender.com"  # NEW Web Service from dashboard

routes = [
    "/",
    "/gallery",
    "/image-generator",
    "/admin"
]

print("🧪 Testando rotas do frontend...\n")

for route in routes:
    url = f"{BASE_URL}{route}"
    try:
        response = requests.get(url, timeout=10)
        status = "✅" if response.status_code == 200 else "❌"
        
        # Check if it returned HTML (not 404 page)
        is_html = "<!DOCTYPE html>" in response.text or "<html" in response.text
        has_root_div = 'id="root"' in response.text
        
        print(f"{status} {route}")
        print(f"   Status: {response.status_code}")
        print(f"   HTML: {is_html}")
        print(f"   React Root: {has_root_div}")
        
        if response.status_code != 200:
            print(f"   ⚠️  Error: Not Found")
        elif not has_root_div:
            print(f"   ⚠️  Warning: React root div not found")
        
        print()
        
    except Exception as e:
        print(f"❌ {route}")
        print(f"   Error: {e}\n")

print("\n📋 Resumo:")
print("Se todas as rotas retornarem 200 e tiverem React root div, o SPA routing está funcionando!")
