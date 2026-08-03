import os, json, time, requests

AGNES_API_KEY = os.environ['AGNES_API_KEY']
BASE_URL = 'https://apihub.agnes-ai.com/v1'

UID = os.environ.get('UID', 'unknown')
IMAGEN_URL = os.environ.get('IMAGEN_URL')
AUDIO_URL = os.environ.get('AUDIO_URL')
DURACION = int(os.environ.get('DURACION', 8))
FILA_NUM = os.environ.get('FILA_NUM', '0')

PROMPTS = {
    'tiktok': 'Estilo TikTok viral. Movimiento rápido, energía alta, colores vibrantes. Vertical 9:16.',
    'youtube': 'Estilo YouTube Shorts. Profesional, limpio, con foco en el producto. Vertical 9:16.',
    'instagram': 'Estilo Instagram Reel. Estético, cuidando composición y colores. Vertical 9:16.',
    'facebook': 'Estilo Facebook video. Directo, conversacional, con enfoque en el beneficio. Vertical 9:16.'
}

def iniciar_video(prompt, plataforma):
    print(f'📤 Iniciando {plataforma}...')
    payload = {
        'model': 'agnes-video-v2.0',
        'image': IMAGEN_URL,
        'audio': AUDIO_URL,
        'height': 1080,
        'width': 608,
        'num_frames': DURACION * 24,
        'frame_rate': 24,
        'guidance_scale': 7.5,
        'num_inference_steps': 25,
        'prompt': prompt
    }
    r = requests.post(f'{BASE_URL}/videos', 
                      headers={'Authorization': f'Bearer {AGNES_API_KEY}'},
                      json=payload, timeout=30)
    if r.status_code in [200, 201]:
        return r.json().get('video_id') or r.json().get('id')
    return None

def esperar_video(video_id, plataforma):
    for _ in range(30):
        r = requests.get(f'{BASE_URL}/videos/{video_id}',
                         headers={'Authorization': f'Bearer {AGNES_API_KEY}'})
        data = r.json()
        status = data.get('status') or data.get('state') or 'pending'
        if status in ['succeeded', 'completed', 'done']:
            return data.get('url') or data.get('video_url') or data.get('data', [{}])[0].get('url')
        if status in ['failed', 'error']:
            raise Exception(f'Render falló: {data}')
        time.sleep(10)
    raise Exception('Timeout')

os.makedirs('./output', exist_ok=True)
resultados = {}
render_ids = {}

for plataforma, prompt in PROMPTS.items():
    vid = iniciar_video(prompt, plataforma)
    render_ids[plataforma] = vid
    time.sleep(5)

for plataforma, vid in render_ids.items():
    try:
        url = esperar_video(vid, plataforma)
        resultados[plataforma] = {'success': True, 'videoUrl': url}
        print(f'✅ {plataforma}: listo')
    except Exception as e:
        resultados[plataforma] = {'success': False, 'error': str(e)}
        print(f'❌ {plataforma}: {e}')

with open('./output/resultados.json', 'w') as f:
    json.dump({'uid': UID, 'filaNum': FILA_NUM, 'resultados': resultados}, f)
