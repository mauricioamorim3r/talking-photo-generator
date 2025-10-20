import requests
import os

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
for var in env_vars:
    if 'CLOUDINARY' in var['envVar']['key']:
        cloudinary_vars.append(var['envVar']['id'])
        print(f"  - {var['envVar']['key']}: {var['envVar']['id']}")

# Delete each Cloudinary variable
if cloudinary_vars:
    print(f"\n🗑️ Deleting {len(cloudinary_vars)} Cloudinary variables...")
    for var_id in cloudinary_vars:
        delete_url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars/{var_id}'
        response = requests.delete(delete_url, headers=headers)
        if response.status_code == 204:
            print(f"  ✅ Deleted variable {var_id}")
        else:
            print(f"  ❌ Failed to delete {var_id}: {response.status_code}")
    print("\n✅ All Cloudinary variables removed!")
else:
    print("\n✅ No Cloudinary variables found")
