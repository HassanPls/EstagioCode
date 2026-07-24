import json
import os
import re
from datetime import datetime
from engines import MAPA_ENGINES

DATA_JSON_PATH = 'docs/vagas.json'
RESULT_MD_PATH = 'RESULT.md'

def carregar_configuracoes():
    with open('src/companies.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def eh_vaga_de_estagio(titulo):
    titulo_lower = titulo.lower()
    
    padrao_ingles = r'\b(intern|internship|internships)\b'
    
    if re.search(padrao_ingles, titulo_lower):
        return True
        
    if "estágio" in titulo_lower or "estagio" in titulo_lower or "estagi" in titulo_lower:
        return True
        
    return False

def carregar_vagas_salvas():
    if os.path.exists(DATA_JSON_PATH):
        try:
            with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def extrair_conjunto_links(dados_vagas):
    links = set()
    for vagas in dados_vagas.values():
        for vaga in vagas:
            links.add(vaga.get('link'))
    return links

def salvar_arquivos(resultados, houve_mudanca_real):
    if not houve_mudanca_real:
        print("💤 Nenhuma alteração real nas vagas. Arquivos mantidos intactos.")
        return False

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    total_vagas = sum(len(vagas) for vagas in resultados.values())

    payload_web = {
        "ultima_atualizacao": data_atual,
        "total_vagas": total_vagas,
        "empresas": resultados
    }
    
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload_web, f, ensure_ascii=False, indent=2)
    print(f"💾 Arquivo {DATA_JSON_PATH} atualizado com sucesso.")

    linhas = [
        "# Relatório Consolidado de Oportunidades Ativas\n",
        "Este documento é gerado e atualizado de forma automatizada pelo pipeline de integração contínua.\n",
        "---\n",
        f"**Última Atualização:** {data_atual} (Horário Local)\n",
        f"**Total de vagas encontradas:** {total_vagas}\n",
        "---\n"
    ]
    
    for empresa, vagas in resultados.items():
        linhas.append(f"## {empresa.upper()}")
        if vagas:
            for v in vagas:
                linhas.append(f"* **Cargo:** {v['titulo']}")
                linhas.append(f"  * Local: {v['local']}")
                linhas.append(f"  * Link: [Inscrição Direta]({v['link']})")
        else:
            linhas.append("*Nenhuma vaga compatível localizada nos filtros atuais.*")
        linhas.append("\n" + "-" * 30 + "\n")
        
    with open(RESULT_MD_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas))
    print(f"💾 Arquivo {RESULT_MD_PATH} atualizado com sucesso.")
    
    return True

def executar_busca_vagas(termos=["estágio", "intern", "internship"]):
    empresas = carregar_configuracoes()
    todas_as_vagas = {}
    
    print(f"🔍 Iniciando busca consolidada pelos termos: {termos}\n")
    
    for empresa in empresas:
        nome_empresa = empresa['nome']
        tipo_engine = empresa['engine']
        url = empresa['url_api']
        config_extra = empresa['config_extra']
        
        print(f"🏢 Verificando portal: {nome_empresa}...")
        engine_funcao = MAPA_ENGINES.get(tipo_engine)
        
        if engine_funcao:
            vagas_da_empresa = []
            links_vistos = set()
            
            for termo in termos:
                vagas_encontradas = engine_funcao(url, config_extra, termo)
                
                for vaga in vagas_encontradas:
                    if eh_vaga_de_estagio(vaga['titulo']):
                        if vaga['link'] not in links_vistos:
                            links_vistos.add(vaga['link'])
                            vagas_da_empresa.append(vaga)
            
            todas_as_vagas[nome_empresa] = vagas_da_empresa
            print(f"✅ {len(vagas_da_empresa)} vaga(s) estrita(s) encontrada(s).\n")
        else:
            print(f"❌ Engine '{tipo_engine}' não implementada.\n")
            
    return todas_as_vagas

if __name__ == "__main__":
    termos_alvo = ["estágio", "intern", "internship"]
    
    resultados_atuais = executar_busca_vagas(termos_alvo)

    dados_salvos = carregar_vagas_salvas()
    empresas_salvas = dados_salvos.get("empresas", {})

    links_novos = extrair_conjunto_links(resultados_atuais)
    links_antigos = extrair_conjunto_links(empresas_salvas)

    houve_mudanca = links_novos != links_antigos

    salvar_arquivos(resultados_atuais, houve_mudanca)