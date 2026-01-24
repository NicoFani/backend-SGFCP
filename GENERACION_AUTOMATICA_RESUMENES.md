# Generación Automática de Resúmenes de Liquidación - Cambios Implementados

## Resumen de Cambios

Se ha implementado la generación automática de resúmenes de liquidación con validaciones inteligentes de estados y un sistema de recálculo cuando se completan viajes. Los resúmenes ahora pueden estar en 5 estados diferentes según su contexto:

## Estados de Resúmenes

### 1. **draft** (Borrador)

- Estado inicial para resúmenes generados manualmente
- El admin puede revisar antes de enviarlo a aprobación
- Permite recalcular múltiples veces

### 2. **calculation_pending** (Cálculo Pendiente)

- Generado automáticamente al final del período
- El chofer tenía viajes en curso en ese momento
- El resumen espera a que se completen esos viajes
- Se recalcula automáticamente cuando se completa un viaje

### 3. **pending_approval** (Pendiente de Aprobación)

- Generado automáticamente sin viajes en curso
- Todos los viajes finalizados tienen tarifa
- El admin debe revisarlo y aprobarlo

### 4. **error** (Error de Cálculo)

- Error encontrado durante el cálculo
- Razón más común: viajes sin tarifa cargada
- El admin debe corregir la tarifa del viaje y recalcular

### 5. **approved** (Aprobado)

- Resumen final aprobado por el admin
- No se puede tener 2 resúmenes aprobados en el mismo período para el mismo chofer
- Las restricciones aseguran que un resumen solo se aprueba cuando no hay viajes en curso ni errores de tarifa

## Arquitectura Implementada

### 1. Modelo Actualizado (`app/models/payroll_summary.py`)

```python
is_auto_generated = db.Column(db.Boolean, default=False)  # Indica si fue generado automáticamente
```

### 2. Scheduler (`app/scheduler.py`)

- **Función**: `generate_auto_payroll_summaries()`
  - Se ejecuta el último día de cada mes a las 23:59
  - Busca todos los períodos que terminan ese día
  - Genera resúmenes automáticamente para todos los choferes activos

- **Función**: `recalculate_pending_payroll_summaries(driver_id, period_id)`
  - Se dispara cuando un viaje se completa (pasa a estado "Finalizado")
  - Busca resúmenes en estado "calculation_pending"
  - Recalcula automáticamente si todos los viajes están finalizados

### 3. Lógica de Validación en Controlador (`app/controllers/payroll_calculation.py`)

#### En `generate_summaries()`

- Verifica que no haya un resumen aprobado existente
- Elimina resúmenes en estados temporales (draft, pending_approval, error, calculation_pending)
- Permite regenerar resúmenes múltiples veces

#### En `_calculate_summary()`

- **Paso 1**: Verificar si hay viajes en curso
  - Si es generación automática y hay viajes en curso → estado `calculation_pending`
  - Si es generación manual → ignora viajes en curso
- **Paso 2**: Validar tarifas
  - Si algún viaje finalizado no tiene tarifa → estado `error`
- **Paso 3**: Calcular totales
  - Comisión por viajes
  - Gastos a reintegrar/descontar
  - Adelantos
  - Otros conceptos
  - Mínimo garantizado

### 4. Listener en Controlador de Viajes (`app/controllers/trip.py`)

Cuando un viaje cambia de estado a "Finalizado":

1. Crea ajuste retroactivo si es necesario
2. Busca el período que contiene el viaje
3. Llama a `recalculate_pending_payroll_summaries()` para recalcular resúmenes en espera

### 5. Inicialización en la App (`app/__init__.py`)

```python
with app.app_context():
    from .scheduler import start_scheduler
    app.scheduler = start_scheduler(app)
```

## Flujos de Casos de Uso

### Caso 1: Generación Automática - Viajes en Curso

```
Fin de período (último día a las 23:59)
    ↓
Scheduler ejecuta generate_summaries(is_manual=False)
    ↓
Encuentra al chofer con viajes en curso
    ↓
Resumen → estado "calculation_pending"
    ↓
Admin recibe notificación (pendiente de viajes)
    ↓
Chofer completa viaje
    ↓
Se dispara recalculate_pending_payroll_summaries()
    ↓
Resumen se recalcula y pasa a "pending_approval" (o "error" si falta tarifa)
```

### Caso 2: Generación Automática - Sin Viajes en Curso pero Sin Tarifa

```
Fin de período
    ↓
Scheduler genera resúmenes
    ↓
Encuentra viaje finalizado sin tarifa
    ↓
Resumen → estado "error" con mensaje de error
    ↓
Admin corrige la tarifa del viaje
    ↓
Admin recalcula resumen manualmente
    ↓
Resumen se recalcula y pasa a "pending_approval"
```

### Caso 3: Generación Manual por Admin

```
Admin hace clic en "Generar Resúmenes"
    ↓
POST /api/payroll/summaries/generate con is_manual=true
    ↓
Genera resúmenes solo de viajes finalizados
    ↓
Resúmenes en estado "draft"
    ↓
Admin puede revisar y recalcular varias veces
    ↓
Admin envía a aprobación (cambiar estado a pending_approval)
```

## Cambios en el Backend

### Archivos Modificados

1. **app/models/payroll_summary.py**
   - Agregado campo `is_auto_generated`

2. **app/controllers/payroll_calculation.py**
   - Mejorada lógica de `_calculate_summary()` para manejar viajes en curso
   - Se elimina el resumen anterior antes de regenerar

3. **app/controllers/trip.py**
   - Agregado listener cuando se completa un viaje
   - Llamada a `recalculate_pending_payroll_summaries()`

4. **app/**init**.py**
   - Inicialización del scheduler al crear la aplicación

5. **app/routes/payroll_summary.py**
   - Documentación actualizada del endpoint `/generate`

6. **app/schemas/payroll.py**
   - Agregado campo `is_auto_generated` en `PayrollSummarySchema`

### Archivos Nuevos

1. **app/scheduler.py**
   - Lógica de scheduler con APScheduler
   - Tarea programada para generación automática
   - Función de recálculo de resúmenes en "calculation_pending"

2. **requirements.txt**
   - Agregado `APScheduler==3.10.4`

## Instalación y Configuración

### 1. Instalar Dependencia

```bash
pip install -r requirements.txt
```

### 2. Ejecutar Migraciones (si es necesario)

```bash
# Crear campo is_auto_generated en payroll_summaries
# Esto depende de tu sistema de migraciones
```

### 3. Iniciar la Aplicación

El scheduler se inicia automáticamente al crear la aplicación con `create_app()`.

## Pruebas Recomendadas

### Prueba 1: Generación Manual

1. Crear período (Ej: 01/01 a 31/01)
2. Crear varios viajes para un chofer (mezcla de finalizados y pendientes)
3. POST /api/payroll/summaries/generate con `is_manual=true`
4. Verificar: resúmenes en estado "draft"

### Prueba 2: Viajes en Curso (Automática)

1. Crear período que termine hoy
2. Crear viaje en estado "En curso"
3. Ejecutar scheduler manualmente (o esperar a las 23:59)
4. Verificar: resumen en estado "calculation_pending"
5. Completar viaje
6. Verificar: resumen recalculado, pasa a "pending_approval"

### Prueba 3: Error de Tarifa

1. Crear período
2. Crear viaje finalizado SIN tarifa
3. Generar resumen
4. Verificar: estado "error" con mensaje
5. Cargar tarifa en el viaje
6. Recalcular resumen
7. Verificar: pasa a "pending_approval"

### Prueba 4: Aprobación Múltiple

1. Intentar aprobar 2 resúmenes en el mismo período para el mismo chofer
2. Verificar: error "Ya existe un resumen aprobado"

## API Endpoints

### Generar Resúmenes

```
POST /api/payroll/summaries/generate
Content-Type: application/json

{
    "period_id": 1,
    "driver_ids": [1, 2, 3],  // opcional
    "is_manual": false  // opcional, por defecto false
}
```

### Obtener Resúmenes

```
GET /api/payroll/summaries?period_id=1&status=pending_approval&page=1&per_page=20
```

### Aprobar Resumen

```
POST /api/payroll/summaries/{id}/approve
Content-Type: application/json

{
    "notes": "Verificado y aprobado"
}
```

## Restricciones Implementadas

1. **Una aprobación por período y chofer**: No puede haber 2 resúmenes aprobados en el mismo período para el mismo chofer

2. **Recalculo de pendientes**: Los resúmenes en "calculation_pending" solo se recalculan cuando:
   - Se completa un viaje del mismo chofer en el mismo período
   - No hay más viajes en curso

3. **Aprobación solo de pending**: Solo se pueden aprobar resúmenes en estado "pending_approval"

4. **Error de tarifa**: Si falta tarifa, el resumen va a "error" y no puede ser aprobado hasta corregir

## Logs

El scheduler registra:

- Inicio del scheduler
- Períodos encontrados que terminan hoy
- Resúmenes generados por período
- Estado de cada resumen generado
- Errores en la generación
- Recálculos automáticos ejecutados

Busca en los logs por `generate_auto_payroll_summaries` y `recalculate_pending_payroll_summaries`.

## Notas Importantes

- El scheduler se ejecuta en background, no bloquea la aplicación
- Los recálculos automáticos se ejecutan sin esperar confirmación del admin
- Los resúmenes "calculation_pending" se recalculan apenas se completa el viaje
- El sistema mantiene integridad referencial: no permite estados contradictorios
- Todos los errores se registran para auditoría y debugging
