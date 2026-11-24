# Mockups y Flujo de Interfaz (UI/UX): Aplicación WTP Latinex Data Hub

> [!NOTE]
> Wireframes iniciales de referencia (v2.0). En la implementación productiva actual, la consola administrativa está separada en `/admin` (protegida por contraseña) y el Paso 3 utiliza pestañas interactivas con vistas previas de Power BI y Python/API. Ver [`../README.md`](../README.md).

**Proyecto:** Latinex Data Hub: Etapa 2 (IE-PRY-002)  
**Sub-entregable Asociado:** D1.1: Metodología de Pricing & Captura WTP  
**Módulo:** Flujo de Navegación y Wireframes de la Aplicación WTP  
**Versión:** 2.0  
**Fecha de Actualización:** 2026-11-09  

---

## 1. Sistema de Navegación y Segregación de Vistas

La aplicación WTP cuenta con dos vistas principales accesibles mediante el selector de roles en la barra superior:
- **Vista Encuesta Institucional (Evaluador / Cliente):** Wizard guiado de 5 pasos diseñado para decisores de mesas de dinero, tesorería, operaciones y tecnología.
- **Vista Consola de Inteligencia Tarifaria (Super Admin / Junta Directiva):** Tablero de analítica consolidada con curvas de percepción, proyección de ingresos y matriz de auditoría confidencial.

```text
+--------------------------------------------------------------------------------------------------+
| [ ▽ LATINEX DATA HUB ]  Aplicación Oficial de Evaluación Tarifaria   | Modo: (•) Encuesta ( ) Admin|
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Flujo del Wizard Institucional (5 Pasos)

### Barra de Progreso del Wizard
```text
( 1. Introducción ) ──► ( 2. Perfil ) ──► ( 3. Solución ) ──► ( 4. Umbrales ) ──► ( 5. Probabilidad )
```

---

### 2.1. Pantalla Paso 1: Introducción y Contexto Institucional

```text
+--------------------------------------------------------------------------------------------------+
| PASO 1 DE 5: CONTEXTO INSTITUCIONAL                                                              |
| Modernización, Sostenibilidad y Competitividad del Ecosistema Bursátil                           |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | Una plataforma al servicio de las instituciones del mercado                                  | |
| | El Latinex Data Hub representa un paso decisivo en la modernización del mercado de valores    | |
| | de Panamá, permitiendo a puestos de bolsa, bancos, administradores de inversión y custodios   | |
| | acceder de forma directa, automatizada y segura a la información bursátil oficial sin        | |
| | fricciones manuales.                                                                         | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| +---------------------------------------------+ +----------------------------------------------+ |
| | (•) Sostenibilidad y Calidad de Servicio    | | (•) Propósito de esta Consulta               | |
| | Una infraestructura de datos institucional  | | El objetivo es construir un referente        | |
| | exige inversión continua en disponibilidad, | | tarifario equilibrado y transparente,        | |
| | ciberseguridad, ingeniería especializada y  | | alineado con el ahorro operativo real,       | |
| | soporte ágil. Existe una relación directa   | | asegurando que la bolsa cuente con los       | |
| | entre la sostenibilidad económica de este   | | recursos necesarios para mantener una        | |
| | servicio y la capacidad de la bolsa para    | | capacidad técnica robusta, competitiva y en  | |
| | ofrecer a sus instituciones miembros la     | | constante crecimiento.                       | |
| | atención inmediata y estabilidad requerida. | |                                              | |
| +---------------------------------------------+ +----------------------------------------------+ |
|                                                                                                  |
| [ Le invitamos a evaluar con criterio objetivo, valorando la eficiencia que genera y el         ] |
| [ estándar de respaldo institucional que su organización espera de la bolsa local.              ] |
|                                                                                                  |
|                                                     [ Comenzar: Perfil Institucional -> ]       |
+--------------------------------------------------------------------------------------------------+
```

---

### 2.2. Pantalla Paso 2: Perfil Institucional y Esfuerzo Operativo

```text
+--------------------------------------------------------------------------------------------------+
| PASO 2 DE 5: IDENTIFICACIÓN INSTITUCIONAL Y ESFUERZO OPERATIVO ACTUAL                            |
+--------------------------------------------------------------------------------------------------+
| Institución Financiera: [ [Nombre de su Institución / Puesto de Bolsa]          ]                |
| Contacto / Evaluador:   [ [Nombre o Cargo del Evaluador]                        ]                |
| Segmento de Mercado:    [ Puesto de Bolsa / Casa de Valores                   v ]                |
| Rol en la Decisión:     [ Decisor Comercial, Mesa de Dinero o Dirección        v ]                |
|                                                                                                  |
| Horas-Hombre Mensuales Manuales (Descarga/Carga de Información de Mercado): [ 46  ] hrs/mes       |
| Costo Hora Estimado de Personal:                                            [ $25 ] USD / hr     |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | Ahorro Operativo Directo Estimado: 46 horas mensuales x $25/hr      = ~$1,150.00 USD / mes    | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| [ <- Paso Anterior ]                                                [ Siguiente: Solución -> ]   |
+--------------------------------------------------------------------------------------------------+
```

---

### 2.3. Pantalla Paso 3: Solución Integral y Alcance del Servicio

```text
+--------------------------------------------------------------------------------------------------+
| PASO 3 DE 5: ALCANCE DE LA SOLUCIÓN INTEGRAL                                                     |
+--------------------------------------------------------------------------------------------------+
| Al evaluar el valor en el siguiente paso, considere la solución integral que su entidad recibe:  |
| conectividad automatizada a la información oficial y consola corporativa para gestión de accesos.|
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | CONJUNTOS DE INFORMACIÓN BURSÁTIL DISPONIBLES (8 ENDPOINTS OPENAPI OFICIALES)                 | |
| | • GET /v1/trades                      | Cinta de transacciones ejecutadas (paginada)         | |
| | • GET /v1/prices                      | Histórico de precios oficiales de cierre             | |
| | • GET /v1/market/offers               | Libro de posturas vigentes por profundidad           | |
| | • GET /v1/instruments                 | Catálogo maestro de títulos valores                  | |
| | • GET /v1/instruments/{sym}/pay-plan  | Cronograma proyectado de cupones y amortizaciones     | |
| | • GET /v1/instruments/search          | Buscador multicriterio de instrumentos               | |
| | • GET /v1/discovery                   | Catálogo de colecciones y servicios disponibles      | |
| | • GET /v1/datasets/availability       | Cobertura histórica y disponibilidad de series       | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | CAPACIDADES DE LA CONSOLA CORPORATIVA INCLUIDAS EN LA SUSCRIPCIÓN                            | |
| | [ Credenciales M2M ] [ Métricas de Consumo ] [ Sandbox de Pruebas ] [ Recetas ] [ Usuarios ] | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| [x] He revisado el alcance de la solución y las capacidades corporativas incluidas.              |
|                                                                                                  |
| [ <- Paso Anterior ]                                                [ Siguiente: Umbrales -> ]   |
+--------------------------------------------------------------------------------------------------+
```

---

### 2.4. Pantalla Paso 4: Umbrales de Sensibilidad de Precios

```text
+--------------------------------------------------------------------------------------------------+
| PASO 4 DE 5: LOS 4 UMBRALES DE SENSIBILIDAD DE PRECIOS                                           |
+--------------------------------------------------------------------------------------------------+
| Indique los cuatro niveles de tarifa mensual (en USD / mes) para la suscripción de su entidad:   |
|                                                                                                  |
| 1. MUY BARATO (Dudaría de calidad o soporte):       [ $ 450.00  ] USD / mes                      |
| 2. BARATO / BUENA OFERTA (Excelente relación valor):[ $ 750.00  ] USD / mes                      |
| 3. CARO (Elevado, pero aún justificable):           [ $ 900.00  ] USD / mes                      |
| 4. MUY CARO (Descartaría completamente contratar):  [ $ 1,500.00] USD / mes                      |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | [✓] Validación Correcta: $450 < $750 < $900 < $1,500                                         | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| [ <- Paso Anterior ]                                            [ Siguiente: Probabilidad -> ]   |
+--------------------------------------------------------------------------------------------------+
```

---

### 2.5. Pantalla Paso 5: Probabilidad de Compra y Servicios Adicionales

```text
+--------------------------------------------------------------------------------------------------+
| PASO 5 DE 5: PROBABILIDAD DE COMPRA Y SERVICIOS ADICIONALES                                      |
+--------------------------------------------------------------------------------------------------+
| A. Si la tarifa oficial fuera su precio BARATO ($750 USD/mes):                                   |
|    ¿Qué tan probable es que su institución contrate el servicio en los próximos 90 días?         |
|    [ 5: Definitivamente SÍ lo contrataría                                                     v ]|
|                                                                                                  |
| B. Si la tarifa oficial fuera su precio CARO ($900 USD/mes):                                     |
|    ¿Qué tan probable es que su institución aún apruebe su contratación por el beneficio?         |
|    [ 3: Podría contratarlo o no / Indeciso                                                    v ]|
|                                                                                                  |
| SERVICIOS ADICIONALES OPCIONALES:                                                                |
| (Facturación adicional a la suscripción mensual de datos)                                        |
| [x] Conector Automatizado AWS S3 para Hechos Relevantes      ($500 Setup + $100/mes adicional)   |
| [x] Tablero Interactivo con Marca Institucional              ($1,800 Setup + $250/mes adicional) |
| [ ] Cliente Programático (API Client / SDK Institucional)    ($900 Setup + $100/mes adicional)   |
|                                                                                                  |
| [ <- Paso Anterior ]                                     [ ✓ Registrar Evaluación y Guardar ]    |
+--------------------------------------------------------------------------------------------------+
```

---

## 3. Consola de Inteligencia Tarifaria (Super Admin)

```text
+--------------------------------------------------------------------------------------------------+
| CONSOLA DE INTELIGENCIA TARIFARIA: LATINEX DATA HUB          | Muestra Registrada: 12 Entidades  |
| Tablero de Estimación de Precios y Optimización de Ingresos                                      |
+--------------------------------------------------------------------------------------------------+
| Proyección de Capacidad Técnica para la Junta Directiva:                                         |
| Al precio óptimo de $775 / mes, la bolsa proyecta recaudar ~$111,600 USD anuales.                |
| Capacidad financiada: Ingeniería dedicada de soporte, SLA garantizado 99.8% y expansión datasets|
+--------------------------------------------------------------------------------------------------+
| Límite Inferior    | Precio Mín. Resistencia | Punto Medio Merc. | Límite Superior | Máx. Ingreso MRR|
|      $525          |         $525            |       $770        |     $1,100      |   $775 / mes    |
| (Duda de calidad)  | (Menor rechazo)         | (Equilibrio B/C)  | (Descarta comp.)| ($4,690 MRR)    |
+--------------------------------------------------------------------------------------------------+
| +---------------------------------------------+ +----------------------------------------------+ |
| | CURVAS DE PERCEPCIÓN DE PRECIOS Y RAP       | | CURVA DE INGRESO MENSUAL ESPERADO (MRR)      | |
| | 100% |  \                                   | | MRR  |           Pico: $775 / mes            | |
| |      |   \                               /  | | ($)  |                 * ($4,690 MRR)         | |
| |  50% |    \     [ Rango Aceptable ]     /   | |      |             *       *                  | |
| |      |     \       $525 a $1,100       /    | |      |         *               *              | |
| |   0% +------------------------------------> | |   0  +-------------------------------------> | |
| |      $300          Precio (USD)      $2,000 | |      $300          Tarifa Mensual     $2,000 | |
| +---------------------------------------------+ +----------------------------------------------+ |
|                                                                                                  |
| MATRIZ DE RESPUESTAS REGISTRADAS (DATOS CONFIDENCIALES ANONIMIZADOS)                             |
| # | Identificador | Rol Evaluador | Segmento | M.Barato | Barato | Caro | M.Caro | Prob | S3 | Tab | SDK |
| 1 | Entidad #01   | Mesa Trading  | P. Bolsa |   $450   |  $750  | $900 | $1,500 | 5/3  | Sí | Sí  | No  |
| 2 | Entidad #02   | Gestor Inv.   | Wealth M.|   $400   |  $700  | $850 | $1,400 | 5/3  | Sí | Sí  | No  |
| 3 | Entidad #03   | Tesorería     | Banco C. |   $500   |  $850  |$1,100| $1,800 | 5/4  | Sí | No  | Sí  |
| 4 | Entidad #04   | Operaciones   | Banco/PB |   $480   |  $800  |$1,000| $1,650 | 5/3  | Sí | Sí  | Sí  |
| 5 | Entidad #05   | Riesgos       | Banco C. |   $520   |  $850  |$1,050| $1,700 | 4/3  | Sí | No  | Sí  |
| 6 | Entidad #06   | Mesa Renta F. | P. Bolsa |   $450   |  $750  | $950 | $1,550 | 5/3  | Sí | Sí  | No  |
| 7 | Entidad #07   | Arquitecto TI | Banco C. |   $480   |  $820  |$1,000| $1,600 | 4/3  | No | No  | Sí  |
| 8 | Entidad #08   | Back-Office   | Banco C. |   $380   |  $650  | $850 | $1,350 | 4/2  | No | No  | No  |
| 9 | Entidad #09   | Portafolio    | Wealth M.|   $400   |  $680  | $880 | $1,400 | 5/3  | Sí | Sí  | No  |
|10 | Entidad #10   | Trader Ppal.  | P. Bolsa |   $440   |  $740  | $920 | $1,500 | 5/3  | Sí | Sí  | No  |
|11 | Entidad #11   | Liquidaciones | Banco/PB |   $460   |  $780  | $980 | $1,550 | 4/3  | Sí | No  | Sí  |
|12 | Entidad #12   | Analítica     | Proveedor|   $420   |  $720  | $900 | $1,450 | 4/2  | No | No  | No  |
+--------------------------------------------------------------------------------------------------+
```
