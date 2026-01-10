# Módulo de Liquidación de Sueldos - SGFCP

## Descripción General

El módulo de liquidación de sueldos automatiza el cálculo y gestión de los pagos mensuales a los choferes, incluyendo comisiones por viajes, gastos, adelantos y ajustes retroactivos.

## Arquitectura del Módulo

### Modelos de Datos

#### 1. PayrollPeriod
Períodos de liquidación mensuales.
- **Campos principales**: year, month, start_date, end_date, status, has_trips_in_progress
- **Estados**: open, closed, with_adjustments
- **Funcionalidad**: Se pospone el cierre si hay viajes en curso

#### 2. PayrollSummary
Resumen de liquidación por chofer en un período.
- **Campos de cálculo**: 
  - commission_from_trips
  - expenses_to_reimburse
  - expenses_to_deduct
  - guaranteed_minimum_applied
  - advances_deducted
  - adjustments_applied
  - total_amount
- **Estados**: draft, approved, paid
- **Tipos de cálculo**: by_tonnage, by_km, both

#### 3. PayrollDetail
Detalle de cada concepto del cálculo (viajes, gastos, adelantos, ajustes).
- Almacena referencias a trips, expenses, advances o adjustments
- Incluye descripción y datos del cálculo en JSON

#### 4. PayrollAdjustment
Ajustes retroactivos a períodos cerrados.
- Se aplican automáticamente en el próximo cálculo
- Pueden ser manuales o automáticos (por gastos post-cierre)

#### 5. PayrollSettings
Configuración global historizada.
- Mínimo garantizado
- Porcentaje de comisión por defecto
- Día de generación automática

#### 6. DriverCommissionHistory
Historial de porcentajes de comisión por chofer.
- Permite historizar cambios en la comisión del chofer
- Se usa el porcentaje vigente al cierre del período

## Fórmula de Cálculo

```
Liquidación = comision_viajes + gastos_reintegrar + minimo_garantizado + ajustes - gastos_descontar - adelantos
```

Donde:
- **comision_viajes** = Base de viajes * % comisión del chofer
- **Base de viajes** = Σ(toneladas × tarifa) + Σ(km × tarifa_km)
- **gastos_reintegrar** = Reparaciones + Combustible sin vale + Peajes + Gastos extraordinarios (pagados por chofer)
- **gastos_descontar** = Multas
- **minimo_garantizado** = max(0, mínimo_config - comision_viajes)
- **adelantos** = Suma de adelantos del período

## Endpoints Principales

### Períodos de Liquidación

```
POST   /api/payroll/periods                    # Crear período
GET    /api/payroll/periods                    # Listar períodos
GET    /api/payroll/periods/{id}               # Obtener período
GET    /api/payroll/periods/current            # Período actual
POST   /api/payroll/periods/{id}/close         # Cerrar período
PUT    /api/payroll/periods/{id}/reopen        # Reabrir para ajustes
GET    /api/payroll/periods/{id}/check-trips   # Verificar viajes en curso
```

### Resúmenes de Liquidación

```
POST   /api/payroll/summaries/generate         # Generar resúmenes
GET    /api/payroll/summaries                  # Listar resúmenes
GET    /api/payroll/summaries/{id}             # Detalle del resumen
POST   /api/payroll/summaries/{id}/approve     # Aprobar resumen
POST   /api/payroll/summaries/{id}/export      # Exportar a Excel/PDF
GET    /api/payroll/summaries/{id}/download    # Descargar archivo
GET    /api/payroll/summaries/by-driver/{id}   # Resúmenes de un chofer
GET    /api/payroll/summaries/by-period/{id}   # Resúmenes de un período
```

### Ajustes Retroactivos

```
POST   /api/payroll/adjustments                # Crear ajuste
GET    /api/payroll/adjustments                # Listar ajustes
GET    /api/payroll/adjustments/{id}           # Obtener ajuste
PUT    /api/payroll/adjustments/{id}           # Actualizar ajuste
DELETE /api/payroll/adjustments/{id}           # Eliminar ajuste
GET    /api/payroll/adjustments/pending/{id}   # Ajustes pendientes de un chofer
```

### Configuración

```
GET    /api/payroll/settings                   # Configuración actual
PUT    /api/payroll/settings                   # Actualizar configuración
GET    /api/payroll/settings/history           # Historial de configuraciones
```

### Comisión de Choferes

```
POST   /api/drivers/{id}/commission            # Establecer comisión
GET    /api/drivers/{id}/commission/current    # Comisión actual
GET    /api/drivers/{id}/commission/history    # Historial de comisión
```

## Flujo de Uso

### 1. Configuración Inicial
```bash
# Establecer configuración global
PUT /api/payroll/settings
{
  "guaranteed_minimum": 150000.00,
  "default_commission_percentage": 18.00,
  "auto_generation_day": 31
}

# Establecer comisión específica para un chofer
POST /api/drivers/1/commission
{
  "commission_percentage": 20.00,
  "effective_from": "2026-01-01T00:00:00"
}
```

### 2. Generación de Resúmenes
```bash
# Generar resúmenes para el período actual
# Incluye SOLO viajes finalizados. Los viajes en curso se aplicarán como ajustes.
POST /api/payroll/summaries/generate
{
  "period_id": 1,
  "calculation_type": "both",
  "driver_ids": [1, 2, 3]  # Opcional: null para todos los choferes
}
```

### 3. Revisión y Aprobación
```bash
# Ver detalle del resumen
GET /api/payroll/summaries/1

# Exportar a Excel para revisión
POST /api/payroll/summaries/1/export
{
  "format": "excel"
}

# Aprobar resumen
POST /api/payroll/summaries/1/approve
{
  "notes": "Aprobado para pago"
}

# Exportar a PDF
POST /api/payroll/summaries/1/export
{
  "format": "pdf"
}
```

### 4. Ajustes Retroactivos
```bash
# Crear ajuste manual
POST /api/payroll/adjustments
{
  "origin_period_id": 1,
  "driver_id": 1,
  "amount": 5000.00,
  "description": "Bono por desempeño",
  "adjustment_type": "manual"
}
```

### 5. Cierre de Período
```bash
# Verificar viajes en curso
GET /api/payroll/periods/1/check-trips

# Cerrar período
POST /api/payroll/periods/1/close
{
  "force": false
}
```

## Reglas de Negocio Implementadas

### Gastos
- **Multas**: Se descuentan 100%
- **Reparaciones**: Se reintegran si las pagó el chofer
- **Combustible**: Se reintegra si fue sin vale
- **Peajes**: Se reintegran si los pagó el chofer
- **Gastos extraordinarios**: Se reintegran 100%

### Períodos
- Los períodos se pueden cerrar solo cuando todos los viajes estén finalizados
- La generación de liquidaciones incluye SOLO viajes finalizados del período
- Los viajes iniciados en el período pero no finalizados generan ajustes retroactivos automáticos
- Los datos de períodos cerrados no se pueden modificar directamente
- Los ajustes retroactivos se aplican automáticamente en el próximo cálculo

### Comisiones
- Se historiza el porcentaje de comisión del chofer
- Se usa el porcentaje vigente al final del período
- El mínimo garantizado se aplica solo si la comisión es inferior

### Exportación
- Excel: Se puede generar en cualquier estado (para revisión)
- PDF: Solo se puede generar si el resumen está aprobado

## Migraciones de Base de Datos

Para crear las tablas nuevas, ejecutar:

```bash
python migrate_db.py
```

O usar las migraciones de SQLAlchemy si están configuradas.

## Dependencias Adicionales

Las siguientes librerías fueron agregadas al proyecto:
- `openpyxl==3.1.2`: Para exportación a Excel
- `reportlab==4.0.7`: Para exportación a PDF
- `python-dateutil==2.8.2`: Para manejo de fechas

Instalar con:
```bash
pip install -r requirements.txt
```

## Consideraciones de Seguridad

- [ ] Implementar autenticación JWT para todos los endpoints
- [ ] Validar permisos de usuario (solo admins pueden generar/aprobar)
- [ ] Los choferes solo deberían ver sus propios resúmenes
- [ ] Auditoría de cambios en ajustes y aprobaciones

## Generación Automática (Por Implementar)

### Requisitos de Negocio
- Las liquidaciones deben generarse automáticamente el último día de cada mes
- Si hay viajes en curso, se generan con los viajes finalizados
- Los viajes que finalicen después generarán ajustes retroactivos automáticos

### Implementación Sugerida con APScheduler

```python
# En app/__init__.py agregar:
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def auto_generate_payroll():
    """Tarea programada para generar liquidaciones automáticamente."""
    with app.app_context():
        from app.controllers.payroll_calculation import PayrollCalculationController
        from app.controllers.payroll_period import PayrollPeriodController
        
        # Obtener período actual
        period = PayrollPeriodController.get_current_period()
        
        # Generar para todos los choferes
        PayrollCalculationController.generate_summaries(
            period_id=period.id,
            calculation_type='both'
        )

# Configurar scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=auto_generate_payroll,
    trigger=CronTrigger(day='last', hour=23, minute=59),  # Último día del mes a las 23:59
    id='auto_payroll',
    name='Generación automática de liquidaciones',
    replace_existing=True
)
scheduler.start()
```

**Dependencias necesarias:**
```bash
pip install apscheduler
```

## Mejoras Futuras

1. **Implementar la generación automática**: Usar APScheduler según el ejemplo anterior
2. **Notificaciones**: Enviar notificaciones a choferes cuando se aprueba su liquidación
3. **Firma Digital**: Agregar firma digital a PDFs aprobados
4. **Dashboard**: Visualización de estadísticas de liquidaciones
5. **Validaciones**: Agregar más validaciones de integridad de datos
6. **Reportes**: Reportes consolidados por período o comparativos entre períodos

## Testing

### Preparación del Entorno

#### 1. Crear las tablas en la base de datos
```bash
python setup_db.py
```
Este comando crea todas las tablas incluyendo las nuevas del módulo de liquidación.

#### 2. Iniciar el servidor backend
```bash
python run.py
```
El servidor debe estar corriendo en http://localhost:5000

#### 3. Acceder a la interfaz de prueba
Abrir en el navegador:
```
file:///C:/Proyecto Final/backend-SGFCP/trip_management.html
```

#### 4. Iniciar sesión como administrador
- Email: admin@sgfcp.com
- Password: admin123
- Verificar que aparece la pestaña "⚙️ Liquidación"

---

### CASO DE PRUEBA 1: Configuración Inicial

**Objetivo**: Configurar parámetros globales del módulo de liquidación

**Pasos**:
1. Hacer clic en la pestaña "⚙️ Liquidación"
2. En la sección "Configuración de Liquidación":
   - **Mínimo Garantizado**: Ingresar `80000`
   - **Comisión Por Defecto (%)**: Ingresar `60`
3. Hacer clic en "Guardar Configuración"

**Resultado Esperado**:
- ✅ Mensaje de confirmación: "Configuración actualizada correctamente"
- Los valores quedan guardados para futuros cálculos

**Verificación**: Los valores se guardan en la tabla `payroll_settings` con `effective_from` = fecha actual

---

### CASO DE PRUEBA 2: Crear Período de Liquidación

**Objetivo**: Abrir un nuevo período mensual para liquidaciones

**Pasos**:
1. En la sección "Gestión de Períodos", hacer clic en "Crear Período Actual"
2. Observar la información del período creado

**Resultado Esperado**:
- ✅ Se muestra información del período:
  - 🟢 Período 2026-01
  - Estado: open
  - Inicio: 2026-01-01
  - Fin: 2026-01-31
  - Viajes en curso: No
- ✅ Aparece botón "Cerrar Período"

**Verificación**: El período se guarda en la tabla `payroll_period` con status='open'

---

### CASO DE PRUEBA 3: Crear Viajes para el Período

**Objetivo**: Crear viajes que serán liquidados

**Pasos**:
1. Ir a la pestaña "Administración"
2. Crear un nuevo viaje:
   - Cliente: Seleccionar cualquiera
   - Choferes: Seleccionar chofer (ej: Juan Pérez)
   - Origen: Buenos Aires
   - Destino: Córdoba
   - Tipo de Carga: Granos
   - Toneladas: `25`
   - Tarifa: `5000` (comisión será 25 × 5000 × 60% = 75,000)
   - Fecha: Dentro del período actual (enero 2026)
3. Hacer clic en "Crear Viaje"
4. En la lista, hacer clic en "▶️ Iniciar Viaje"
5. Completar datos de inicio:
   - Dueño de la Carga: Seleccionar cualquiera
   - Km Iniciales: `100000`
   - Hacer clic en "Iniciar"
6. Hacer clic en "✅ Finalizar"
7. Completar datos de finalización:
   - Km Finales: `101000` (1000 km recorridos)
   - Hacer clic en "Finalizar Viaje"

**Resultado Esperado**:
- ✅ Viaje queda en estado "Finalizado"
- Listo para ser incluido en la liquidación

---

### CASO DE PRUEBA 4: Crear Gastos Reembolsables

**Objetivo**: Agregar gastos que el chofer debe recuperar

**Pasos**:
1. En el viaje finalizado, hacer clic en "📊 Ver Gastos"
2. Agregar gasto de combustible:
   - Tipo: Combustible
   - Monto: `15000`
   - Descripción: "Carga combustible ruta"
   - Hacer clic en "Guardar"
3. Agregar gasto de peaje:
   - Tipo: Peaje
   - Monto: `2500`
   - Descripción: "Peajes Buenos Aires-Córdoba"
   - Hacer clic en "Guardar"

**Resultado Esperado**:
- ✅ Los gastos quedan asociados al viaje
- Combustible y peaje son gastos reembolsables (se suman en la liquidación)

---

### CASO DE PRUEBA 5: Crear Gastos Deducibles (Multas)

**Objetivo**: Agregar gastos que se descuentan al chofer

**Pasos**:
1. En el mismo viaje o en otro, agregar:
   - Tipo: Multa
   - Monto: `5000`
   - Descripción: "Multa por exceso de velocidad"
   - Hacer clic en "Guardar"

**Resultado Esperado**:
- ✅ El gasto se registra
- Las multas se deducen en la liquidación

---

### CASO DE PRUEBA 6: Crear Adelantos al Chofer

**Objetivo**: Registrar adelantos que se descontarán en la liquidación

**Requisito**: Debe existir el módulo de adelantos implementado

**Pasos**:
1. Ir a "Gestión de Adelantos" (si está implementado)
2. Crear adelanto:
   - Chofer: Juan Pérez
   - Monto: `20000`
   - Fecha: Dentro del período actual
   - Estado: approved

**Resultado Esperado**:
- ✅ El adelanto queda registrado
- Se descontará automáticamente de la liquidación

**Alternativa**: Si no existe el módulo, insertar directamente en la base de datos:
```sql
INSERT INTO advance_payment (driver_id, amount, request_date, status, approved_date)
VALUES (1, 20000.0, '2026-01-15', 'approved', '2026-01-15');
```

---

### CASO DE PRUEBA 7: Generar Liquidación Borrador

**Objetivo**: Calcular la liquidación del período

**Pasos**:
1. Volver a la pestaña "⚙️ Liquidación"
2. En "Generar Liquidaciones":
   - Período: Seleccionar "2026-01 (open)"
   - Tipo de Cálculo: Seleccionar "both" (tonelada y km)
3. Hacer clic en "Generar Liquidaciones"
4. Esperar mensaje de confirmación

**Nota**: Solo se incluyen viajes finalizados. Si hay viajes en curso del período, se aplicarán como ajustes cuando se finalicen.

**Resultado Esperado**:
- ✅ Mensaje: "Liquidaciones generadas exitosamente"
- En "Liquidaciones Generadas" aparece una tarjeta con:
  - 🟡 Liquidación #1
  - Período: 1 | Chofer: ID 1
  - Tipo: both
  - Comisión viajes: $75,000.00
  - Total a pagar: **$92,500.00** (aproximado)

**Cálculo Esperado**:
```
Comisión = 25 ton × $5000 × 60% = $75,000
Gastos a reembolsar = $15,000 (combustible) + $2,500 (peaje) = $17,500
Gastos a deducir = $5,000 (multa)
Adelantos = $20,000

Total = $75,000 + $17,500 - $5,000 - $20,000 = $67,500
(Si es menor al mínimo garantizado de $80,000, se aplica el mínimo)
Total final = $80,000
```

---

### CASO DE PRUEBA 8: Ver Detalle de Liquidación

**Objetivo**: Revisar el desglose completo del cálculo

**Pasos**:
1. En la tarjeta de la liquidación, hacer clic en "👁️ Detalle"

**Resultado Esperado**:
- ✅ Aparece ventana con detalle:
  - Total: $80,000.00 (o el calculado)
  - Lista de conceptos:
    - Comisión viaje #1: $75,000.00
    - Reembolso combustible: $15,000.00
    - Reembolso peaje: $2,500.00
    - Deducción multa: -$5,000.00
    - Adelanto: -$20,000.00
    - Mínimo garantizado aplicado: $12,500.00 (si corresponde)

---

### CASO DE PRUEBA 9: Exportar a Excel (Borrador)

**Objetivo**: Generar archivo Excel con la liquidación en borrador

**Pasos**:
1. En la tarjeta de la liquidación (estado 🟡 draft), hacer clic en "📊 Excel"

**Resultado Esperado**:
- ✅ Mensaje: "Exportado a EXCEL: exports/payroll/liquidacion_X.xlsx"
- El archivo se genera en la carpeta `exports/payroll/`
- Abrir el archivo Excel:
  - Contiene encabezado con período y chofer
  - Tabla con desglose de conceptos
  - Total calculado
  - Formato con colores y estilos

---

### CASO DE PRUEBA 10: Aprobar Liquidación

**Objetivo**: Cambiar estado de borrador a aprobado

**Pasos**:
1. En la tarjeta de la liquidación (estado 🟡 draft), hacer clic en "Aprobar"
2. Confirmar la aprobación

**Resultado Esperado**:
- ✅ Mensaje: "Liquidación aprobada"
- El estado cambia a 🟢 approved
- Ahora aparece botón "📄 PDF"

---

### CASO DE PRUEBA 11: Exportar a PDF (Aprobada)

**Objetivo**: Generar PDF oficial de la liquidación aprobada

**Pasos**:
1. En la tarjeta de la liquidación (estado 🟢 approved), hacer clic en "📄 PDF"

**Resultado Esperado**:
- ✅ Mensaje: "Exportado a PDF: exports/payroll/liquidacion_X.pdf"
- El archivo se genera en la carpeta `exports/payroll/`
- Abrir el PDF:
  - Documento profesional con encabezado
  - Información del chofer y período
  - Tabla detallada de conceptos
  - Total a pagar destacado
  - Fecha de aprobación

---

### CASO DE PRUEBA 12: Cerrar Período

**Objetivo**: Cerrar el período mensual después de aprobar liquidaciones

**Pasos**:
1. En "Gestión de Períodos", hacer clic en "Cerrar Período"
2. Confirmar el cierre

**Resultado Esperado**:
- ✅ Mensaje: "Período cerrado correctamente"
- El estado cambia a 🔴 closed
- Ya no se puede modificar el período
- El botón "Cerrar Período" desaparece

---

### CASO DE PRUEBA 13: Agregar Gasto a Período Cerrado

**Objetivo**: Verificar que se genera un ajuste automático

**Pasos**:
1. Ir a la pestaña "Viajes"
2. Buscar un viaje del período cerrado
3. Agregar un nuevo gasto:
   - Tipo: Reparación
   - Monto: `8000`
   - Descripción: "Reparación olvidada"
   - Guardar

**Resultado Esperado**:
- ✅ El gasto se registra
- En la base de datos se crea automáticamente un ajuste en `payroll_adjustments`:
  - `origin_period_id` = período cerrado
  - `amount` = 8000
  - `adjustment_type` = 'expense_post_close'
  - `is_applied` = false (pendiente de aplicar)

**Verificación SQL**:
```sql
SELECT * FROM payroll_adjustments WHERE adjustment_type = 'expense_post_close';
```

---

### CASO DE PRUEBA 14: Crear Ajuste Retroactivo Manual

**Objetivo**: Crear un ajuste manual a un período cerrado

**Pasos**:
1. En la pestaña "⚙️ Liquidación"
2. Ir a "Crear Ajuste Retroactivo"
3. Completar:
   - Período: Seleccionar el período cerrado
   - Chofer: Seleccionar chofer (ej: Juan Pérez)
   - Monto: `5000` (positivo = a favor del chofer)
   - Tipo: manual
   - Descripción: "Bonificación por desempeño"
4. Hacer clic en "Crear Ajuste"

**Resultado Esperado**:
- ✅ Mensaje: "Ajuste creado correctamente"
- El ajuste se guarda con `is_applied` = false

---

### CASO DE PRUEBA 15: Aplicar Ajustes en Siguiente Período

**Objetivo**: Verificar que los ajustes se incluyen automáticamente en el próximo cálculo

**Pasos**:
1. Crear nuevo período (febrero 2026):
   - Hacer clic en "Crear Período Actual"
2. Crear al menos un viaje finalizado para el mismo chofer en febrero
3. Generar liquidación para febrero:
   - Período: 2026-02
   - Tipo: both
   - Generar
4. Ver el detalle de la liquidación generada

**Resultado Esperado**:
- ✅ En el detalle aparecen los ajustes:
  - "Ajuste retroactivo: Reparación olvidada": $8,000.00
  - "Ajuste retroactivo: Bonificación por desempeño": $5,000.00
- El total incluye estos $13,000 adicionales
- Los ajustes cambian `is_applied` = true y `applied_in_period_id` = febrero

**Verificación del Total**:
```
Total Febrero = Comisiones + Gastos - Adelantos + $13,000 (ajustes)
```

---

### CASO DE PRUEBA 16: Regenerar Liquidaciones

**Objetivo**: Recalcular una liquidación ya generada (por ejemplo, después de finalizar más viajes)

**Pasos**:
1. Finalizar un nuevo viaje del mismo período
2. En "Generar Liquidaciones":
   - Período: Seleccionar el mismo período
   - Tipo: both
3. Hacer clic en "Generar Liquidaciones"

**Resultado Esperado**:
- ✅ Las liquidaciones en estado 'draft' se eliminan y regeneran
- ✅ Las liquidaciones 'approved' NO se pueden regenerar
- Aparecen las nuevas liquidaciones con el viaje adicional incluido

**Nota**: Solo se pueden regenerar liquidaciones en estado 'draft'

---

### CASO DE PRUEBA 17: Generar con Viajes en Curso

**Objetivo**: Validar que se pueden generar liquidaciones con viajes en curso

**Pasos**:
1. Crear un viaje e iniciarlo (dejarlo en estado "En curso")
2. Generar liquidaciones para el período actual

**Resultado Esperado**:
- ✅ Las liquidaciones se generan exitosamente
- ✅ El viaje en curso NO se incluye en el cálculo
- ℹ️ El sistema marca que hay viajes en curso
- Cuando se finalice ese viaje, se generará un ajuste retroactivo automático

---

### CASO DE PRUEBA 17.1: Cerrar Período con Viajes en Curso

**Objetivo**: Validar que no se puede cerrar con viajes activos

**Pasos**:
1. Con el viaje anterior aún en curso, intentar cerrar el período

**Resultado Esperado**:
- ❌ Mensaje de error: "No se puede cerrar el período mientras haya viajes en curso"
- El período permanece abierto
- Se debe finalizar el viaje primero antes de cerrar el período

---

### CASO DE PRUEBA 18: Mínimo Garantizado

**Objetivo**: Verificar que se aplica el mínimo cuando el cálculo es menor

**Pasos**:
1. Configurar mínimo garantizado = $80,000
2. Crear un viaje pequeño:
   - Toneladas: 5
   - Tarifa: $3000
   - Comisión = 5 × $3000 × 60% = $9,000
3. Sin gastos ni adelantos
4. Generar liquidación

**Resultado Esperado**:
- ✅ Comisión viajes: $9,000.00
- ✅ Total a pagar: **$80,000.00** (se aplicó el mínimo)
- En el detalle aparece: "Mínimo garantizado aplicado: $71,000.00"

---

### CASO DE PRUEBA 19: Cambiar Comisión de Chofer

**Objetivo**: Modificar el porcentaje de comisión individual

**Requisito**: Endpoint para actualizar comisión de chofer

**Pasos API** (usando curl o Postman):
```bash
curl -X POST http://localhost:5000/api/driver-commission/history \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": 1,
    "commission_percentage": 70,
    "effective_from": "2026-02-01"
  }'
```

**Resultado Esperado**:
- ✅ Se crea registro en `driver_commission_history`
- A partir de febrero, el chofer tiene 70% de comisión en lugar de 60%

**Verificación**: Generar liquidación de febrero y verificar que usa 70%

---

### CASO DE PRUEBA 20: Liquidación por KM

**Objetivo**: Probar cálculo basado en kilómetros

**Pasos**:
1. Crear un viaje con `km_rate` definido:
   - Tarifa por KM: $50
   - Km recorridos: 1000 (km finales - km iniciales)
   - Comisión = 1000 × $50 × 60% = $30,000
2. Generar liquidación con tipo "by_km"

**Resultado Esperado**:
- ✅ Comisión se calcula solo por kilómetros
- Total incluye $30,000 de comisión + gastos - adelantos

---

### Verificación en Base de Datos

Para validar que todo funciona correctamente, ejecutar estas queries:

```sql
-- Ver todos los períodos
SELECT * FROM payroll_period;

-- Ver liquidaciones generadas
SELECT * FROM payroll_summary;

-- Ver detalles de una liquidación
SELECT * FROM payroll_detail WHERE payroll_summary_id = 1;

-- Ver ajustes pendientes
SELECT * FROM payroll_adjustments WHERE is_applied = 0;

-- Ver configuración actual
SELECT * FROM payroll_settings WHERE effective_until IS NULL;

-- Ver historial de comisiones de choferes
SELECT * FROM driver_commission_history;
```

---

### Casos de Error Esperados

| Acción | Error Esperado |
|--------|----------------|
| Generar liquidación sin crear período | "No existe un período abierto" |
| Cerrar período con viajes en curso | "No se puede cerrar el período mientras haya viajes en curso" |
| Aprobar liquidación ya aprobada | "La liquidación ya está aprobada" |
| Regenerar liquidación aprobada | "El resumen ya está aprobado. No se puede regenerar" |
| Exportar PDF de borrador | "Solo se pueden exportar a PDF liquidaciones aprobadas" |
| Crear período duplicado (mismo mes/año) | "Ya existe un período para este mes y año" |
| Crear ajuste para período abierto | "Solo se pueden crear ajustes para períodos cerrados" |

---

### Resumen de Funcionalidades Probadas

✅ Configuración global de liquidación  
✅ Creación y gestión de períodos  
✅ Cálculo de comisiones por tonelada  
✅ Cálculo de comisiones por kilómetro  
✅ Cálculo mixto (both)  
✅ Reembolso de gastos  
✅ Deducción de multas  
✅ Deducción de adelantos  
✅ Aplicación de mínimo garantizado  
✅ Generación de borradores  
✅ Aprobación de liquidaciones  
✅ Exportación a Excel  
✅ Exportación a PDF  
✅ Cierre de períodos  
✅ Ajustes retroactivos manuales  
✅ Ajustes automáticos por gastos post-cierre  
✅ Aplicación de ajustes en próximo período  
✅ Historización de comisiones de choferes  
✅ Validaciones de integridad

## Contacto y Soporte

Para dudas sobre la implementación, revisar el código en:
- Controladores: `/app/controllers/payroll_*.py`
- Modelos: `/app/models/payroll_*.py`, `driver_commission_history.py`
- Rutas: `/app/routes/payroll_*.py`, `driver_commission.py`
- Schemas: `/app/schemas/payroll.py`
