# Guia de Instalação e Configuração do ReadRelint

Este documento descreve o passo a passo para clonar, configurar e executar o ReadRelint em uma nova máquina Windows.

---

## 📋 Pré-requisitos

1. **Python (versão 3.10 ou superior)**
   * Baixe em: [python.org](https://www.python.org/downloads/)
   * **Importante (Windows):** durante a instalação, marque a caixa **"Add Python to PATH"**.
2. **Node.js (LTS) e npm**
   * Baixe em: [nodejs.org](https://nodejs.org/) — necessário para o dashboard web (SvelteKit).
3. **Ollama**
   * Baixe e instale em: [ollama.com](https://ollama.com/)
   * Necessário para rodar o modelo de IA localmente (extração cognitiva 100% offline). Sem o Ollama ativo, o sistema opera automaticamente no motor determinístico (regex/spaCy), sem perda de funcionalidade.
4. **Git**
   * Baixe e instale em: [git-scm.com](https://git-scm.com/)

---

## 🛠️ Passo a Passo de Instalação

### 1. Clonar o Repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
cd ReadRelint
```

### 2. Baixar o Modelo de IA no Ollama
Com o Ollama em execução em segundo plano, baixe o modelo usado pelo sistema:
```bash
ollama run llama3.1
```
(≈4.7 GB de download. Digite `/bye` para sair do prompt interativo após o término.)

### 3. Configurar o Ambiente Virtual do Python
**No Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```
**No Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar as Dependências do Backend
Com o ambiente virtual ativado (`(.venv)` no prompt):
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Instalar as Dependências do Frontend
```bash
cd frontend
npm install
cd ..
```

---

## 🧪 Validar a Instalação (Opcional)

Suíte de testes do backend:
```bash
pytest
```

Verificação de tipos do frontend:
```bash
cd frontend
npm run check
cd ..
```

---

## 🚀 Como Executar o Sistema

### Iniciar o Painel Desktop
* **Método rápido:** dê duplo clique em `Iniciar-Painel.bat` na raiz do projeto.
* **Via terminal** (com o ambiente virtual ativado):
  ```bash
  python painel.py
  ```

O painel desktop (PyQt6) atua como um hub central: a partir dele você liga/desliga o monitoramento de pastas, o servidor backend (FastAPI, porta `:8000`) e o dashboard web (SvelteKit, porta `:5173`), que abre automaticamente no navegador ao ser iniciado.

---

## 📂 Organização das Pastas pós-instalação
* Ao iniciar o monitoramento, selecione uma pasta local contendo os PDFs de RELINTs.
* O banco de dados relacional (SQLite, modo WAL) é gerado automaticamente em `data/relints.db`.
* Fotos e anexos extraídos dos PDFs ficam em `data/media/`.
