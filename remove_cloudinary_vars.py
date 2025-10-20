import requests

API_KEY = 'rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S'
SERVICE_ID = 'srv-d3q80d0gjchc73b48p40'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Get current env vars
url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars'
response = requests.get(url, headers=headers)
env_vars = response.json()

print("🔍 Current environment variables:")
cloudinary_vars = []
other_vars = []
for var in env_vars:
    key = var['envVar']['key']
    if 'CLOUDINARY' in key:
        print(f"  ❌ Found Cloudinary var: {key}")
    else:
        other_vars.append({'key': key, 'value': var['envVar']['value']})
        print(f"  ✅ Keeping: {key}")

# Render API requires PUT with complete list (no DELETE endpoint)
print(f"\n🗑️ Updating environment variables (removing Cloudinary vars)...")
put_url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars'
response = requests.put(put_url, headers=headers, json=other_vars)
if response.status_code == 200:
    print(f"  ✅ Successfully updated environment variables")
    print(f"  ✅ Removed all Cloudinary variables")
    print(f"  ✅ Kept {len(other_vars)} other variables")
else:
    print(f"  ❌ Failed to update: {response.status_code}")
    print(f"  Response: {response.text}")
