# Funcionalidad de Recalcular Resumen

## Descripción

Se ha implementado la funcionalidad para recalcular resúmenes de liquidación manualmente. Esta es útil en dos escenarios:

1. **Recálculo manual**: El usuario toca el botón "Recalcular resumen" en la pantalla de detalle del resumen
2. **Recálculo automático**: Se finaliza un viaje y el sistema necesita recalcular un resumen que estaba en estado `calculation_pending`

## Flujo de Funcionamiento

### Cuando el usuario hace clic en "Recalcular resumen"

1. Frontend llama a `PayrollSummaryService.recalculateSummary(summaryId)`
2. Se ejecuta POST a `/api/payroll/summaries/{id}/recalculate`
3. Backend ejecuta `PayrollCalculationController.recalculate_summary(summary_id)`
4. El controlador:
   - Valida que el resumen no esté aprobado
   - Limpia los detalles existentes
   - Recalcula todos los componentes:
     - Comisión por viajes (validando tarifas)
     - Gastos a reintegrar/descontar
     - Adelantos
     - Otros conceptos
     - Mínimo garantizado
     - Total final
   - Determina el nuevo estado:
     - Si hay viajes en curso → `calculation_pending`
     - Si hay errores de tarifa → `error`
     - Si es manual y sin errores → `draft`
     - Si es automático y sin errores → `pending_approval`
5. Devuelve el resumen recalculado con todos los detalles actualizados

## Cambios en el Backend

### `app/controllers/payroll_calculation.py`

**Nuevo método**: `recalculate_summary(summary_id)`

```python
@staticmethod
def recalculate_summary(summary_id):
    """
    Recalcular un resumen existente sin cambiar su estado base.

    Útil cuando:
    - Se toca el botón "Recalcular resumen" manualmente
    - Se finaliza un viaje y necesita recalcularse un resumen en 'calculation_pending'
    """
```

**Características del método**:

- No permite recalcular resúmenes aprobados
- Limpia detalles previos para evitar duplicados
- Re-obtiene parámetros actuales (comisión, mínimo garantizado)
- Ejecuta exactamente el mismo cálculo que `_calculate_summary`
- Respeta el tipo de generación (manual vs automático)

### `app/routes/payroll_summary.py`

**Nueva ruta**: `POST /api/payroll/summaries/{id}/recalculate`

```python
@payroll_summary_bp.route('/<int:summary_id>/recalculate', methods=['POST'])
def recalculate_summary(summary_id):
    """Recalcular un resumen existente."""
```

**Respuesta exitosa** (HTTP 200):

```json
{
  "success": true,
  "data": {
    "summary": {
      /* PayrollSummaryData */
    },
    "details": [
      /* Array de PayrollDetailData */
    ]
  },
  "message": "Resumen recalculado exitosamente"
}
```

**Errores**:

- `400`: Resumen aprobado o no encontrado
- `500`: Error interno del servidor

## Cambios en el Frontend

### `lib/services/payroll_summary_service.dart`

**Nuevo método**: `recalculateSummary()`

```dart
static Future<PayrollSummaryData> recalculateSummary({
  required int summaryId,
}) async {
  // POST a /api/payroll/summaries/{summaryId}/recalculate
  // Retorna: PayrollSummaryData con los valores actualizados
}
```

### `lib/pages/admin/summary_detail.dart`

**Método implementado**: `_recalculateSummary()`

```dart
Future<void> _recalculateSummary() async {
  // 1. Muestra diálogo de carga
  // 2. Llama a PayrollSummaryService.recalculateSummary(widget.summaryId)
  // 3. Actualiza el estado local con el resumen recalculado
  // 4. Muestra SnackBar verde de éxito
  // 5. En caso de error: muestra SnackBar rojo con el mensaje
}
```

**UX**:

- Mientras se recalcula: Muestra AlertDialog con spinner + "Recalculando resumen..."
- Si éxito: SnackBar verde "Resumen recalculado exitosamente" + UI actualizado
- Si error: Cierra diálogo y muestra SnackBar rojo con el error

## Estados Posibles Después de Recalcular

| Estado Anterior       | Condición Después del Recálculo | Estado Nuevo                 |
| --------------------- | ------------------------------- | ---------------------------- |
| `draft`               | Hay viajes en curso             | `calculation_pending`        |
| `draft`               | Hay viajes sin tarifa           | `error`                      |
| `draft`               | Sin errores, es manual          | `draft`                      |
| `calculation_pending` | Hay viajes en curso             | `calculation_pending`        |
| `calculation_pending` | Hay viajes sin tarifa           | `error`                      |
| `calculation_pending` | Sin errores, es automático      | `pending_approval`           |
| `error`               | Se solucionaron los errores     | `draft` o `pending_approval` |
| `pending_approval`    | Hay viajes sin tarifa           | `error`                      |
| `pending_approval`    | Sin errores, sigue automático   | `pending_approval`           |
| `approved`            | **No se permite recalcular**    | Error 400                    |

## Validaciones

- ✅ No permite recalcular resúmenes aprobados
- ✅ Valida que el resumen exista
- ✅ Valida tarifas en viajes
- ✅ Detecta viajes en curso
- ✅ Limpia estado previo antes de recalcular
- ✅ Re-obtiene parámetros actuales del chofer

## Integración con Webhook

El método `recalculate_summary` también se llama automáticamente desde `app/routes/trip.py` cuando se finaliza un viaje:

```python
# En trip.py, en update_trip() cuando state = "Finalizado":
scheduler.recalculate_pending_payroll_summaries(driver_id, period_id)
```

Esto permite que resúmenes en `calculation_pending` se recalculen automáticamente cuando se resuelven los viajes en curso.

## Pruebas Manuales

### Test 1: Recalcular resumen draft sin cambios

1. Navega a un resumen en estado `draft`
2. Toca "Recalcular resumen"
3. **Esperado**: Resumen se recalcula, mantiene estado `draft`

### Test 2: Recalcular resumen con nuevo viaje

1. Genera un resumen manual
2. Crea un nuevo viaje para ese chofer en el mismo período
3. Toca "Recalcular resumen"
4. **Esperado**: Comisión aumenta, total se actualiza

### Test 3: Recalcular cuando hay viajes en curso

1. Crea un viaje en estado "En curso"
2. Genera resumen automático (debería estar en `calculation_pending`)
3. Toca "Recalcular resumen"
4. **Esperado**: Sigue en `calculation_pending`

### Test 4: Error - Recalcular aprobado

1. Aprueba un resumen
2. Intenta tocar "Recalcular resumen"
3. **Esperado**: Error 400 "No se puede recalcular un resumen aprobado"

## Relación con Otros Componentes

- Usa la misma lógica de cálculo que `generate_summaries()` (método privado `_calculate_summary()`)
- Respeta los estados definidos en `ESTADOS_RESUMENES_GUIA.md`
- Se integra con el webhook de viajes en `trip.py`
- Retorna datos en el mismo formato que `get_summary_details()`

## Notas de Implementación

1. **Idempotencia**: Recalcular varias veces el mismo resumen produce el mismo resultado
2. **Performance**: Limpia detalles antes de recalcular para evitar duplicados
3. **Seguridad**: Solo usuarios autenticados (JWT) pueden recalcular
4. **Atomicidad**: Todo el cálculo ocurre en una transacción de base de datos
