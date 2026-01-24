# Guía de Pruebas Manuales - Migración Módulo Payroll

## 📋 Checklist de Pruebas

### Fase 1: Verificación de Base de Datos

- [ ] Verificar estructura de tablas migradas
- [ ] Verificar datos históricos preservados
- [ ] Verificar tablas nuevas creadas

### Fase 2: Pruebas Backend (API)

- [ ] Crear gasto con paid_by_admin --> Para peaje tipo ruta falla
- [ ] Crear comisión histórica para chofer --> hay que armar la pantalla
- [ ] Crear mínimo garantizado para chofer --> hay que armar la pantalla
- [ ] Crear otros conceptos de nómina --> hay que armar la pantalla
- [ ] Generar nómina de período
- [ ] Recalcular nómina

### Fase 3: Pruebas Frontend (Flutter)

- [x ] Crear gasto desde app (con switch "Pagó contaduría")
- [ ] Editar gasto existente
- [ ] Verificar visualización de gastos

### Fase 4: Integración Backend-Frontend

- [ ] Flujo completo: crear viaje → gastos → nómina

---

## 🔍 FASE 1: Verificación de Base de Datos

### 1.1 Verificar Estructura de Tablas

**Objetivo:** Confirmar que las tablas se migraron correctamente.

**Pasos:**

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar script de inspección
python inspect_tables.py
```

**Resultado Esperado:**

```
Tabla: expense
- ✅ Campo paid_by_admin existe
- ✅ Campo toll_paid_by NO existe

Tabla: driver
- ✅ Campo commission NO existe

Tabla: payroll_periods
- ✅ Campo status NO existe
- ✅ Campo actual_close_date NO existe

Tabla: payroll_summaries
- ✅ Campos nuevos: driver_minimum_guaranteed, other_items_total, error_message
- ✅ Campos viejos NO existen: calculation_type, adjustments_applied
```

### 1.2 Verificar Datos Migrados

**Objetivo:** Confirmar que los datos históricos se preservaron.

**Pasos:**

```bash
# Verificar comisiones migradas
python -c "from app import create_app, db; from sqlalchemy import text; app = create_app(); app.app_context().push(); result = db.session.execute(text('SELECT * FROM driver_commission_history')); print('Comisiones migradas:', result.rowcount); [print(row) for row in result]"
```

**Resultado Esperado:**

- Se muestran 3 registros de comisiones históricas
- Cada registro tiene: driver_id, commission_percentage, effective_from

### 1.3 Verificar Tablas Nuevas

**Pasos:**

```bash
# Verificar tabla minimum_guaranteed_history
python -c "from app import create_app, db; from sqlalchemy import text; app = create_app(); app.app_context().push(); result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type=\"table\" AND name IN (\"minimum_guaranteed_history\", \"payroll_other_items\")')); print('Tablas encontradas:'); [print(row[0]) for row in result]"
```

**Resultado Esperado:**

```
Tablas encontradas:
minimum_guaranteed_history
payroll_other_items
```

---

## 🔌 FASE 2: Pruebas Backend (API)

### Prerequisito: Iniciar el Servidor

```bash
# Terminal 1: Backend
cd C:\Users\Nicol\OneDrive\Escritorio\backend-SGFCP
.\.venv\Scripts\Activate.ps1
python run.py
```

**Resultado Esperado:**

```
* Running on http://127.0.0.1:5000
```

### 2.1 Obtener Token de Autenticación

**Herramienta:** Postman, Thunder Client, o curl

**Request:**

```http
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "tu_password"
}
```

**Resultado Esperado:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**Acción:** Copiar el `access_token` para usarlo en las siguientes pruebas.

---

### 2.2 Prueba: Crear Gasto con paid_by_admin

**Objetivo:** Verificar que el nuevo campo funciona correctamente.

**Test 1: Gasto pagado por administración**

```http
POST http://localhost:5000/expenses/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "expense_type": "Peaje",
  "date": "2026-01-21",
  "amount": 5000,
  "description": "Peaje ruta 9",
  "toll_type": "Ruta",
  "paid_by_admin": true
}
```

**Resultado Esperado:**

```json
{
  "expense": {
    "id": X,
    "driver_id": 1,
    "expense_type": "Peaje",
    "amount": 5000,
    "paid_by_admin": true,
    "description": "Peaje ruta 9"
  }
}
```

**Test 2: Gasto pagado por chofer (reembolsable)**

```http
POST http://localhost:5000/expenses/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "expense_type": "Combustible",
  "date": "2026-01-21",
  "amount": 15000,
  "fuel_liters": 50,
  "paid_by_admin": false
}
```

**Resultado Esperado:**

```json
{
  "expense": {
    "id": X,
    "paid_by_admin": false,
    "amount": 15000
  }
}
```

**Verificación:**

- ✅ Gasto con `paid_by_admin: true` se crea correctamente
- ✅ Gasto con `paid_by_admin: false` se crea correctamente
- ✅ Campo `toll_paid_by` NO aparece en la respuesta

---

### 2.3 Prueba: Crear Comisión Histórica para Chofer

**Objetivo:** Configurar comisión específica para un chofer.

```http
POST http://localhost:5000/driver-commission/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "commission_percentage": 25.00,
  "effective_from": "2026-01-01"
}
```

**Resultado Esperado:**

```json
{
  "id": X,
  "driver_id": 1,
  "commission_percentage": 25.00,
  "effective_from": "2026-01-01T00:00:00",
  "effective_until": null
}
```

**Verificar comisión vigente:**

```http
GET http://localhost:5000/driver-commission/driver/1/current
Authorization: Bearer {tu_access_token}
```

**Resultado Esperado:**

```json
{
  "driver_id": 1,
  "commission_percentage": 25.0,
  "effective_from": "2026-01-01T00:00:00",
  "effective_until": null
}
```

---

### 2.4 Prueba: Crear Mínimo Garantizado para Chofer

**Objetivo:** Configurar mínimo garantizado específico para un chofer.

```http
POST http://localhost:5000/minimum-guaranteed/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "minimum_guaranteed": 150000.00,
  "effective_from": "2026-01-01"
}
```

**Resultado Esperado:**

```json
{
  "id": X,
  "driver_id": 1,
  "minimum_guaranteed": 150000.00,
  "effective_from": "2026-01-01T00:00:00",
  "effective_until": null
}
```

**Verificar mínimo garantizado vigente:**

```http
GET http://localhost:5000/minimum-guaranteed/driver/1/current
Authorization: Bearer {tu_access_token}
```

**Resultado Esperado:**

```json
{
  "driver_id": 1,
  "minimum_guaranteed": 150000.0,
  "effective_from": "2026-01-01T00:00:00"
}
```

---

### 2.5 Prueba: Crear Otros Conceptos de Nómina

**Objetivo:** Agregar ajustes, bonos, multas o cargos.

**Test 1: Agregar Bono**

```http
POST http://localhost:5000/payroll-other-items/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "period_id": 1,
  "item_type": "bonus",
  "description": "Bono por productividad",
  "amount": 50000,
  "date": "2026-01-21",
  "created_by": 1
}
```

**Resultado Esperado:**

```json
{
  "id": X,
  "item_type": "bonus",
  "amount": 50000,
  "description": "Bono por productividad"
}
```

**Test 2: Agregar Multa**

```http
POST http://localhost:5000/payroll-other-items/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "driver_id": 1,
  "period_id": 1,
  "item_type": "fine",
  "description": "Multa por exceso de velocidad",
  "amount": -25000,
  "date": "2026-01-21",
  "created_by": 1
}
```

**Resultado Esperado:**

```json
{
  "id": X,
  "item_type": "fine",
  "amount": -25000
}
```

**Verificar resumen de otros conceptos:**

```http
GET http://localhost:5000/payroll-other-items/period/1/driver/1/summary
Authorization: Bearer {tu_access_token}
```

**Resultado Esperado:**

```json
{
  "bonus": 50000,
  "fine": -25000,
  "adjustment": 0,
  "extra_charge": 0,
  "total": 25000
}
```

---

### 2.6 Prueba: Generar Nómina de Período

**Prerequisito:** Debe existir:

- Período de nómina activo
- Viajes completados con tarifa configurada
- Chofer con comisión histórica

**Crear período si no existe:**

```http
POST http://localhost:5000/payroll-periods/
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}
```

**Generar nómina:**

```http
POST http://localhost:5000/payroll-summaries/generate
Authorization: Bearer {tu_access_token}
Content-Type: application/json

{
  "period_id": 1,
  "driver_ids": [1],
  "is_manual": false
}
```

**Resultado Esperado (con viajes y tarifa):**

```json
{
  "summaries": [
    {
      "id": X,
      "driver_id": 1,
      "commission_from_trips": 120000.00,
      "driver_minimum_guaranteed": 30000.00,
      "total_expenses": 20000.00,
      "total_advances": 50000.00,
      "other_items_total": 25000.00,
      "total_net": 105000.00,
      "status": "pending_approval"
    }
  ]
}
```

**Resultado Esperado (sin tarifa configurada):**

```json
{
  "summaries": [
    {
      "id": X,
      "status": "error",
      "error_message": "Tarifa no configurada para viaje ID 123"
    }
  ]
}
```

**Verificación:**

- ✅ Si hay viajes con tarifa → status "pending_approval"
- ✅ Si faltan tarifas → status "error" con mensaje descriptivo
- ✅ Campo `driver_minimum_guaranteed` calculado correctamente
- ✅ Campo `other_items_total` incluye bonos y multas
- ✅ Campo `calculation_type` NO aparece en la respuesta

---

### 2.7 Prueba: Recalcular Nómina

**Objetivo:** Verificar que se puede recalcular una nómina pendiente.

**Prerequisito:** Tener una nómina en estado `pending_approval` o `error`.

```http
POST http://localhost:5000/payroll-summaries/{summary_id}/recalculate
Authorization: Bearer {tu_access_token}
```

**Resultado Esperado:**

```json
{
  "old_summary": {
    "id": X,
    "status": "draft"
  },
  "new_summary": {
    "id": Y,
    "status": "pending_approval",
    "commission_from_trips": 125000.00,
    "total_net": 110000.00
  }
}
```

**Verificación:**

- ✅ Nómina anterior pasa a estado "draft"
- ✅ Nueva nómina con estado "pending_approval"
- ✅ Nuevos cambios (viajes, gastos) reflejados en nueva nómina

---

## 📱 FASE 3: Pruebas Frontend (Flutter)

### Prerequisito: Iniciar App Flutter

```bash
# Terminal 2: Frontend
cd C:\Users\Nicol\OneDrive\Escritorio\frontend_sgfcp
flutter run
```

### 3.1 Prueba: Crear Gasto desde App

**Pasos:**

1. Abrir app Flutter
2. Iniciar sesión como chofer
3. Navegar a un viaje
4. Presionar "Cargar gasto"
5. Seleccionar tipo: "Peaje"
6. Ingresar importe: 5000
7. Seleccionar subtipo: "Ruta"
8. **Activar switch "¿Pagó contaduría?"** ← CLAVE
9. Presionar "Cargar gasto"

**Resultado Esperado:**

- ✅ Mensaje: "Gasto cargado exitosamente"
- ✅ Gasto aparece en lista del viaje

**Verificar en backend:**

```http
GET http://localhost:5000/expenses/{expense_id}
Authorization: Bearer {tu_access_token}
```

**Resultado Esperado:**

```json
{
  "id": X,
  "paid_by_admin": true,
  "expense_type": "Peaje",
  "amount": 5000
}
```

### 3.2 Prueba: Gasto Pagado por Chofer

**Pasos:**

1. Cargar nuevo gasto
2. Tipo: "Combustible"
3. Importe: 15000
4. Litros: 50
5. **NO activar switch "¿Pagó contaduría?"** ← CLAVE
6. Presionar "Cargar gasto"

**Verificar en backend:**

```http
GET http://localhost:5000/expenses/{expense_id}
```

**Resultado Esperado:**

```json
{
  "paid_by_admin": false,
  "amount": 15000
}
```

**Verificación:**

- ✅ Switch activado → `paid_by_admin: true`
- ✅ Switch desactivado → `paid_by_admin: false`

### 3.3 Prueba: Editar Gasto Existente

**Pasos:**

1. Seleccionar un gasto de la lista
2. Presionar editar
3. Cambiar importe: 6000
4. Activar/desactivar "¿Pagó contaduría?"
5. Guardar cambios

**Resultado Esperado:**

- ✅ Mensaje: "Cambios guardados"
- ✅ Gasto actualizado con nuevo valor de `paid_by_admin`

---

## 🔄 FASE 4: Integración Backend-Frontend

### Flujo Completo: Viaje → Gastos → Nómina

**Escenario:** Un chofer realiza un viaje, carga gastos y se genera su nómina.

**Pasos:**

#### 4.1 Preparación (Backend)

1. **Crear comisión para chofer:**

```http
POST http://localhost:5000/driver-commission/
{
  "driver_id": 1,
  "commission_percentage": 25.00,
  "effective_from": "2026-01-01"
}
```

2. **Crear mínimo garantizado:**

```http
POST http://localhost:5000/minimum-guaranteed/
{
  "driver_id": 1,
  "minimum_guaranteed": 150000.00,
  "effective_from": "2026-01-01"
}
```

3. **Crear período de nómina:**

```http
POST http://localhost:5000/payroll-periods/
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}
```

#### 4.2 Viaje y Gastos (Frontend + Backend)

4. **Crear viaje con tarifa** (Backend o Frontend)
5. **Desde app Flutter:**
   - Cargar gasto 1: Peaje $5000 (pagó contaduría)
   - Cargar gasto 2: Combustible $15000 (pagó chofer)

6. **Completar viaje**

#### 4.3 Generación de Nómina (Backend)

7. **Generar nómina:**

```http
POST http://localhost:5000/payroll-summaries/generate
{
  "period_id": 1,
  "driver_ids": [1],
  "is_manual": false
}
```

**Resultado Esperado:**

```json
{
  "summaries": [
    {
      "driver_id": 1,
      "commission_from_trips": 100000.0,
      "driver_minimum_guaranteed": 50000.0,
      "total_expenses": 15000.0, // Solo combustible (pagó chofer)
      "total_advances": 0,
      "other_items_total": 0,
      "total_net": 135000.0,
      "status": "pending_approval"
    }
  ]
}
```

**Verificación Clave:**

- ✅ `total_expenses` = 15000 (solo gasto con `paid_by_admin: false`)
- ✅ Gasto de peaje ($5000 con `paid_by_admin: true`) NO se incluye
- ✅ `driver_minimum_guaranteed` aplicado correctamente
- ✅ `total_net` = comisión + mínimo - gastos - anticipos + otros

#### 4.4 Agregar Bono y Recalcular

8. **Agregar bono:**

```http
POST http://localhost:5000/payroll-other-items/
{
  "driver_id": 1,
  "period_id": 1,
  "item_type": "bonus",
  "description": "Bono productividad",
  "amount": 25000,
  "date": "2026-01-21",
  "created_by": 1
}
```

9. **Recalcular nómina:**

```http
POST http://localhost:5000/payroll-summaries/{summary_id}/recalculate
```

**Resultado Esperado:**

```json
{
  "new_summary": {
    "other_items_total": 25000.0,
    "total_net": 160000.0, // +25000 del bono
    "status": "pending_approval"
  }
}
```

---

## ✅ Checklist Final de Validación

### Base de Datos

- [ ] Estructura de tablas correcta
- [ ] Datos históricos preservados
- [ ] Tablas nuevas funcionando

### API Backend

- [ ] Crear gasto con `paid_by_admin: true`
- [ ] Crear gasto con `paid_by_admin: false`
- [ ] Crear comisión histórica
- [ ] Crear mínimo garantizado
- [ ] Crear otros conceptos (bonus, fine, etc.)
- [ ] Generar nómina con tarifa → status "pending_approval"
- [ ] Generar nómina sin tarifa → status "error"
- [ ] Recalcular nómina → nueva versión creada

### Frontend Flutter

- [ ] Switch "¿Pagó contaduría?" funciona
- [ ] Gasto con switch ON → `paid_by_admin: true`
- [ ] Gasto con switch OFF → `paid_by_admin: false`
- [ ] Editar gasto preserva campo correctamente

### Integración

- [ ] Flujo completo viaje → gastos → nómina
- [ ] Gastos pagados por admin NO se restan de nómina
- [ ] Gastos pagados por chofer SÍ se restan de nómina
- [ ] Mínimo garantizado se aplica correctamente
- [ ] Otros conceptos suman/restan correctamente
- [ ] Recálculo genera nueva versión

---

## 🐛 Troubleshooting

### Error: "No such column: paid_by_admin"

**Causa:** Migración de BD no completada.
**Solución:**

```bash
python complete_table_migrations.py
```

### Error: "400 Bad Request" al crear gasto

**Causa:** Campo `toll_paid_by` en lugar de `paid_by_admin`.
**Solución:** Verificar que frontend envíe `paid_by_admin`.

### Error: Status "error" en nómina

**Causa:** Viaje sin tarifa configurada.
**Solución:** Configurar tarifa en el viaje antes de generar nómina.

### Error: Nómina con total_expenses = 0

**Causa:** Todos los gastos tienen `paid_by_admin: true`.
**Solución:** Verificar que gastos pagados por chofer tengan `paid_by_admin: false`.

---

## 📊 Casos de Prueba Adicionales

### Caso 1: Viaje sin Tarifa

- Crear viaje sin configurar tarifa
- Generar nómina
- Verificar status "error" con mensaje descriptivo

### Caso 2: Múltiples Comisiones

- Crear comisión 20% vigente desde 01/01/2026
- Crear comisión 25% vigente desde 15/01/2026
- Generar nómina de enero
- Verificar que use 25% (comisión vigente)

### Caso 3: Cambio de Mínimo Garantizado

- Mínimo 150k vigente desde 01/01
- Mínimo 180k vigente desde 15/01
- Generar nómina
- Verificar que use 180k

### Caso 4: Recálculo con Nuevos Gastos

- Generar nómina inicial
- Agregar nuevo gasto
- Recalcular
- Verificar que nuevo gasto se incluya

---

## 📞 Soporte

Si encuentras algún error durante las pruebas:

1. Verificar logs del backend
2. Verificar estructura de BD con `inspect_tables.py`
3. Consultar `MIGRATION_COMPLETED.md`
4. Revisar `FRONTEND_CHANGES_REQUIRED.md`

**Estado de la Migración:** ✅ COMPLETADA
**Fecha:** 21 de enero de 2026
