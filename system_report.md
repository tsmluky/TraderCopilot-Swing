# Reporte de Estado del Sistema y Diagnóstico

Este reporte detalla por qué la aplicación dejó de funcionar correctamente hoy y los pasos exactos para restaurarla manualmente.

## 🚨 Estado Crítico: Procesos "Zombis"
El problema principal que está causando la inestabilidad hoy (errores en logs, "Failed to fetch") es que **el código en ejecución es antiguo**, a pesar de que los archivos en disco se han actualizado.
- **Evidencia:** Los logs muestran errores (`TypeError`, `ValueError`) que son imposibles con el código actual (verificado).
- **Solución:** Es imperativo limpiar el entorno de ejecución.

## Resumen de Problemas y Correcciones (Ya Aplicadas en Código)

### 1. Error 404 en Admin Dashboard (`/admin/stats`)
- **Problema:** La página de Admin no cargaba datos.
- **Causa:** El router de administración (`admin.py`) existía pero no estaba "conectado" al archivo principal (`main.py`).
- **Estado Actual:** ✅ **FIXED**. He actualizado `backend/main.py` para incluir `/admin`.

### 2. Error 404 en Scan Dialog (`/analyze/lite`)
- **Problema:** Al intentar escanear, el frontend daba error 404.
- **Causa:** El frontend apuntaba a `/analyze/lite` pero el backend esperaba `/analysis/lite`. Un cambio reciente en la estructura de rutas causó esta desconexión.
- **Estado Actual:** ✅ **FIXED**. He actualizado `web/services/analysis.ts` para usar la ruta correcta `/analysis`.

### 3. Scheduler Crash (Logs)
- **Problema:** El scheduler se reinicia constantemente con errores de `ccxt` y tipos de datos.
- **Causa:** Los procesos antiguos en memoria no tienen las correcciones recientes de normalización de timeframes (minusculas) y métodos faltantes (`metadata`).
- **Estado Actual:** ✅ **FIXED (Código)**. El código en disco es correcto, pero necesita reinicio.

### 4. Componentes Faltantes (Alertas)
- **Nota:** La funcionalidad de Alertas (Watchlist) está incompleta en el backend (`routers/alerts_api.py` no existe), aunque el frontend ya tiene los botones. Esto no impide el funcionamiento general, pero los botones de alerta no funcionarán.

---

## 🛠️ Instrucciones de Reparación Manual

Para restaurar el servicio al estado funcional de ayer (con las mejoras de hoy), sigue estos pasos estrictamente:

### Paso 1: Limpieza Total (Kill Switch)
Debemos asegurar que no quede ningún proceso de Python antiguo corriendo. Abre una terminal (PowerShell) y ejecuta:

```powershell
taskkill /IM python.exe /F
taskkill /IM uvicorn.exe /F
```

*Si alguno da error de "no encontrado", es buena señal.*

### Paso 2: Verificar Archivos Clave
Asegúrate de que estos cambios existen (yo ya los he aplicado, pero puedes verificar):
1.  **backend/main.py**: Ábrelo y busca `app.include_router(admin_router, prefix="/admin")` cerca de la línea 120. Debe estar ahí.
2.  **web/services/analysis.ts**: Busca `apiFetch("/analysis/lite"`. Si dice `/analyze`, corrígelo.

### Paso 3: Iniciar Backend (Limpio)
En la terminal de `backend`:
```powershell
# Asegura entorno virtual si usas venv
venv\Scripts\activate
# Iniciar API (sin scheduler integrado para evitar bloqueos)
python main.py
```
*Espera a ver "Application startup complete".*

### Paso 4: Iniciar Scheduler (Separado)
Abre **otra** terminal para el scheduler (esto evita que bloquee la API):
```powershell
cd backend
venv\Scripts\activate
python scheduler.py
```
*Debe iniciar sin los errores de "AttributeError" o "TypeError".*

### Paso 5: Iniciar Frontend
Si no está corriendo:
```powershell
cd web
npm run dev
```

---
Una vez realizados estos pasos, el Dashboard, el Admin Panel y los Escáneres funcionarán correctamente.
