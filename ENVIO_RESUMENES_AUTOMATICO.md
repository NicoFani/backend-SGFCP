# Envío Automático de Resúmenes de Liquidación

## Descripción

El sistema ahora envía automáticamente un email con los resúmenes de liquidación generados al final de cada período.

## Funcionamiento

### Generación Automática de Resúmenes

Al finalizar cada período (último día del mes a las 23:59), el sistema:

1. **Genera resúmenes** para todos los choferes activos
2. **Clasifica los resúmenes** según su estado:
   - `pending_approval`: Listo para aprobación (sin errores ni viajes pendientes)
   - `calculation_pending`: Esperando finalización de viajes en curso
   - `error`: Con errores de cálculo (ej: viajes sin tarifa)
   - `draft`: Borrador (otros casos)

3. **Exporta a Excel** los resúmenes en estado `pending_approval`
4. **Envía un email** a contabilidad con:
   - Archivos Excel adjuntos de resúmenes listos para aprobar
   - Lista detallada de resúmenes en espera o con errores
   - Resumen total de la generación

### Contenido del Email

El email incluye:

#### ✓ Resúmenes Listos para Aprobación

- Tabla con ID, Chofer y Total de cada resumen
- **Excel adjunto** de cada resumen listo para aprobar
- Estos pueden ser aprobados inmediatamente

#### ⏳ Resúmenes en Espera (calculation_pending)

- Lista de choferes con viajes en curso
- Motivo de la espera
- Se calcularán automáticamente cuando finalicen los viajes

#### ⚠ Resúmenes con Error

- Lista de choferes con errores de cálculo
- Descripción del error
- Requieren atención manual

#### Resumen Total

- Cantidad de resúmenes en cada estado
- Total de resúmenes generados

## Configuración

Las siguientes variables de entorno deben estar configuradas en el archivo `.env`:

```env
# Brevo (Sendinblue) Email Configuration
BREVO_API_KEY=tu_api_key_de_brevo
BREVO_SENDER_EMAIL=email@tuempresa.com
BREVO_SENDER_NAME=Nombre de tu Empresa
BREVO_ACCOUNTING_RECIPIENTS=contabilidad@tuempresa.com,admin@tuempresa.com
```

### Múltiples Destinatarios

Para enviar a múltiples destinatarios, separa los emails con comas:

```env
BREVO_ACCOUNTING_RECIPIENTS=email1@empresa.com,email2@empresa.com,email3@empresa.com
```

## Archivos Exportados

Los archivos Excel se guardan en: `exports/payroll/`

Formato del nombre: `Liquidacion_{Estado}_{NombreChofer}_{Periodo}.xlsx`

Ejemplo: `Liquidacion_PendienteAprobacion_Juan_Perez_02-2026.xlsx`

## Modo de Prueba (SIMULACIÓN)

Actualmente el sistema está en modo simulación:

- **Ejecuta**: 30 segundos después de iniciar el servidor
- **Simula**: Período que termina el 28/02/2026

### Para Producción

Editar `app/scheduler.py`:

1. Comentar el bloque de SIMULACIÓN
2. Descomentar el bloque de producción (cron)
3. Cambiar la fecha simulada por `datetime.now().date()`

```python
# Cambiar de:
today = date(2026, 2, 28)  # SIMULACIÓN

# A:
today = datetime.now().date()
```

## Logs

El sistema registra en los logs:

- Generación de resúmenes por período
- Estado de cada resumen generado
- Exportación de Excel
- Envío de emails (éxito o error)

Revisar logs para verificar el correcto funcionamiento.

## Recálculo Automático

Los resúmenes en estado `calculation_pending`:

1. Se recalculan automáticamente al finalizar los viajes
2. No requieren intervención manual
3. Una vez calculados, pasan a `pending_approval` o `error`

## Solución de Problemas

### Email no se envía

- Verificar variables de entorno de Brevo
- Revisar logs para mensajes de error
- Confirmar que BREVO_ACCOUNTING_RECIPIENTS tiene emails válidos

### Excel no se adjunta

- Verificar permisos de escritura en `exports/payroll/`
- Revisar logs de exportación
- Confirmar que los resúmenes tienen estado `pending_approval`

### Resúmenes en estado error

- Revisar el campo `error_message` del resumen
- Verificar que todos los viajes tengan tarifa configurada
- Validar configuración de comisiones y mínimo garantizado
