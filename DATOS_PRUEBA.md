# 📋 Datos de Prueba - Sistema de Gestión de Flota

Datos coherentes para testear el flujo completo del sistema (Febrero 2026).

---

## 👤 CHOFERES DISPONIBLES

Según tus datos actuales, tienes 3 choferes:

- **Juan Pérez** (ID: 1)
- **María González** (ID: 2)
- **Carlos Rodríguez** (ID: 3)

Usuario para login: El nombre del chofer (ej: `juan`, `maria`, `carlos`)

---

## 🚚 ESCENARIO DE PRUEBA 1: Viaje Completo con Gastos

### 1. CREAR VIAJE

**Fecha de inicio:** 17/02/2026 (hoy)

**Origen:** Rosario, Santa Fe  
**Destino:** Buenos Aires, CABA  
**Descripción origen:** Puerto San Martín - Terminal 6  
**Descripción destino:** Depósito Industrial Parque Patricios

**Cliente:** (Seleccionar uno existente o crear nuevo)

- Nombre: "Transportes del Sur S.A."

**Dueño de la carga:** (Seleccionar uno existente)

- Ejemplo: "Molinos Río de la Plata"

**Tipo de carga:**

- Cereales / Granos

**Peso al cargar:** 25.5 toneladas  
**Distancia estimada:** 320 km

**Tarifa:** $8,500 por tonelada  
**Cálculo:** Por tonelada

**Combustible por cuenta del cliente:**

- ❌ NO
- Litros: 0

**Adelanto del cliente al chofer:** $150,000

**Documento:**

- Tipo: Carta de Porte
- Número: CP-2026-001234

**Chofer asignado:** Juan Pérez

---

### 2. INICIAR VIAJE

1. Login como Juan Pérez
2. Ver "Tu próximo viaje" en la pantalla principal
3. Click en "Comenzar viaje"
4. Confirmar peso de carga: **25.5 ton**
5. El viaje cambia a estado "En curso"

---

### 3. CARGAR GASTOS DURANTE EL VIAJE

#### Gasto 1: Peaje

- **Tipo:** Peaje
- **Subtipo:** Peaje de ruta
- **Fecha:** 17/02/2026
- **Importe:** $12,500
- **¿Pagó contaduría?** NO
- **Foto:** Adjuntar comprobante

#### Gasto 2: Combustible

- **Tipo:** Combustible
- **Fecha:** 17/02/2026
- **Importe:** $85,000
- **Litros cargados:** 120
- **Foto:** Adjuntar comprobante

#### Gasto 3: Viáticos (comida)

- **Tipo:** Viáticos
- **Fecha:** 17/02/2026
- **Importe:** $15,000
- **Foto:** Adjuntar comprobante

#### Gasto 4: Peaje (otro)

- **Tipo:** Peaje
- **Subtipo:** Peaje de ruta
- **Fecha:** 17/02/2026
- **Importe:** $8,000
- **¿Pagó contaduría?** NO

**Total gastos:** $120,500

---

### 4. CARGAR ADELANTOS

Como admin, cargar adelantos al chofer:

#### Adelanto 1

- **Chofer:** Juan Pérez
- **Fecha:** 17/02/2026
- **Monto:** $50,000
- **Descripción:** Adelanto en ruta
- **Comprobante:** Adjuntar recibo

#### Adelanto 2

- **Chofer:** Juan Pérez
- **Fecha:** 17/02/2026
- **Monto:** $30,000
- **Descripción:** Solicitud chofer urgencia
- **Comprobante:** Adjuntar recibo

**Total adelantos:** $80,000

---

### 5. FINALIZAR VIAJE

1. Login como Juan Pérez
2. En "Viaje actual" → Click "Finalizar viaje"
3. Completar datos:
   - **Fecha de finalización:** 17/02/2026
   - **Peso al descargar:** 25.2 ton (pérdida normal por merma)
   - **Km reales recorridos:** 325 km
4. Confirmar finalización

---

### 6. CÁLCULO ESPERADO

**Facturación:**

- 25.2 ton × $8,500/ton = **$214,200**

**Comisión del chofer (18%):**

- $214,200 × 0.18 = **$38,556**

**Balance preliminar:**

```
Comisión bruta:           $38,556
+ Adelanto del cliente:  $150,000
- Gastos:               -$120,500
- Adelantos pagados:     -$80,000
TOTAL A LIQUIDAR:       -$11,944
```

**Nota:** El chofer debe al sistema $11,944 (gastos y adelantos superaron la comisión y adelanto del cliente)

---

## 🚚 ESCENARIO DE PRUEBA 2: Viaje con Mínimo Garantizado

Para que se aplique el mínimo garantizado ($1.000.000), crear un viaje con comisión baja:

### Datos del Viaje

**Chofer:** María González

**Ruta:** Córdoba → Mendoza  
**Descripción origen:** Planta Industrial Zona Franca  
**Descripción destino:** Bodega Vista Alegre

**Cliente:** Logística Express

**Tipo de carga:** Alimentos envasados  
**Peso al cargar:** 15 ton  
**Distancia:** 650 km

**Tarifa:** $2,500 por tonelada (BAJA para probar mínimo)  
**Cálculo:** Por tonelada

**Combustible cliente:** NO  
**Adelanto cliente:** $50,000

**Documento:** Remito R-789456

**Inicio:** 17/02/2026  
**Fin:** 17/02/2026  
**Peso final:** 15 ton

**Comisión calculada:**

- 15 ton × $2,500 = $37,500
- 18% = $6,750 ← **MENOR que mínimo garantizado**

**Se aplicará:** $1.000.000 (mínimo garantizado)

---

## 🚚 ESCENARIO DE PRUEBA 3: Viaje Calculado por Kilómetro

### Datos del Viaje

**Chofer:** Carlos Rodríguez

**Ruta:** Buenos Aires → Mar del Plata  
**Origen:** Retiro  
**Destino:** Puerto de Mar del Plata

**Cliente:** Marítima Argentina

**Tipo de carga:** Contenedores  
**Peso:** 20 ton  
**Distancia:** 400 km

**Tarifa:** $850 por kilómetro  
**Cálculo:** Por kilómetro ✅

**Combustible cliente:** SÍ  
**Litros de combustible:** 150 lts

**Adelanto cliente:** $100,000

**Documento:** Carta de Porte CP-555222

**Gastos:**

- Peaje: $18,000
- Viáticos: $25,000

**Comisión esperada:**

- 400 km × $850 = $340,000
- 18% = $61,200

---

## 📊 GENERAR RESÚMENES

### Periodo de Liquidación

1. Login como Admin
2. Ir a "Resúmenes"
3. Click "Generar resumen"
4. Seleccionar:
   - **Periodo:** Febrero de 2026
   - **Chofer:** Juan Pérez (para el escenario 1)
5. Click "Generar resumen"

El resumen mostrará:

- Viajes realizados en febrero
- Total comisión
- Total gastos (desglosados)
- Total adelantos
- Aplicación de mínimo garantizado (si corresponde)
- Liquidación final

---

## 💰 CARGAR OTROS CONCEPTOS

Antes o después de generar resumen, puedes cargar:

### Bonificación

- **Chofer:** Juan Pérez
- **Periodo:** Febrero 2026
- **Tipo:** Bonificación
- **Monto:** $50,000
- **Descripción:** "Bono por buen desempeño"

### Multa

- **Chofer:** María González
- **Periodo:** Febrero 2026
- **Tipo:** Multa
- **Monto:** -$25,000
- **Descripción:** "Infracción de tránsito"
- **Municipio:** Córdoba Capital

### Ajuste

- **Chofer:** Carlos Rodríguez
- **Periodo:** Febrero 2026
- **Tipo:** Ajuste
- **Monto:** -$10,000
- **Descripción:** "Corrección facturación mes anterior"

---

## 🔄 FLUJO COMPLETO DE TESTING

### Día 1: Configuración

1. ✅ Ejecutar `clean_test_data.py` (limpiar BD)
2. ✅ Ejecutar `load_driver_defaults.py` (cargar valores default)
3. Verificar que existen clientes, tipos de carga, etc.

### Día 2: Viajes

1. Crear Viaje 1 (Juan) - con gastos y adelantos
2. Crear Viaje 2 (María) - prueba mínimo garantizado
3. Crear Viaje 3 (Carlos) - calculado por km
4. Iniciar cada viaje
5. Cargar gastos
6. Finalizar cada viaje

### Día 3: Liquidación

1. Cargar "otros conceptos" para cada chofer
2. Generar resúmenes para Febrero 2026
3. Revisar cálculos
4. Aprobar resúmenes
5. Exportar a Excel/PDF (si está implementado)

---

## 📝 NOTAS IMPORTANTES

### Validaciones a Verificar

- ✅ No se puede generar resumen si ya existe uno "pendiente de aprobación"
- ✅ No se puede iniciar viaje si el chofer tiene otro "En curso"
- ✅ Gastos solo se pueden cargar en viajes "En curso"
- ✅ Adelantos se pueden cargar en cualquier momento
- ✅ Mínimo garantizado solo se aplica si comisión es menor

### Estados de Viaje

- **Pendiente:** Creado pero no iniciado
- **En curso:** Iniciado pero no finalizado
- **Finalizado:** Completado, listo para liquidar

### Estados de Resumen

- **draft:** Generación manual inicial
- **calculation_pending:** Esperando fin de viajes en curso
- **pending_approval:** Listo para revisar
- **approved:** Aprobado para pago
- **error:** Error en cálculo (ej: viajes sin tarifa)

---

## 🎯 CHECKLIST DE TESTING

- [ ] Crear viaje
- [ ] Asignar chofer
- [ ] Iniciar viaje
- [ ] Cargar gastos con fotos
- [ ] Cargar adelantos con comprobantes
- [ ] Finalizar viaje
- [ ] Verificar cálculos de comisión
- [ ] Cargar otros conceptos
- [ ] Generar resumen
- [ ] Verificar totales en resumen
- [ ] Validar que no se puede regenerar si está pendiente
- [ ] Aprobar resumen
- [ ] Verificar diferentes tipos de cálculo (por ton / por km)
- [ ] Verificar aplicación de mínimo garantizado
- [ ] Probar con combustible del cliente
- [ ] Probar adelanto del cliente al chofer

---

**¡Listo para testear! 🚀**
