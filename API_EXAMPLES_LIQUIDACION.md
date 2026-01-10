# Ejemplos de Uso - API de Liquidación de Sueldos

## Configuración Inicial

### 1. Establecer Configuración Global del Sistema

```bash
curl -X PUT http://localhost:5000/api/payroll/settings \
  -H "Content-Type: application/json" \
  -d '{
    "guaranteed_minimum": 150000.00,
    "default_commission_percentage": 18.00,
    "auto_generation_day": 31
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "guaranteed_minimum": "150000.00",
    "default_commission_percentage": "18.00",
    "auto_generation_day": 31,
    "effective_from": "2026-01-09T12:00:00",
    "effective_until": null
  },
  "message": "Configuración actualizada exitosamente"
}
```

### 2. Establecer Comisión de un Chofer

```bash
curl -X POST http://localhost:5000/api/drivers/1/commission \
  -H "Content-Type: application/json" \
  -d '{
    "commission_percentage": 20.00,
    "effective_from": "2026-01-01T00:00:00"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "driver_id": 1,
    "commission_percentage": "20.00",
    "effective_from": "2026-01-01T00:00:00",
    "effective_until": null
  },
  "message": "Comisión establecida exitosamente"
}
```

## Gestión de Períodos

### 3. Crear Período Manualmente

```bash
curl -X POST http://localhost:5000/api/payroll/periods \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2026,
    "month": 1,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  }'
```

### 4. Obtener Período Actual

```bash
curl -X GET http://localhost:5000/api/payroll/periods/current
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "year": 2026,
    "month": 1,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
    "status": "open",
    "has_trips_in_progress": false,
    "actual_close_date": null
  }
}
```

### 5. Listar Todos los Períodos

```bash
curl -X GET "http://localhost:5000/api/payroll/periods?page=1&per_page=20&status=open"
```

### 6. Verificar Viajes en Curso

```bash
curl -X GET http://localhost:5000/api/payroll/periods/1/check-trips
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "has_trips_in_progress": false
  }
}
```

### 7. Cerrar Período

```bash
curl -X POST http://localhost:5000/api/payroll/periods/1/close \
  -H "Content-Type: application/json" \
  -d '{
    "force": false
  }'
```

### 8. Reabrir Período para Ajustes

```bash
curl -X PUT http://localhost:5000/api/payroll/periods/1/reopen
```

## Generación de Liquidaciones

### 9. Generar Resúmenes para Todos los Choferes

```bash
curl -X POST http://localhost:5000/api/payroll/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{
    "period_id": 1,
    "calculation_type": "both",
    "force": false
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "period_id": 1,
      "driver_id": 1,
      "calculation_type": "both",
      "driver_commission_percentage": "20.00",
      "commission_from_trips": "450000.00",
      "expenses_to_reimburse": "25000.00",
      "expenses_to_deduct": "15000.00",
      "guaranteed_minimum_applied": "0.00",
      "advances_deducted": "100000.00",
      "adjustments_applied": "0.00",
      "total_amount": "360000.00",
      "status": "draft"
    }
  ],
  "message": "1 resúmenes generados exitosamente"
}
```

### 10. Generar Resúmenes para Choferes Específicos

```bash
curl -X POST http://localhost:5000/api/payroll/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{
    "period_id": 1,
    "driver_ids": [1, 2, 3],
    "calculation_type": "by_tonnage",
    "force": false
  }'
```

## Consulta de Resúmenes

### 11. Obtener Detalle de un Resumen

```bash
curl -X GET http://localhost:5000/api/payroll/summaries/1
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "id": 1,
      "period_id": 1,
      "driver_id": 1,
      "total_amount": "360000.00",
      "status": "draft"
    },
    "details": [
      {
        "id": 1,
        "detail_type": "trip_commission",
        "trip_id": 5,
        "description": "Viaje CTG 12345678901 - Rosario a Buenos Aires",
        "amount": "150000.00"
      },
      {
        "id": 2,
        "detail_type": "expense_deduct",
        "expense_id": 3,
        "description": "Multa - Exceso de velocidad",
        "amount": "15000.00"
      }
    ]
  }
}
```

### 12. Listar Resúmenes de un Chofer

```bash
curl -X GET "http://localhost:5000/api/payroll/summaries/by-driver/1?page=1&per_page=10"
```

### 13. Listar Resúmenes de un Período

```bash
curl -X GET "http://localhost:5000/api/payroll/summaries/by-period/1?page=1&per_page=20"
```

### 14. Filtrar Resúmenes por Estado

```bash
curl -X GET "http://localhost:5000/api/payroll/summaries?status=approved&page=1"
```

## Aprobación y Exportación

### 15. Aprobar Resumen

```bash
curl -X POST http://localhost:5000/api/payroll/summaries/1/approve \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Aprobado para pago del 10/01/2026"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "approved",
    "notes": "Aprobado para pago del 10/01/2026"
  },
  "message": "Resumen aprobado exitosamente"
}
```

### 16. Exportar a Excel (Borrador para Revisión)

```bash
curl -X POST http://localhost:5000/api/payroll/summaries/1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "excel"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "filepath": "exports/payroll/liquidacion_1_2026_01_20260109_143025.xlsx",
    "format": "excel"
  },
  "message": "Resumen exportado a Excel exitosamente"
}
```

### 17. Exportar a PDF (Solo si está Aprobado)

```bash
curl -X POST http://localhost:5000/api/payroll/summaries/1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "filepath": "exports/payroll/liquidacion_1_2026_01_20260109_143530.pdf",
    "format": "pdf"
  },
  "message": "Resumen exportado a PDF exitosamente"
}
```

### 18. Descargar Archivo Exportado

```bash
curl -X GET http://localhost:5000/api/payroll/summaries/1/download \
  --output liquidacion.xlsx
```

## Ajustes Retroactivos

### 19. Crear Ajuste Manual

```bash
curl -X POST http://localhost:5000/api/payroll/adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "origin_period_id": 1,
    "driver_id": 1,
    "amount": 5000.00,
    "description": "Bono por desempeño excepcional",
    "adjustment_type": "manual",
    "created_by": 1
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "origin_period_id": 1,
    "driver_id": 1,
    "amount": "5000.00",
    "description": "Bono por desempeño excepcional",
    "adjustment_type": "manual",
    "is_applied": "pending"
  },
  "message": "Ajuste creado exitosamente"
}
```

### 20. Crear Ajuste por Corrección de Viaje

```bash
curl -X POST http://localhost:5000/api/payroll/adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "origin_period_id": 1,
    "driver_id": 1,
    "trip_id": 5,
    "amount": -3000.00,
    "description": "Corrección por error en toneladas del viaje CTG 12345",
    "adjustment_type": "trip_correction",
    "created_by": 1
  }'
```

### 21. Listar Ajustes Pendientes de un Chofer

```bash
curl -X GET http://localhost:5000/api/payroll/adjustments/pending/1
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "origin_period_id": 1,
      "driver_id": 1,
      "amount": "5000.00",
      "description": "Bono por desempeño excepcional",
      "is_applied": "pending"
    }
  ]
}
```

### 22. Actualizar Ajuste Pendiente

```bash
curl -X PUT http://localhost:5000/api/payroll/adjustments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 7000.00,
    "description": "Bono actualizado por desempeño excepcional"
  }'
```

### 23. Eliminar Ajuste Pendiente

```bash
curl -X DELETE http://localhost:5000/api/payroll/adjustments/1
```

### 24. Listar Todos los Ajustes con Filtros

```bash
curl -X GET "http://localhost:5000/api/payroll/adjustments?origin_period_id=1&driver_id=1&is_applied=pending"
```

## Consulta de Comisiones

### 25. Obtener Comisión Actual de un Chofer

```bash
curl -X GET http://localhost:5000/api/drivers/1/commission/current
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "driver_id": 1,
    "commission_percentage": "20.00"
  }
}
```

### 26. Obtener Historial de Comisión de un Chofer

```bash
curl -X GET http://localhost:5000/api/drivers/1/commission/history
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "driver_id": 1,
      "commission_percentage": "20.00",
      "effective_from": "2026-01-01T00:00:00",
      "effective_until": null
    },
    {
      "id": 1,
      "driver_id": 1,
      "commission_percentage": "18.00",
      "effective_from": "2025-01-01T00:00:00",
      "effective_until": "2026-01-01T00:00:00"
    }
  ]
}
```

## Consulta de Configuración

### 27. Obtener Configuración Actual

```bash
curl -X GET http://localhost:5000/api/payroll/settings
```

### 28. Ver Historial de Configuraciones

```bash
curl -X GET "http://localhost:5000/api/payroll/settings/history?page=1&per_page=10"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "guaranteed_minimum": "150000.00",
      "default_commission_percentage": "18.00",
      "auto_generation_day": 31,
      "effective_from": "2026-01-09T12:00:00",
      "effective_until": null
    },
    {
      "id": 1,
      "guaranteed_minimum": "120000.00",
      "default_commission_percentage": "18.00",
      "auto_generation_day": 31,
      "effective_from": "2025-01-01T00:00:00",
      "effective_until": "2026-01-09T12:00:00"
    }
  ]
}
```

## Escenarios Completos

### Escenario 1: Liquidación Mensual Completa

```bash
# 1. Obtener período actual
curl -X GET http://localhost:5000/api/payroll/periods/current

# 2. Verificar que no haya viajes en curso
curl -X GET http://localhost:5000/api/payroll/periods/1/check-trips

# 3. Generar resúmenes
curl -X POST http://localhost:5000/api/payroll/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{"period_id": 1, "calculation_type": "both", "force": false}'

# 4. Exportar a Excel para revisión
curl -X POST http://localhost:5000/api/payroll/summaries/1/export \
  -H "Content-Type: application/json" \
  -d '{"format": "excel"}'

# 5. Aprobar resumen
curl -X POST http://localhost:5000/api/payroll/summaries/1/approve \
  -H "Content-Type: application/json" \
  -d '{"notes": "Aprobado"}'

# 6. Exportar a PDF
curl -X POST http://localhost:5000/api/payroll/summaries/1/export \
  -H "Content-Type: application/json" \
  -d '{"format": "pdf"}'

# 7. Cerrar período
curl -X POST http://localhost:5000/api/payroll/periods/1/close \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### Escenario 2: Corrección con Ajuste Retroactivo

```bash
# 1. Crear ajuste para período cerrado
curl -X POST http://localhost:5000/api/payroll/adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "origin_period_id": 1,
    "driver_id": 1,
    "amount": -5000.00,
    "description": "Corrección por error en cálculo de peajes",
    "adjustment_type": "manual",
    "created_by": 1
  }'

# 2. Generar liquidación del período siguiente (el ajuste se aplicará automáticamente)
curl -X POST http://localhost:5000/api/payroll/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{"period_id": 2, "calculation_type": "both"}'

# 3. Verificar que el ajuste aparece en el detalle
curl -X GET http://localhost:5000/api/payroll/summaries/2
```

## Manejo de Errores

### Error: Período con Viajes en Curso
```json
{
  "success": false,
  "message": "Hay viajes en curso en el período. Complete los viajes o use force=True"
}
```

### Error: Resumen Ya Aprobado
```json
{
  "success": false,
  "message": "El resumen para el chofer Juan Pérez ya está aprobado. No se puede regenerar."
}
```

### Error: Exportar PDF sin Aprobar
```json
{
  "success": false,
  "message": "Solo se pueden exportar a PDF resúmenes aprobados"
}
```

### Error: Modificar Ajuste Aplicado
```json
{
  "success": false,
  "message": "No se puede modificar un ajuste ya aplicado"
}
```
