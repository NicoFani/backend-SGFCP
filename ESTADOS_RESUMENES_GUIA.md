# Estados de Resúmenes de Liquidación - Guía Técnica y de Negocio

## Definición de Estados

### 1. **draft** (Borrador)

**Cuándo ocurre**: Generación manual de resúmenes  
**Quién lo crea**: Admin al hacer clic en "Generar Resúmenes"  
**Qué significa**: El resumen fue creado pero aún no está listo para aprobación  
**Acciones permitidas**:

- Recalcular (genera un nuevo resumen, descarta el anterior)
- Ver detalles
- Cambiar a draft nuevamente

**Ejemplo de flujo**:

```
Admin: "Generar Resúmenes" (manual) para Enero 2026
  ↓
Sistema: Crea resumen para cada chofer en estado "draft"
  ↓
Admin: Revisa los totales y verifica que sean correctos
  ↓
Admin: Si está incorrecto, recalcula
  ↓
Admin: Cuando esté satisfecho, puede mover a "pending_approval"
```

---

### 2. **calculation_pending** (Cálculo Pendiente)

**Cuándo ocurre**: Generación automática con viajes en curso  
**Quién lo crea**: Scheduler automático al final del período  
**Qué significa**: No se pudo completar el cálculo porque el chofer tenía viajes sin finalizar  
**Acciones permitidas**:

- Solo lectura (es automático)
- Se recalcula automáticamente cuando se complete el viaje
- Ver "por qué está en este estado"

**Restricción importante**:

- Si el chofer tiene 1 o más viajes en estado "Pendiente" o "En curso" al final del período
- El resumen NO se genera completamente
- Espera a que se completen TODOS los viajes
- Una vez completos, se recalcula automáticamente

**Ejemplo de flujo**:

```
30/01/2026 23:59:00 - Scheduler se ejecuta
  ↓
Sistema: Detecta al Chofer A con 3 viajes finalizados y 1 en curso
  ↓
Sistema: Crea resumen en estado "calculation_pending"
  ↓
Sistema: Registra en error_message: "Pendiente finalización de 1 viaje en curso"
  ↓
31/01/2026 - Chofer A completa el viaje en curso
  ↓
Sistema (webhook): Recalcula automáticamente
  ↓
Si todo OK → resumen pasa a "pending_approval"
Si error de tarifa → resumen pasa a "error"
```

---

### 3. **pending_approval** (Pendiente de Aprobación)

**Cuándo ocurre**:

- Generación automática sin viajes en curso (TODO OK)
- Cuando se recalcula un resumen en "error" después de corregir la tarifa

**Quién lo crea**: Scheduler o Admin (recalculando)  
**Qué significa**: El resumen está listo para ser revisado y aprobado  
**Acciones permitidas**:

- Revisar detalles
- Aprobar (cambia a "approved")
- Exportar (Excel/PDF)
- Recalcular si algo cambió

**Responsabilidad**: El Admin DEBE revisar antes de aprobar

**Ejemplo de flujo**:

```
30/01/2026 23:59:00 - Scheduler se ejecuta
  ↓
Sistema: Chofer B tiene 5 viajes finalizados, todos con tarifa
  ↓
Sistema: Calcula totales:
  - Comisión: $5,000
  - Gastos reembolso: $200
  - Adelantos: -$1,000
  - Total: $4,200
  ↓
Sistema: Crea resumen en estado "pending_approval"
  ↓
Admin: Recibe notificación
  ↓
Admin: Revisa los detalles en el dashboard
  ↓
Admin: Verifica que sea correcto
  ↓
Admin: Hace clic en "Aprobar"
  ↓
Resumen pasa a "approved"
```

---

### 4. **error** (Error de Cálculo)

**Cuándo ocurre**:

- Generación automática con viajes sin tarifa
- Recálculo cuando la tarifa sigue faltando

**Quién lo crea**: Sistema automáticamente  
**Qué significa**: Hay un problema que impide la aprobación  
**Error más común**: "Los siguientes viajes no tienen tarifa cargada: CTG-001, REMITO-045"

**Acciones permitidas**:

- Ver error_message
- Admin debe corregir el problema
- Admin recalcula manualmente

**Requisitos para resolver**:

1. Cargar la tarifa en el/los viaje(s) indicado(s)
2. Hacer clic en "Recalcular Resumen" en el admin
3. Si todo OK → pasa a "pending_approval"
4. Si sigue sin tarifa → sigue en "error"

**Ejemplo de flujo**:

```
30/01/2026 23:59:00 - Scheduler se ejecuta
  ↓
Sistema: Chofer C tiene viaje CTG-001 sin tarifa
  ↓
Sistema: Crea resumen en estado "error"
  ↓
error_message: "Viaje CTG-001 no tiene tarifa cargada"
  ↓
Admin: Ve resumen en rojo (error)
  ↓
Admin: Va a viajes, busca CTG-001
  ↓
Admin: Carga tarifa $50/km
  ↓
Admin: Vuelve a resúmenes y hace clic "Recalcular"
  ↓
Sistema: Recalcula, encuentra tarifa
  ↓
Resumen pasa a "pending_approval"
```

---

### 5. **approved** (Aprobado)

**Cuándo ocurre**: Admin aprueba un resumen en "pending_approval"  
**Quién lo crea**: Admin  
**Qué significa**: El resumen está final, el chofer no puede tener otro resumen aprobado en ese período  
**Acciones permitidas**:

- Solo lectura
- Exportar (Excel/PDF) - para pago
- Ver auditoría de cambios

**Restricción clave**:

```
UN RESUMEN APROBADO POR CHOFER POR PERÍODO
```

Si intentas crear otro resumen para el mismo chofer en el mismo período:

- Si es manual → rechaza con error
- Si es automática → no genera (verifica antes)

**Ejemplo de flujo**:

```
Admin: Aprueba resumen del Chofer B para Enero 2026
  ↓
Resumen: pasa a estado "approved"
  ↓
Admin: Intenta generar otro resumen para Chofer B en Enero
  ↓
Sistema: Error → "Ya existe resumen aprobado para este chofer en enero"
  ↓
Alternativa: Si es para otro período (Febrero) → se permite
```

---

## Máquina de Estados

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJOS DE ESTADO                              │
└─────────────────────────────────────────────────────────────────┘

MANUAL (Admin genera):
┌──────────┐
│  draft   │
└────┬─────┘
     │ Admin recalcula múltiples veces
     │ (descarta anterior, crea nuevo)
     ↓
┌────────────────────┐       ┌────────────┐
│ pending_approval   │       │   error    │
└──────┬─────────────┘       └────────────┘
       │                            ↑
       │                            │
       │ Admin recalcula después
       │ de corregir tarifa
       └────────────────────────────┘
       │
       │ Admin aprueba
       ↓
┌──────────┐
│ approved │ (final)
└──────────┘

AUTOMÁTICA (Scheduler):
Período con viajes en curso:
┌──────────────────────┐
│ calculation_pending  │
└──────────┬───────────┘
           │ Se completa viaje
           │ (webhook)
           ↓
    ┌──────────────┐
    │ Recalcular   │
    └──────┬───────┘
           │
           ├─────── (si OK) ────→ ┌────────────────────┐
           │                      │ pending_approval   │
           │                      └────────────────────┘
           │
           └────── (si sin tarifa) → ┌────────┐
                                    │ error  │
                                    └────────┘

Período sin viajes en curso:
┌────────────────────────┐    ┌─────────────────────┐
│ pending_approval (OK)  │    │ error (falta tarifa)│
└────────────────────────┘    └─────────────────────┘
           │
           │ Admin aprueba
           ↓
┌──────────┐
│ approved │
└──────────┘
```

---

## Validaciones Críticas

### 1. Al Generar Resumen Automático

```python
if viajes_en_curso > 0:
    estado = "calculation_pending"
    return  # No continúa con cálculos

if algún_viaje_finalizado_sin_tarifa:
    estado = "error"
    return  # No continúa

# Si todo OK:
estado = "pending_approval"
```

### 2. Al Completar un Viaje

```python
if resumen_en_calculation_pending_existe:
    if no_hay_mas_viajes_en_curso:
        recalcular_resumen()
    else:
        # Seguir esperando otros viajes
```

### 3. Al Aprobar Resumen

```python
if resumen.status != "pending_approval":
    raise Error("Solo se aprueban pendientes")

if existe_resumen_aprobado_para_este_chofer_en_este_período:
    raise Error("Ya existe uno aprobado")

resumen.status = "approved"
```

---

## Casos de Uso en Detalle

### Caso A: Chofer con viajes normales

**Escenario**: Enero 2026, Chofer A

- Viaje 1: Finalizado, $1,000 base
- Viaje 2: Finalizado, $800 base
- Viaje 3: Finalizado, $1,200 base

**Qué pasa**:

```
30/01 23:59 → Scheduler ejecuta
  → No hay viajes en curso ✓
  → Todos tienen tarifa ✓
  → Crea resumen:
      - Base: $3,000
      - Comisión (10%): $300
      - Estado: pending_approval

31/01 → Admin revisa y aprueba
  → Estado: approved
```

---

### Caso B: Chofer con viaje en curso

**Escenario**: Enero 2026, Chofer B

- Viaje 1: Finalizado, $500 base
- Viaje 2: Finalizado, $600 base
- Viaje 3: EN CURSO (iniciado 30/01, aún sin finalizar)

**Qué pasa**:

```
30/01 23:59 → Scheduler ejecuta
  → Detecta Viaje 3 en curso ✗
  → Crea resumen:
      - Estado: calculation_pending
      - Error message: "Pendiente finalización de 1 viaje en curso"

01/02 11:00 → Chofer finaliza Viaje 3
  → Sistema dispara webhook
  → Recalcula automáticamente:
      - Base: $500 + $600 + (viaje 3 con tarifa)
      - Comisión: ...
      - Estado: pending_approval (o error si falta tarifa)

01/02 16:00 → Admin revisa y aprueba
  → Estado: approved
```

---

### Caso C: Chofer sin tarifa en viaje

**Escenario**: Enero 2026, Chofer C

- Viaje 1: Finalizado, $2,000 base
- Viaje 2: Finalizado, PERO SIN TARIFA

**Qué pasa**:

```
30/01 23:59 → Scheduler ejecuta
  → No hay viajes en curso ✓
  → Valida tarifas:
      - Viaje 1: OK ✓
      - Viaje 2: NO TIENE TARIFA ✗
  → Crea resumen:
      - Estado: error
      - Error message: "Viaje REMITO-002 no tiene tarifa"

30/01 23:00 → Admin ve error
  → Va a viajes
  → Carga tarifa en REMITO-002

31/01 09:00 → Admin va a resúmenes
  → Hace clic en "Recalcular"
  → Sistema recalcula:
      - Viaje 2: ahora tiene tarifa ✓
      - Estado: pending_approval

31/01 15:00 → Admin aprueba
  → Estado: approved
```

---

## Dashboard - Colores Sugeridos

```
draft           → GRIS (borrador, puede cambiar)
calculation_pending → NARANJA (esperando acción automática)
pending_approval → AMARILLO (requiere acción del admin)
error           → ROJO (hay un problema que resolver)
approved        → VERDE (final, completado)
```

---

## Auditoría y Logs

Se recomienda registrar:

1. **Cuándo se genera cada resumen**: timestamp, quién (scheduler/admin), estado inicial
2. **Cuándo cambia de estado**: timestamp, de→a, razón
3. **Errores encontrados**: qué faltó, dónde
4. **Recálculos**: cuándo, por qué (viaje completado, manual, etc.)
5. **Aprobaciones**: timestamp, admin, notas

---

## Preguntas Frecuentes

**P: ¿Qué pasa si termina el mes pero el chofer no completó viajes?**  
R: El resumen se genera normalmente (con los que completó), estado pending_approval.

**P: ¿Puedo tener un resumen en "draft" y otro en "pending_approval" al mismo tiempo?**  
R: No. Cuando generas uno nuevo, el anterior se descarta.

**P: ¿Se recalculan automáticamente los resúmenes en "error"?**  
R: No. El admin debe corregir el problema (cargar tarifa) y hacer clic en "Recalcular".

**P: ¿Qué pasa si un viaje se completa en febrero pero su período es enero?**  
R: Si está en calculation_pending desde enero, se recalcula. Si fue error, sigue error (requiere admin).

**P: ¿Puedo cambiar un resumen de "approved" a otro estado?**  
R: No. Una vez aprobado, es final. Si necesitas cambios, debes generar un nuevo período.

---

## Migración de Base de Datos

**Ejecutar (una vez)**:

```sql
ALTER TABLE payroll_summaries ADD COLUMN is_auto_generated BOOLEAN DEFAULT FALSE;
```

**O con Alembic (si lo usas)**:

```bash
alembic revision --autogenerate -m "Add is_auto_generated to payroll_summaries"
alembic upgrade head
```
