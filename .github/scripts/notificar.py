import os, json, requests

UID = os.environ.get('UID')
FILA_NUM = os.environ.get('FILA_NUM')
APPS_SCRIPT_URL = os.environ.get('APPS_SCRIPT_URL')

if APPS_SCRIPT_URL:
    with open('./output/resultados.json', 'r') as f:
        data = json.load(f)
    data['filaNum'] = FILA_NUM
    try:
        r = requests.post(APPS_SCRIPT_URL, json=data, timeout=30)
        print(f'✅ Notificación enviada: HTTP {r.status_code}')
    except Exception as e:
        print(f'❌ Error: {e}')
