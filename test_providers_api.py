"""Test the providers endpoint"""
import requests
import json

try:
    response = requests.get("http://localhost:8001/api/video/providers")
    data = response.json()
    
    print("\n" + "="*80)
    print("🎬 VIDEO PROVIDERS API TEST")
    print("="*80)
    
    print(f"\n✅ Success: {data.get('success')}")
    print(f"⭐ Default Provider: {data.get('default_provider')}")
    
    print("\n📋 Available Providers:")
    for provider in data.get('providers', []):
        recommended = " ⭐" if provider.get('recommended') else ""
        print(f"\n  • {provider['name']}{recommended}")
        print(f"    ID: {provider['id']}")
        print(f"    Provider: {provider['provider']}")
        print(f"    Cost: ${provider['cost_per_second']}/second")
        print(f"    With Audio: ${provider['cost_per_second_with_audio']}/second")
        print(f"    Available: {provider['available']}")
        if provider.get('savings_vs_fal'):
            print(f"    💰 Savings: {provider['savings_vs_fal']} vs FAL.AI")
        print(f"    Description: {provider['description']}")
    
    if 'recommendation' in data:
        rec = data['recommendation']
        print("\n" + "="*80)
        print("💡 RECOMMENDATION:")
        print(f"   Provider: {rec['provider']}")
        print(f"   Reason: {rec['reason']}")
        print(f"   Savings: {rec['savings']}")
        print("="*80)
    
    print("\n✅ API Test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
