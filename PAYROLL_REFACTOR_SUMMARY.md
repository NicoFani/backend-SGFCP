# Resumen de Cambios - Refactorización Módulo Payroll

## 📋 CAMBIOS IMPLEMENTADOS

### ✅ Nuevos Modelos Creados

#### 1. **MinimumGuaranteedHistory** (`app/models/minimum_guaranteed_history.py`)

- Historial de mínimo garantizado por chofer
- Campos: `driver_id`, `minimum_guaranteed`, `effective_from`, `effective_until`
- Permite rastrear cambios en el mínimo garantizado a lo largo del tiempo

#### 2. **PayrollOtherItem** (`app/models/payroll_other_item.py`)

- Otros conceptos de liquidación (reemplaza `PayrollAdjustment`)
- Tipos: `adjustment`, `bonus`, `extra_charge`, `fine_without_trip`
- Campos: `driver_id`, `period_id`, `item_type`, `description`, `amount`, `date`

### ✅ Modelos Modificados

#### 1. **Expense** (`app/models/expense.py`)

- ✅ Agregado: `paid_by_admin` (Boolean) - reemplaza `toll_paid_by`
- ❌ Eliminado: `toll_paid_by` (enum)
- **Lógica**: Para reparaciones y peajes, `paid_by_admin=False` → se reintegra al chofer

#### 2. **PayrollSummary** (`app/models/payroll_summary.py`)

- ✅ Agregado: `driver_minimum_guaranteed` - mínimo garantizado vigente
- ✅ Agregado: `other_items_total` - total de otros conceptos
- ✅ Agregado: `error_message` - descripción de error si falta tarifa
- ❌ Eliminado: `calculation_type` - ahora siempre es 'both'
- ❌ Eliminado: `adjustments_applied` - reemplazado por `other_items_total`
- **Estados actualizados**: `calculation_pending`, `pending_approval`, `error`, `draft`, `approved`

#### 3. **Driver** (`app/models/driver.py`)

- ❌ Eliminado: `commission` - ahora se usa `DriverCommissionHistory`
- La comisión ahora se obtiene del histórico según la fecha

#### 4. **PayrollPeriod** (`app/models/payroll_period.py`)

- ❌ Eliminado: `status` - los estados se manejan en los resúmenes
- ❌ Eliminado: `actual_close_date` - ya no se usa

#### 5. **base.py** (`app/models/base.py`)

- ❌ Eliminado: `toll_paid_by_enum` - reemplazado por boolean `paid_by_admin`

### ✅ Controlador Actualizado

#### **PayrollCalculationController** (`app/controllers/payroll_calculation.py`)

**Completamente reescrito con nueva lógica:**

##### Funciones Nuevas:

- `generate_summaries(period_id, driver_ids, is_manual)` - parámetro `is_manual` para diferenciar generación
- `_get_minimum_guaranteed(driver_id, reference_date)` - obtiene mínimo del histórico
- `_calculate_other_items()` - calcula ajustes, bonificaciones, cargos, multas sin viaje
- `recalculate_summary(summary_id)` - recalcula resumen (pendiente → draft + nuevo pendiente)
- `update_calculation_pending_summaries()` - actualiza resúmenes en espera cuando se finalizan viajes
- `_check_driver_trips_in_progress()` - verifica si hay viajes en curso

##### Lógica Actualizada:

- **Validación de tarifa**: Si falta tarifa en algún viaje → `status='error'` con mensaje
- **Cálculo unificado**: Siempre calcula ambos tipos (por km y por tonelada) según campo `calculated_per_km` del viaje
- **Gastos con `paid_by_admin`**:
  - Reparaciones: `paid_by_admin=False` → se reintegra
  - Peajes: `paid_by_admin=False` → se reintegra
  - Multas: siempre se descuentan
  - Viáticos: siempre se reintegran
- **Estados automáticos**:
  - Manual → `draft`
  - Automático + viajes en curso → `calculation_pending`
  - Automático + sin viajes en curso → `pending_approval`

### ❌ Modelos Deprecated (mantener por compatibilidad)

Los siguientes modelos están marcados como DEPRECATED pero se mantienen en el código:

1. **CommissionPercentage** - usar `DriverCommissionHistory`
2. **KmRate** - la tarifa ahora va en el campo `rate` de cada viaje
3. **MonthlySummary** - usar `PayrollSummary`
4. **PayrollAdjustment** - usar `PayrollOtherItem`

## 🔄 Estados de Resúmenes

| Estado                | Descripción                                      | Cuándo se aplica                            |
| --------------------- | ------------------------------------------------ | ------------------------------------------- |
| `calculation_pending` | Fecha alcanzada pero hay viaje en curso          | Generación automática con viajes pendientes |
| `pending_approval`    | Generado automáticamente y listo para aprobar    | Generación automática sin viajes pendientes |
| `error`               | Falta tarifa en algún viaje                      | Validación en cálculo                       |
| `draft`               | Generado manualmente o reemplazado por recálculo | Generación manual o al recalcular           |
| `approved`            | Definitivo, aprobado por contador                | Aprobación manual                           |

## 🔧 Flujo de Generación de Resúmenes

### Generación Manual (en cualquier momento)

1. Admin genera resumen manualmente
2. Estado → `draft`
3. Solo incluye viajes finalizados hasta ese momento

### Generación Automática (último día del mes)

1. Sistema genera resumen automáticamente
2. Verifica si hay viajes en curso:
   - **SÍ** → Estado: `calculation_pending`
   - **NO** → Estado: `pending_approval`
3. Cuando viaje en curso se finaliza → `update_calculation_pending_summaries()` recalcula

### Recálculo

1. Contador detecta error en resumen `pending_approval` o `error`
2. Corrige datos (carga tarifa, ajusta gastos, etc.)
3. Presiona "Recalcular"
4. Resumen actual → `draft`
5. Nuevo resumen → `pending_approval`

## 📊 Cálculo de Comisión

### Fórmula:

```
comision_por_viajes = suma_de_viajes(
    SI viaje.calculated_per_km:
        base = viaje.estimated_kms * viaje.rate
    SINO:
        base = (viaje.load_weight_on_unload / 1000) * viaje.rate

    comision_viaje = base * (driver_commission_percentage / 100)
)

minimo_garantizado_aplicado = max(0, driver_minimum_guaranteed - comision_por_viajes)

total = (
    comision_por_viajes +
    gastos_a_reintegrar +
    minimo_garantizado_aplicado +
    otros_conceptos -
    gastos_a_descontar -
    adelantos
)
```

## 🗄️ Migración de Base de Datos

**Archivo**: `migrate_payroll_refactor.py`

### Pasos Necesarios:

1. **Backup de base de datos** (IMPORTANTE)
2. Migrar comisiones de `driver.commission` → `driver_commission_history`
3. Modificar tabla `expense` (agregar `paid_by_admin`, eliminar `toll_paid_by`)
4. Modificar tabla `driver` (eliminar `commission`)
5. Modificar tabla `payroll_periods` (eliminar `status`, `actual_close_date`)
6. Modificar tabla `payroll_summaries` (nuevos campos)
7. Crear tabla `minimum_guaranteed_history`
8. Crear tabla `payroll_other_items`

**NOTA**: SQLite no soporta `ALTER TABLE DROP COLUMN`, por lo que algunas tablas requieren recreación manual.

## 📝 Tareas Pendientes / Próximos Pasos

1. **Actualizar routes y schemas** para reflejar nuevos campos
2. **Actualizar frontend** para manejar nuevos estados y campos
3. **Implementar exportación a Excel/PDF** (revisar `payroll_export.py`)
4. **Crear endpoints para**:
   - Gestión de `MinimumGuaranteedHistory`
   - Gestión de `PayrollOtherItem`
   - Endpoint `recalculate_summary`
5. **Testing** de toda la lógica nueva
6. **Documentación de API** actualizada

## ⚠️ Consideraciones Importantes

- Los modelos deprecated se mantienen por compatibilidad pero NO USAR
- La comisión y el mínimo garantizado son IGUALES para todos los viajes del mismo período (se consultan al momento de generar el resumen)
- El campo `rate` en Trip puede ser NULL al iniciar viaje (el chofer lo carga después o admin al calcular)
- El combustible con vale (`fuel_on_client=True` en Trip) NO influye en el cálculo de comisiones
- Los adelantos solo vienen del administrador (no del cliente)
