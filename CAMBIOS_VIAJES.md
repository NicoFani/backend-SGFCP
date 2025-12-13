## 🔄 CAMBIOS REALIZADOS EN EL MÓDULO DE VIAJES

### 📋 Resumen de Modificaciones:

#### 1. **Modelo Trip (app/models/trip.py)**

- ✅ Eliminado campo `driver_id` (relación 1-a-muchos)
- ✅ Agregada relación muchos-a-muchos con Driver a través de `trip_drivers`
- ✅ Agregados campos de descripción:
  - `origin_description`: Descripción del punto exacto de origen
  - `destination_description`: Descripción del punto exacto de destino
- ✅ Agregados campos de documento:
  - `document_type`: Enum (CTG/Remito)
  - `document_number`: String para guardar número de documento
- ✅ Agregados campos de combustible:
  - `fuel_liters`: Float para litros del vale
- ✅ Actualizado método `to_dict()` para retornar lista de choferes asignados

#### 2. **Modelo Base (app/models/base.py)**

- ✅ Agregado enum `document_type_enum` con valores: CTG, Remito
- ✅ Creada tabla asociativa `trip_drivers` para relación muchos-a-muchos

#### 3. **Schema Trip (app/schemas/trip.py)**

- ✅ Actualizado `TripSchema` con nuevos campos
- ✅ Agregado `drivers`: List[Integer] para múltiples choferes
- ✅ Agregada validación de formato de documento:
  - CTG: 11 dígitos exactos
  - Remito: 5 dígitos punto de venta + 8 dígitos número
- ✅ Actualizado `TripUpdateSchema` con mismos campos

#### 4. **Controlador Trip (app/controllers/trip.py)**

- ✅ Reescrito completamente para manejar múltiples choferes
- ✅ `get_all_trips()`: Filtra por choferes asignados (no admin)
- ✅ `get_trip_by_id()`: Verifica que el chofer esté asignado al viaje
- ✅ `create_trip()`: Asigna lista de choferes al viaje
- ✅ `update_trip()`: Actualiza permisos según estado del viaje:
  - **Pendiente** (Chofer iniciando): Puede actualizar documento, kms, peso carga, dador, vale combustible
  - **En curso** (Chofer finalizando): Puede actualizar fecha fin, peso descarga
  - **Finalizado**: No puede editar
- ✅ Validación de transiciones de estado: Pendiente→En curso, En curso→Finalizado
- ✅ Admin: Puede editar todos los campos en cualquier momento

#### 5. **Rutas Trip (app/routes/trip.py)**

- ✅ Sin cambios en la estructura
- ✅ Sigue el mismo patrón de permisos

#### 6. **Seeds (seeds/seed_relationships.py)**

- ✅ Actualizado para crear viajes con múltiples choferes
- ✅ Agregados datos de ejemplo para los nuevos campos
- ✅ Ejemplos de documentos: CTG y Remito con números válidos
- ✅ Ejemplos de viajes con múltiples choferes asignados

---

### 🗄️ CAMBIOS EN LA BASE DE DATOS

**Nuevos campos en tabla `trip`:**

```sql
origin_description VARCHAR(255)        -- Descripción del origen
destination_description VARCHAR(255)   -- Descripción del destino
document_type ENUM('CTG', 'Remito')   -- Tipo de documento
document_number VARCHAR(20)            -- Número de documento
fuel_liters FLOAT                      -- Litros del vale de combustible
```

**Nueva tabla:**

```sql
trip_drivers (tabla asociativa)
  - trip_id (FK)
  - driver_id (FK)
```

**Campos eliminados:**

- `driver_id` en tabla trip (reemplazado por relación muchos-a-muchos)
- `client_advance_payment`

---

### 🔐 PERMISOS Y FLUJO

**ADMIN:**

- ✅ Crear viajes con múltiples choferes
- ✅ Editar todos los campos en cualquier estado
- ✅ Cambiar estado del viaje libremente
- ✅ Ver todos los viajes

**CHOFER:**

- ✅ Ver solo viajes asignados
- ✅ **Estado PENDIENTE**: Cargar datos de inicio
  - Tipo y número de documento (CTG/Remito)
  - Kilómetros a recorrer
  - Peso de carga estimado
  - Dador de carga
  - Vale de combustible (sí/no) + litros
  - Cambiar a "En curso"
- ✅ **Estado EN CURSO**: Cargar datos de fin
  - Fecha de fin
  - Peso de descarga
  - Cambiar a "Finalizado"
- ✅ **Estado FINALIZADO**: Solo lectura

---

### 📝 PRÓXIMOS PASOS

1. Ejecutar: `python setup_db.py` para reinicializar la BD
2. Ejecutar: `python run.py` para iniciar el servidor
3. Actualizar `trip_management.html` con nuevos campos en formularios

---

### ✅ VALIDACIONES

- ✅ CTG: Exactamente 11 dígitos
- ✅ Remito: Exactamente 13 caracteres (5 + 8)
- ✅ Solo choferes asignados ven sus viajes
- ✅ Transiciones de estado controladas
- ✅ Campos limitados por estado del viaje
