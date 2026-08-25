# TraderCopilot Swing

[![CI](https://img.shields.io/github/actions/workflow/status/tsmluky/TraderCopilot-Swing/ci.yml?label=CI&style=flat-square)](https://github.com/tsmluky/TraderCopilot-Swing/actions)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)

> Plataforma de señales para swing trading. El motor cuantitativo dice **cuándo**, y la capa
> de IA explica **por qué**, con el nivel donde la idea deja de ser válida.

## Por qué existe

Es la segunda versión de [TraderCopilot](https://github.com/tsmluky/Trader-Copilot). La
primera intentaba servir a todos los horizontes a la vez y no servía bien a ninguno. Esta se
centra en swing: operaciones de días o semanas, donde hay tiempo para pensar y la calidad del
análisis pesa más que la latencia.

El problema de fondo es el mismo. Una señal sin explicación no se puede evaluar, así que o la
obedeces a ciegas o la ignoras. Y un LLM preguntado a pelo opina con seguridad sobre un
gráfico que no ha visto.

Aquí la señal la calcula un motor determinista y la explicación la redacta un modelo que
recibe **exactamente los mismos datos**: precio, indicadores, datos on-chain, sentimiento y
noticias del activo. No adivina el contexto, se lo damos.

## Qué hace

**Motor de señales.** Estrategias independientes, cada una en su módulo y registradas en un
`registry`: ruptura de Donchian, seguimiento de tendencia, SuperTrend, y reversión a la media
con RSI o con bandas de Bollinger. Escanea muchos mercados por ciclo y filtra los que no
cumplen los criterios de entrada.

**Analista con RAG.** Para cada señal genera un informe en Markdown con resumen ejecutivo,
evaluación de riesgo y, lo más útil, **el nivel de invalidación**: el precio a partir del cual
la idea deja de tener sentido. El contexto sale de `backend/brain/<activo>/`, donde viven la
tesis, los catalizadores, el riesgo, el playbook, las noticias, los datos on-chain y el
sentimiento de cada activo.

**Varios proveedores de IA.** Gemini, DeepSeek, OpenAI y Anthropic detrás de una misma
interfaz, así que cambiar de modelo es configuración.

**Backtesting.** Validación contra histórico antes de confiar en una estrategia.

**Avisos por Telegram** y **suscripciones con Stripe.**

## Estado

Proyecto personal, de enero a **febrero de 2026**. Funcional pero **no mantenido**: fue el
último trabajo antes de pasarme a agentes conversacionales en
[Studio32](https://github.com/tsmluky/studio32-agent). La raíz del repositorio conserva
scripts de depuración de la época.

## Puesta en marcha

Python 3.11 o superior, Node.js 20 o superior y PostgreSQL 16.

```bash
git clone https://github.com/tsmluky/TraderCopilot-Swing.git
cd TraderCopilot-Swing
```

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate         # en Linux o Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # claves de API y DATABASE_URL
uvicorn main:app --reload      # migra la base al arrancar
```

Frontend:

```bash
cd ../web
npm install
npm run dev
```

Backend en `http://localhost:8000`, con la API documentada en `/docs`. Interfaz en
`http://localhost:3000`.

## Stack

| Capa | Qué usa |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Alembic |
| Base de datos | PostgreSQL 16 |
| IA | Gemini, DeepSeek, OpenAI y Anthropic tras una interfaz común |
| Frontend | Next.js 16, React 19, TypeScript |
| Autenticación | JWT |
| Pagos | Stripe |
| Avisos | Telegram |

## Aviso

Herramienta de análisis con fines educativos. **No es asesoramiento financiero** y no ejecuta
operaciones por ti. Operar conlleva riesgo real de pérdida.

Las claves de API van en tu `.env` y nunca se versionan.

Escrito por Francisco Iannicelli · [github.com/tsmluky](https://github.com/tsmluky)
