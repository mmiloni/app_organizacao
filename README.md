# 🧠 Infos e Pendências

Aplicação interna para organização pessoal com anotações diárias, gestão de tarefas, controle de 1:1 e links úteis.

---

## ✅ Requisitos

- Python 3.8+
- Git instalado
- Acesso ao terminal (Command Prompt / PowerShell no Windows, Terminal no macOS/Linux)

---

## 🔧 Passos para rodar o projeto

### 1. Clone o repositório (após subir para GitHub)

```bash
git clone https://github.com/mmiloni/app_organizacao.git
cd app_organizacao
```

---

### 2. Crie o ambiente virtual

#### 💻 Windows (PowerShell):

```bash
python -m venv venv
.env\Scriptsctivate
```

#### 🍎 macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Crie o banco de dados

Antes de rodar a aplicação, execute o script de criação do banco:

```bash
python criar_banco.py
```

Esse script irá criar o arquivo `infos_pendencias.db` com as tabelas necessárias.

---

### 5. Rode a aplicação

```bash
streamlit run app.py
```

Abra o navegador no endereço informado (geralmente `http://localhost:8501`).

---


## ✍️ Observação

Se você clonar esse repositório, **lembre-se de executar o `criar_banco.py` antes de rodar o app**, caso contrário a aplicação não funcionará corretamente.
