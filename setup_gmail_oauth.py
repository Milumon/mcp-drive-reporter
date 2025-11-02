#!/usr/bin/env python3
"""
Helper para configurar OAuth2 de Gmail
Guía al usuario a través del proceso de autenticación OAuth2.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes necesarios para enviar correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def setup_oauth2():
    """
    Configura OAuth2 para Gmail.
    Genera el refresh_token necesario para el MCP.
    """
    print("\n" + "="*70)
    print("🔐 CONFIGURACIÓN DE OAUTH2 PARA GMAIL")
    print("="*70 + "\n")
    
    print("Pasos previos:")
    print("1. Ve a https://console.cloud.google.com/")
    print("2. Crea un proyecto (o selecciona uno existente)")
    print("3. Habilita la Gmail API")
    print("4. Ve a 'Credenciales' → 'Crear credenciales' → 'ID de cliente OAuth'")
    print("5. Tipo: 'Aplicación de escritorio'")
    print("6. Descarga el archivo JSON de credenciales")
    print("\n" + "="*70 + "\n")
    
    # Pedir ruta al archivo de credenciales
    creds_path = input("Ruta al archivo de credenciales JSON descargado: ").strip()
    
    if not os.path.exists(creds_path):
        print(f"❌ Error: Archivo no encontrado: {creds_path}")
        return
    
    try:
        # Leer credenciales
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        # Extraer client_id y client_secret
        if 'installed' in creds_data:
            client_id = creds_data['installed']['client_id']
            client_secret = creds_data['installed']['client_secret']
        elif 'web' in creds_data:
            client_id = creds_data['web']['client_id']
            client_secret = creds_data['web']['client_secret']
        else:
            print("❌ Error: Formato de credenciales no reconocido")
            return
        
        print(f"\n✅ Credenciales cargadas")
        print(f"Client ID: {client_id[:30]}...")
        
        # Iniciar flujo OAuth2
        print("\n🌐 Iniciando flujo de autenticación...")
        print("Se abrirá una ventana del navegador para autorizar la aplicación.\n")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_path,
            SCOPES
        )
        
        # Ejecutar flujo local
        creds = flow.run_local_server(port=0)
        
        # Obtener refresh token
        refresh_token = creds.refresh_token
        
        if not refresh_token:
            print("⚠️ Warning: No se obtuvo refresh_token. Puede que necesites revocar el acceso y volver a autorizar.")
            print("Revoca el acceso en: https://myaccount.google.com/permissions")
            return
        
        print("\n" + "="*70)
        print("✅ AUTENTICACIÓN EXITOSA")
        print("="*70 + "\n")
        
        print("Agrega estas variables a tu archivo .env:\n")
        print(f"GMAIL_CLIENT_ID={client_id}")
        print(f"GMAIL_CLIENT_SECRET={client_secret}")
        print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
        print()
        
        # Preguntar si quiere guardar en .env
        save = input("¿Quieres que las agregue automáticamente a .env? (s/n): ").strip().lower()
        
        if save == 's':
            env_path = '.env'
            
            # Leer .env existente
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Eliminar líneas existentes de Gmail OAuth
            env_lines = [
                line for line in env_lines 
                if not any(key in line for key in ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'])
            ]
            
            # Agregar nuevas credenciales
            env_lines.append(f"\n# Gmail OAuth2\n")
            env_lines.append(f"GMAIL_CLIENT_ID={client_id}\n")
            env_lines.append(f"GMAIL_CLIENT_SECRET={client_secret}\n")
            env_lines.append(f"GMAIL_REFRESH_TOKEN={refresh_token}\n")
            
            # Guardar
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
            
            print(f"\n✅ Credenciales guardadas en {env_path}")
        
        print("\n" + "="*70)
        print("🎉 Configuración completada. Ya puedes usar el MCP de Gmail.")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    setup_oauth2()

