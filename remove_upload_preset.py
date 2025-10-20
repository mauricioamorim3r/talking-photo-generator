import requests

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
SERVICE_ID = "srv-d3q80d0gjchc73b48p40"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("=" * 70)
print("🗑️  REMOVENDO CLOUDINARY_UPLOAD_PRESET")
print("=" * 70)

# Deletar a variável CLOUDINARY_UPLOAD_PRESET
response = requests.delete(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars/CLOUDINARY_UPLOAD_PRESET",
    headers=headers
)

if response.status_code == 204:
    print("\n✅ CLOUDINARY_UPLOAD_PRESET removido com sucesso!")
    print("\n📝 Agora o Cloudinary vai usar:")
    print("   • CLOUDINARY_CLOUD_NAME")
    print("   • CLOUDINARY_API_KEY")
    print("   • CLOUDINARY_API_SECRET")
    print("\n⚠️  O backend será reiniciado automaticamente")
    print("   Aguarde ~2 minutos antes de testar")
else:
    print(f"\n❌ Erro ao remover: {response.status_code}")
    print(f"   {response.text}")

print("=" * 70)
