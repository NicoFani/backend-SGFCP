# Migración del Módulo de Nómina - Resumen Final

## ✅ Migración Completada Exitosamente

Fecha: 21 de enero de 2026

---

## Cambios Aplicados en Backend

### 1. Modelos Nuevos Creados

- **MinimumGuaranteedHistory** - Histórico de mínimos garantizados por chofer
- **PayrollOtherItem** - Otros conceptos de nómina (ajustes, bonos, multas, cargos)
- **DriverCommissionHistory** - Histórico de comisiones por chofer (ya existía)

### 2. Modelos Modificados

#### Expense

- ❌ Eliminado: `toll_paid_by` (String enum)
- ✅ Agregado: `paid_by_admin` (Boolean)
  - `true` = Administración pagó (no reembolsable)
  - `false` = Chofer pagó (reembolsable)

#### Driver

- ❌ Eliminado: `commission` (ahora en DriverCommissionHistory)

#### PayrollPeriod

- ❌ Eliminado: `status`
- ❌ Eliminado: `actual_close_date`

#### PayrollSummary

- ❌ Eliminado: `calculation_type`
- ❌ Eliminado: `adjustments_applied`
- ❌ Eliminado: `expenses_to_reimburse`
- ❌ Eliminado: `expenses_to_deduct`
- ❌ Eliminado: `guaranteed_minimum_applied`
- ❌ Eliminado: `advances_deducted`
- ❌ Eliminado: `total_amount`
- ✅ Agregado: `driver_minimum_guaranteed`
- ✅ Agregado: `other_items_total`
- ✅ Agregado: `error_message`
- ✅ Modificado: `total_expenses` (suma de expenses_to_reimburse + expenses_to_deduct)
- ✅ Modificado: `total_advances` (antes advances_deducted)
- ✅ Modificado: `total_net` (antes total_amount)
- ✅ Modificado: `status` - Nuevos valores:
  - `calculation_pending` - Esperando tarifa
  - `pending_approval` - Calculada, pendiente de aprobación
  - `error` - Error en cálculo
  - `draft` - Borrador (después de recalcular)
  - `approved` - Aprobada

### 3. Controladores Nuevos

- `MinimumGuaranteedController` - CRUD de mínimos garantizados
- `PayrollOtherItemController` - CRUD de otros conceptos
- `PayrollCalculationController` - Reescrito completamente con nueva lógica

### 4. Rutas Nuevas

- `GET/POST /minimum-guaranteed` - Gestión de mínimos garantizados
- `GET /minimum-guaranteed/driver/{id}/current` - Mínimo garantizado vigente
- `GET/POST /payroll-other-items` - Gestión de otros conceptos
- `GET /payroll-other-items/period/{pid}/driver/{did}/summary` - Resumen por tipo
- `POST /payroll-summaries/{id}/recalculate` - Recalcular nómina

### 5. Schemas Nuevos/Actualizados

- `MinimumGuaranteedHistorySchema`
- `PayrollOtherItemSchema`
- `ExpenseSchema` - Actualizado con `paid_by_admin`
- `PayrollSummarySchema` - Actualizado con nuevos campos
- `GeneratePayrollSchema` - `is_manual` reemplaza `calculation_type`

---

## Migración de Base de Datos

### Scripts Ejecutados

1. ✅ `migrate_payroll_refactor.py` - Creó tablas nuevas y migró comisiones
2. ✅ `complete_table_migrations.py` - Recreó tablas con nueva estructura

### Datos Migrados

- ✅ 3 comisiones de drivers migradas a `driver_commission_history`
- ✅ Datos de `expense.toll_paid_by` convertidos a `expense.paid_by_admin`
- ✅ Datos de `payroll_summaries` consolidados en nuevos campos

### Tablas Nuevas Creadas

- ✅ `minimum_guaranteed_history`
- ✅ `payroll_other_items`
- ✅ `driver_commission_history` (ya existía desde migración anterior)

---

## Modelos Deprecados (Mantenidos por Compatibilidad)

Los siguientes modelos están marcados como DEPRECATED pero se mantienen:

- `CommissionPercentage` (usar `DriverCommissionHistory`)
- `KmRate` (usar tarifa en `Trip`)
- `MonthlySummary` (usar `PayrollSummary`)
- `PayrollAdjustment` (usar `PayrollOtherItem`)

---

## Cambios Pendientes en Frontend

Ver archivo: `FRONTEND_CHANGES_REQUIRED.md`

### Cambios Críticos Requeridos

#### 1. ExpenseData Model (`lib/models/expense_data.dart`)

```dart
// ANTES:
final String? tollPaidBy;

// DESPUÉS:
final bool? paidByAdmin;
```

#### 2. ExpenseService (`lib/services/expense_service.dart`)

```dart
// ANTES:
String? tollPaidBy,
if (tollPaidBy != null) 'toll_paid_by': tollPaidBy,

// DESPUÉS:
bool? paidByAdmin,
if (paidByAdmin != null) 'paid_by_admin': paidByAdmin,
```

#### 3. UI de Gastos

- Reemplazar dropdown (admin/chofer/puerto) por checkbox/switch
- Label: "Pagado por administración" (true) / "Pagado por chofer" (false)

### Servicios Nuevos Recomendados (Opcionales)

- `PayrollService` - Generar y gestionar nóminas
- `MinimumGuaranteedService` - Gestionar mínimos garantizados
- `PayrollOtherItemService` - Gestionar otros conceptos

---

## Nueva Lógica de Cálculo de Nómina

### Proceso de Generación

1. **Validación de Tarifa** - Si un viaje no tiene tarifa → estado `error`
2. **Cálculo de Comisión** - Suma de comisiones de todos los viajes
3. **Aplicación de Mínimo Garantizado** - Solo sobre `commission_from_trips`
4. **Suma de Gastos** - Gastos pagados por chofer (`paid_by_admin = false`)
5. **Suma de Anticipos** - Anticipos del período
6. **Suma de Otros Conceptos** - Ajustes, bonos, multas, cargos
7. **Cálculo Total Neto**:
   ```
   total_net = commission_from_trips
             + driver_minimum_guaranteed
             - total_expenses
             - total_advances
             + other_items_total
   ```

### Flujo de Recálculo

1. Usuario solicita recalcular nómina (estado `pending_approval` o `error`)
2. Nómina actual pasa a estado `draft`
3. Se genera nueva nómina con estado `pending_approval`
4. Nuevos cambios (viajes, gastos) se reflejan en la nueva nómina

---

## Testing Recomendado

### Backend

- [ ] Crear gasto con `paid_by_admin: true`
- [ ] Crear gasto con `paid_by_admin: false`
- [ ] Generar nómina con `is_manual: false`
- [ ] Generar nómina con viajes sin tarifa (verificar estado `error`)
- [ ] Recalcular nómina existente
- [ ] Crear mínimo garantizado para un chofer
- [ ] Crear otros conceptos de nómina

### Frontend

- [ ] Actualizar y probar formulario de gastos
- [ ] Verificar lectura de gastos existentes
- [ ] Probar servicios de nómina (si se implementan)

---

## Notas Importantes

### Backup

- ✅ Se crearon múltiples backups antes de migrar
- ✅ Datos históricos preservados correctamente

### Compatibilidad

- ✅ Modelos deprecados mantenidos por compatibilidad
- ✅ Frontend antiguo seguirá funcionando (con warnings)
- ⚠️ Actualizar frontend a la brevedad para aprovechar nuevas funcionalidades

### Próximos Pasos

1. Actualizar frontend (cambios en `ExpenseData` y `ExpenseService`)
2. Probar generación de nóminas en ambiente de prueba
3. Capacitar a usuarios en nuevo sistema
4. Crear datos de prueba para mínimos garantizados y otros conceptos
5. Monitorear errores en producción

---

## Archivos de Referencia

- `PAYROLL_REFACTOR_SUMMARY.md` - Documentación técnica completa
- `FRONTEND_CHANGES_REQUIRED.md` - Guía de cambios para frontend
- `migrate_payroll_refactor.py` - Script de migración inicial
- `complete_table_migrations.py` - Script de migración de tablas
- `inspect_tables.py` - Script de inspección de estructura

---

## Soporte y Contacto

Para preguntas o problemas con la migración, consultar:

1. Documentación técnica en `PAYROLL_REFACTOR_SUMMARY.md`
2. Logs de migración (si hubo errores)
3. Estructura de tablas con `inspect_tables.py`
