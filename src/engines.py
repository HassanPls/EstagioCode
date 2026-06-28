import requests
from bs4 import BeautifulSoup

def engine_workday(url, config_extra, termo_busca):
    """Trata requisições POST para a plataforma Workday (ex: Santander)"""
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
    """Trata requisições GET para a plataforma Greenhouse (ex: Nubank)"""
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

def engine_talentbrew(url, config_extra, termo_busca):
    """Trata raspagem baseada em HTML (SSR) para a plataforma TalentBrew (ex: Itaú)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            secao_resultados = soup.find(id="search-results-list") or soup.find(class_="search-results")
            
            vagas_filtradas = []
            
            if secao_resultados:
                cards_vagas = secao_resultados.find_all('a')
                
                for card in cards_vagas:
                    titulo_elemento = card.find(['h2', 'h3'])
                    titulo = titulo_elemento.get_text(strip=True) if titulo_elemento else card.get_text(strip=True)
                    
                    href = card.get('href', '')
                    if href.startswith('/'):
                        link_completo = f"{config_extra.get('base_url')}{href}"
                    else:
                        link_completo = href
                        
                    local_elemento = card.find(class_='job-location') or card.find('span')
                    local = local_elemento.get_text(strip=True) if local_elemento else "Brasil"
                    
                    if termo_busca.lower() in titulo.lower():
                        vagas_filtradas.append({
                            "titulo": titulo,
                            "local": local,
                            "link": link_completo
                        })
                        
            return vagas_filtradas
            
    except Exception as e:
        print(f"Erro na engine TalentBrew: {e}")
    return []

MAPA_ENGINES = {
    "workday": engine_workday,
    "greenhouse": engine_greenhouse,
    "talentbrew": engine_talentbrew
}