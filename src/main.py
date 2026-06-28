import json
import os
from datetime import datetime
import requests
from engines import MAPA_ENGINES

def carregar_configuracoes():
    with open('src/companies.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_relatorio_markdown(resultados):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    linhas = []
    linhas.append("# Relatório Consolidado de Oportunidades Ativas\n")
    linhas.append("Este documento é gerado e atualizado de forma automatizada pelo pipeline de integração contínua.\n")
    linhas.append("---\n")
    linhas.append(f"**Última Atualização:** {data_atual} (Horário Local)\n")
    
    total_vagas = sum(len(vagas) for vagas in resultados.values())
    linhas.append(f"**Total de vagas encontradas:** {total_vagas}\n")
    linhas.append("---\n")
    
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
        
    with open('RESULT.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas))
    print("💾 Arquivo RESULT.md atualizado com sucesso.")

def enviar_notificacao_discord(resultados):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ DISCORD_WEBHOOK_URL não configurada no ambiente. Pulando notificação.")
        return

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_vagas = sum(len(vagas) for vagas in resultados.values())
    
    embed = {
        "title": "📋 Novo Relatório de Vagas de Estágio",
        "description": f"Varredura concluída com sucesso em {data_atual}.\nTotal de oportunidades encontradas: **{total_vagas}**",
        "color": 3447003,  
        "fields": []
    }
    
    for empresa, vagas in resultados.items():
        if vagas:
            texto_vagas = ""
            for v in vagas[:5]:  
                texto_vagas += f"• [{v['titulo']}]({v['link']}) - {v['local']}\n"
            
            if len(vagas) > 5:
                texto_vagas += f"*...e mais {len(vagas) - 5} vagas listadas no RESULT.md*"
        else:
            texto_vagas = "*Nenhuma vaga encontrada.*"
            
        embed["fields"].append({
            "name": empresa.upper(),
            "value": texto_vagas,
            "inline": False
        })

    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("🚀 Notificação enviada com sucesso para o Discord!")
        else:
            print(f"❌ Erro ao enviar para o Discord: Código {response.status_code}")
    except Exception as e:
        print(f"❌ Falha de rede ao conectar com o Discord: {e}")

def executar_busca_vagas(termo="estágio"):
    empresas = carregar_configuracoes()
    todas_as_vagas = {}
    
    print(f"🔍 Iniciando busca consolidada por: '{termo}'\n")
    
    for empresa in empresas:
        nome_empresa = empresa['nome']
        tipo_engine = empresa['engine']
        url = empresa['url_api']
        config_extra = empresa['config_extra']
        
        print(f"🏢 Verificando portal: {nome_empresa}...")
        engine_funcao = MAPA_ENGINES.get(tipo_engine)
        
        if engine_funcao:
            vagas_encontradas = engine_funcao(url, config_extra, termo)
            todas_as_vagas[nome_empresa] = vagas_encontradas
            print(f"✅ {len(vagas_encontradas)} vaga(s) encontrada(s).\n")
        else:
            print(f"❌ Engine '{tipo_engine}' não implementada.\n")
            
    return todas_as_vagas

if __name__ == "__main__":
    resultados = executar_busca_vagas("estágio")
    salvar_relatorio_markdown(resultados)
    enviar_notificacao_discord(resultados)