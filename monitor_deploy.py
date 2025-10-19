#!/usr/bin/env python3
"""
Script para monitorar o progresso do deploy do frontend em tempo real
"""
import requests
import json
import time
from datetime import datetime

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
SERVICE_ID = "srv-d3qd08ali9vc73c8a5f0"  # foto-video-fantasia
DEPLOY_ID = None  # Será obtido automaticamente

headers = {"Authorization": f"Bearer {API_KEY}"}

def get_deploy_status():
    """Obtém o status do deploy mais recente"""
    global DEPLOY_ID
    
    # Se não temos DEPLOY_ID, buscar o mais recente
    if not DEPLOY_ID:
        deploys_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys?limit=1"
        response = requests.get(deploys_url, headers=headers)
        if response.status_code == 200:
            deploys = response.json()
            if deploys and len(deploys) > 0:
                DEPLOY_ID = deploys[0].get("deploy", {}).get("id")
    
    if not DEPLOY_ID:
        return None
    
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{DEPLOY_ID}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def format_time(timestamp):
    """Formata timestamp para exibição"""
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except:
        return timestamp[:19]

def get_status_emoji(status):
    """Retorna emoji baseado no status"""
    status_map = {
        "build_in_progress": "🔄",
        "live": "✅",
        "build_failed": "❌",
        "canceled": "⚠️",
        "deactivated": "⏸️",
        "upload_failed": "❌",
        "pre_deploy_in_progress": "⏳",
        "update_in_progress": "🔄"
    }
    return status_map.get(status, "❓")

def main():
    print("=" * 70)
    print("🎯 MONITOR DE DEPLOY - FOTO-VIDEO-FANTASIA (FRONTEND)")
    print("=" * 70)
    print(f"\n📝 Service ID: {SERVICE_ID}")
    if DEPLOY_ID:
        print(f"🚀 Deploy ID: {DEPLOY_ID}")
    else:
        print(f"🚀 Deploy ID: Buscando o mais recente...")
    print(f"🔗 Dashboard: https://dashboard.render.com/static/{SERVICE_ID}")
    print("\n" + "=" * 70)
    print("⏳ Monitorando deploy... (Pressione Ctrl+C para sair)\n")
    
    previous_status = None
    check_count = 0
    start_time = time.time()
    
    try:
        while True:
            check_count += 1
            elapsed = int(time.time() - start_time)
            
            deploy = get_deploy_status()
            
            if not deploy:
                print(f"❌ Erro ao obter status do deploy (tentativa {check_count})")
                time.sleep(10)
                continue
            
            status = deploy.get("status", "unknown")
            emoji = get_status_emoji(status)
            
            # Só imprime se o status mudou ou a cada 6 checks (1 minuto)
            if status != previous_status or check_count % 6 == 0:
                created_at = format_time(deploy.get("createdAt"))
                updated_at = format_time(deploy.get("updatedAt"))
                finished_at = format_time(deploy.get("finishedAt"))
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {emoji} Status: {status.upper().replace('_', ' ')}")
                print(f"   ⏱️  Tempo decorrido: {elapsed // 60}m {elapsed % 60}s")
                print(f"   📅 Criado: {created_at}")
                print(f"   🔄 Atualizado: {updated_at}")
                
                if finished_at != "N/A":
                    print(f"   ✅ Finalizado: {finished_at}")
                
                print()
                
                # Se mudou de status, mostra destaque
                if status != previous_status and previous_status is not None:
                    print(f"   🔔 Status mudou: {previous_status} → {status}")
                    print()
                
                previous_status = status
            
            # Verifica se finalizou
            if status == "live":
                print("=" * 70)
                print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
                print("=" * 70)
                print(f"\n✅ Frontend está ONLINE!")
                print(f"🌐 URL: https://talking-photo-frontend.onrender.com")
                print(f"⏱️  Tempo total: {elapsed // 60}m {elapsed % 60}s")
                print(f"🔗 Dashboard: https://dashboard.render.com/static/{SERVICE_ID}")
                print("\n💡 Teste o frontend agora!")
                print("=" * 70)
                break
            
            elif status == "build_failed":
                print("=" * 70)
                print("❌ BUILD FALHOU!")
                print("=" * 70)
                print(f"\n🔗 Veja os logs: https://dashboard.render.com/static/{SERVICE_ID}")
                print("\n💡 Possíveis causas:")
                print("   1. Build Command incorreto")
                print("   2. Publish Directory incorreto (deve ser 'build')")
                print("   3. Erro nas dependências npm")
                print("   4. Falta variável de ambiente REACT_APP_API_URL")
                print("\n🔧 Configure corretamente no Dashboard e tente novamente")
                print("=" * 70)
                break
            
            elif status in ["canceled", "upload_failed"]:
                print("=" * 70)
                print(f"⚠️  DEPLOY {status.upper().replace('_', ' ')}")
                print("=" * 70)
                print(f"\n🔗 Veja detalhes: https://dashboard.render.com/static/{SERVICE_ID}")
                print("=" * 70)
                break
            
            # Aguarda 10 segundos antes de verificar novamente
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoramento interrompido pelo usuário")
        print(f"⏱️  Tempo decorrido: {elapsed // 60}m {elapsed % 60}s")
        print(f"📊 Último status: {previous_status or 'N/A'}")
        print(f"🔗 Continue acompanhando: https://dashboard.render.com/static/{SERVICE_ID}")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()
