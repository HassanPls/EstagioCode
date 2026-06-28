# Sistema Automatizado de Consolidação de Oportunidades de Estágio

> 📊 **Acesso Rápido aos Resultados:** O relatório atualizado com todas as vagas capturadas pelos motores de busca pode ser acessado diretamente no arquivo [RESULT.md](RESULT.md).

Este projeto consiste em um ecossistema escalável e modular voltado à coleta, filtragem e agregação de posições de estágio em canais proprietários e sistemas de rastreamento de candidatos (ATS) de instituições financeiras e empresas de tecnologia. O sistema mitiga a necessidade de consultas manuais descentralizadas por meio da execução cíclica de rotinas de engenharia reversa em APIs de recrutamento e parseamento de documentos estruturados (SSR).

## Arquitetura de Software

O ecossistema foi projetado sob os princípios de desacoplamento e configuração declarativa, dividindo-se nas seguintes camadas:

1. **Orquestrador Central (`src/main.py`)**: Coordena o ciclo de vida da execução, processando as configurações da matriz de alvos e consolidando as saídas dos motores.
2. **Motores de Coleta (`src/engines.py`)**: Implementações isoladas especializadas por plataforma (Workday, Greenhouse e TalentBrew) encarregadas de realizar requisições de rede, normalização de dados e filtragem programática fina.
3. **Matriz de Alvos (`src/companies.json`)**: Arquivo de especificação que mapeia os endpoints das empresas, permitindo a expansão da cobertura do sistema sem alteração lógica no código-fonte.

## Requisitos de Sistema

* Python 3.10 ou superior
* Bibliotecas listadas em requirements.txt (requests, beautifulsoup4)