import requests

def engine_workday(url, config_extra, termo_busca):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "pt-BR"
    }
    
    payload = {
        "appliedFacets": config_extra.get("appliedFacets", {}),
        "limit": 20,
        "offset": 0,
        "searchText": termo_busca
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            vagas_raw = response.json().get('jobPostings', [])
            vagas_filtradas = []
            
            for item in vagas_raw:
                path_relativo = item.get('externalPath')
                link_completo = f"{config_extra.get('base_url_vagas')}{path_relativo}"
                
                vagas_filtradas.append({
                    "titulo": item.get('title'),
                    "local": item.get('locationsText', 'Brasil'),
                    "link": link_completo
                })
            return vagas_filtradas
    except Exception as e:
        print(f"Erro na engine Workday: {e}")
    return []


def engine_greenhouse(url, config_extra, termo_busca):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            vagas_raw = response.json().get('jobs', [])
            vagas_filtradas = []
            
            termo = termo_busca.lower()
            for item in vagas_raw:
                titulo = item.get('title', '')
                location_info = item.get('location', {})
                local_nome = location_info.get('name', '') if location_info else 'Não especificado'
                
                if termo in titulo.lower() and "brazil" in local_nome.lower():
                    vagas_filtradas.append({
                        "titulo": titulo,
                        "local": local_nome,
                        "link": item.get('absolute_url')
                    })
            return vagas_filtradas
    except Exception as e:
        print(f"Erro na engine Greenhouse: {e}")
    return []

def engine_gupy(url, config_extra, termo_busca):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    url_completa = f"{url}&jobName={termo_busca}"
    
    try:
        response = requests.get(url_completa, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            lista_vagas = dados.get('data', [])
            
            vagas_filtradas = []
            for vaga in lista_vagas:
                titulo = vaga.get('name', '')
                cidade = vaga.get('city', '')
                estado = vaga.get('state', '')
                localizacao = f"{cidade} - {estado}" if cidade and estado else "Brasil"
                link = vaga.get('jobUrl', '')
                
                vagas_filtradas.append({
                    "titulo": titulo,
                    "local": localizacao,
                    "link": link
                })
            return vagas_filtradas
        else:
            print(f"⚠️ API Gupy retornou Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"Erro na engine Gupy: {e}")
    return []

MAPA_ENGINES = {
    "workday": engine_workday,
    "greenhouse": engine_greenhouse,
    "gupy": engine_gupy
}