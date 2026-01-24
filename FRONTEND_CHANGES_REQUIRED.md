# Cambios Requeridos en Frontend (Flutter)

## Resumen

El refactoring del módulo de nómina en el backend requiere actualizaciones en el frontend para mantener la compatibilidad con la nueva API.

## 1. Modelo ExpenseData (`lib/models/expense_data.dart`)

### CAMBIO CRÍTICO: toll_paid_by → paid_by_admin

**Antes:**

```dart
final String? tollPaidBy;  // Enum: "admin", "driver", "port"
```

**Después:**

```dart
final bool? paidByAdmin;   // Boolean: true = admin pagó, false = chofer pagó (reembolsable)
```

### Cambios Requeridos:

1. **Actualizar modelo:**

```dart
class ExpenseData {
  // ... otros campos
  final bool? paidByAdmin;  // Cambiar de String? tollPaidBy

  ExpenseData({
    // ...
    this.paidByAdmin,  // Cambiar de this.tollPaidBy
  });

  factory ExpenseData.fromJson(Map<String, dynamic> json) {
    return ExpenseData(
      // ...
      paidByAdmin: json['paid_by_admin'] as bool?,  // Cambiar de json['toll_paid_by']
    );
  }
}
```

2. **Actualizar servicio (`lib/services/expense_service.dart`):**

```dart
static Future<ExpenseData> createExpense({
  // ... otros parámetros
  bool? paidByAdmin,  // Cambiar de String? tollPaidBy
}) async {
  final payload = {
    // ...
    if (paidByAdmin != null) 'paid_by_admin': paidByAdmin,  // Cambiar de 'toll_paid_by'
  };
}
```

3. **Actualizar UI:**
   - Cambiar dropdown con 3 opciones (admin/driver/port) por un simple checkbox o switch
   - Label sugerido: "Pagado por administración" (true) / "Pagado por chofer" (false)

---

## 2. Modelo DriverData (`lib/models/driver_data.dart`)

### CAMBIO: Eliminar campo commission

**Estado Actual:** El modelo NO tiene campo commission, por lo que **NO requiere cambios**.

**Nota:** El backend movió commission de Driver a DriverCommissionHistory. Si en el futuro se necesita mostrar la comisión actual del chofer, se deberá:

- Crear nuevo endpoint GET `/driver-commission/driver/{driver_id}/current`
- Agregar campo opcional en DriverData o crear modelo separado

---

## 3. Servicios de Nómina (PENDIENTE DE CREAR)

**Actualmente NO EXISTEN** servicios de nómina en el frontend. Si se planea implementar funcionalidad de nómina en Flutter, se necesitarán:

### 3.1 Crear `lib/services/payroll_service.dart`

```dart
class PayrollService {
  static String get baseUrl => dotenv.env['BACKEND_URL'] ?? 'http://localhost:5000';

  // Generar nóminas
  static Future<List<dynamic>> generatePayroll({
    required int periodId,
    List<int>? driverIds,
    bool isManual = false,  // NUEVO: reemplaza calculation_type
  }) async {
    final payload = {
      'period_id': periodId,
      if (driverIds != null) 'driver_ids': driverIds,
      'is_manual': isManual,  // CAMBIO: antes era 'calculation_type': 'both'|'km'|'tonnage'
    };
    // ... implementar llamada a POST /payroll-summaries/generate
  }

  // Recalcular nómina (NUEVO ENDPOINT)
  static Future<dynamic> recalculatePayroll({
    required int summaryId,
  }) async {
    // POST /payroll-summaries/{id}/recalculate
    // Mueve la nómina actual a draft y genera una nueva en pending_approval
  }

  // Obtener nóminas de un período
  static Future<List<dynamic>> getPayrollsByPeriod({
    required int periodId,
  }) async {
    // GET /payroll-summaries/period/{id}
  }
}
```

### 3.2 Crear `lib/services/minimum_guaranteed_service.dart` (NUEVO)

```dart
class MinimumGuaranteedService {
  // Crear/actualizar mínimo garantizado para un chofer
  static Future<dynamic> createMinimumGuaranteed({
    required int driverId,
    required double minimumGuaranteed,
    required DateTime effectiveFrom,
  }) async {
    // POST /minimum-guaranteed
  }

  // Obtener mínimo garantizado vigente
  static Future<dynamic> getCurrentMinimumGuaranteed({
    required int driverId,
  }) async {
    // GET /minimum-guaranteed/driver/{id}/current
  }

  // Obtener historial de mínimos garantizados
  static Future<List<dynamic>> getMinimumGuaranteedHistory({
    required int driverId,
  }) async {
    // GET /minimum-guaranteed?driver_id={id}
  }
}
```

### 3.3 Crear `lib/services/payroll_other_item_service.dart` (NUEVO)

```dart
class PayrollOtherItemService {
  // Crear otro concepto (ajuste, bono, multa, cargo)
  static Future<dynamic> createOtherItem({
    required int driverId,
    required int periodId,
    required String itemType,  // 'adjustment', 'bonus', 'extra_charge', 'fine'
    required double amount,
    String? description,
    required int createdBy,
  }) async {
    // POST /payroll-other-items
  }

  // Obtener otros conceptos de un chofer en un período
  static Future<List<dynamic>> getOtherItems({
    required int periodId,
    required int driverId,
  }) async {
    // GET /payroll-other-items/period/{pid}/driver/{did}
  }

  // Obtener resumen agrupado por tipo
  static Future<Map<String, double>> getOtherItemsSummary({
    required int periodId,
    required int driverId,
  }) async {
    // GET /payroll-other-items/period/{pid}/driver/{did}/summary
  }
}
```

---

## 4. Modelos de Nómina (PENDIENTE DE CREAR)

### 4.1 Crear `lib/models/payroll_summary_data.dart`

```dart
class PayrollSummaryData {
  final int id;
  final int periodId;
  final int driverId;
  final String status;  // NUEVOS VALORES: 'calculation_pending', 'pending_approval', 'error', 'draft', 'approved'

  // Campos de cálculo
  final double commissionFromTrips;
  final double driverMinimumGuaranteed;  // NUEVO
  final double totalExpenses;
  final double totalAdvances;
  final double otherItemsTotal;  // NUEVO: suma de ajustes/bonos/multas/cargos
  final double totalNet;

  // Metadatos
  final String? errorMessage;  // NUEVO: mensaje de error si status = 'error'
  final DateTime createdAt;
  final DateTime? approvedAt;

  // ... constructor y fromJson
}
```

**IMPORTANTE - Nuevos estados de nómina:**

- `calculation_pending`: Esperando tarifa para calcular
- `pending_approval`: Calculada, pendiente de aprobación
- `error`: Error en cálculo (ver errorMessage)
- `draft`: Borrador (nómina anterior después de recalcular)
- `approved`: Aprobada

### 4.2 Crear `lib/models/minimum_guaranteed_data.dart`

```dart
class MinimumGuaranteedData {
  final int id;
  final int driverId;
  final double minimumGuaranteed;
  final DateTime effectiveFrom;
  final DateTime? effectiveUntil;  // null = vigente actualmente
  final DateTime createdAt;
}
```

### 4.3 Crear `lib/models/payroll_other_item_data.dart`

```dart
class PayrollOtherItemData {
  final int id;
  final int driverId;
  final int periodId;
  final String itemType;  // 'adjustment', 'bonus', 'extra_charge', 'fine'
  final double amount;
  final String? description;
  final int createdBy;
  final DateTime createdAt;
}
```

---

## 5. Cambios en UI (Recomendaciones)

### 5.1 Formulario de Gastos

- **Quitar:** Dropdown "Peaje pagado por" con opciones admin/driver/port
- **Agregar:** Checkbox/Switch "Pagado por administración"
  - Marcado = administración pagó (no reembolsable)
  - Desmarcado = chofer pagó (reembolsable)

### 5.2 Vista de Nómina (si existe/se crea)

- **Agregar:** Estado "Error" en lista de nóminas
- **Agregar:** Botón "Recalcular" para nóminas en estado `pending_approval` o `error`
- **Agregar:** Mostrar campo "Mínimo Garantizado Aplicado"
- **Agregar:** Mostrar campo "Otros Conceptos" (suma de ajustes/bonos/multas)
- **Actualizar:** Manejo de 5 estados en lugar de 3

### 5.3 Vista de Chofer (opcional)

- **Agregar:** Gestión de comisión histórica por chofer
- **Agregar:** Gestión de mínimo garantizado histórico

---

## 6. Prioridad de Implementación

### ALTA PRIORIDAD (Bloquea funcionalidad actual)

1. ✅ **ExpenseData.tollPaidBy → paidByAdmin** (CRÍTICO)
2. ✅ **ExpenseService.createExpense/updateExpense** - actualizar parámetros

### MEDIA PRIORIDAD (Funcionalidad nueva del backend)

3. ⏳ Crear modelos de nómina (PayrollSummaryData, MinimumGuaranteedData, PayrollOtherItemData)
4. ⏳ Crear servicios de nómina (PayrollService, MinimumGuaranteedService, PayrollOtherItemService)
5. ⏳ Actualizar UI de gastos (cambiar dropdown por checkbox)

### BAJA PRIORIDAD (Features opcionales)

6. ⏳ Crear UI completa de gestión de nómina
7. ⏳ Implementar gestión de comisiones históricas
8. ⏳ Implementar gestión de mínimos garantizados

---

## 7. Verificación de Compatibilidad

### Endpoints que CAMBIARON:

- `POST /payroll-summaries/generate` - parámetro `calculation_type` → `is_manual`

### Endpoints NUEVOS:

- `POST /payroll-summaries/{id}/recalculate`
- `GET/POST /minimum-guaranteed`
- `GET /minimum-guaranteed/driver/{id}/current`
- `GET/POST/PUT/DELETE /payroll-other-items`
- `GET /payroll-other-items/period/{pid}/driver/{did}/summary`

### Campos de modelo que CAMBIARON:

- **Expense:** `toll_paid_by` (String enum) → `paid_by_admin` (Boolean)
- **PayrollSummary:** Eliminados `calculation_type`, `adjustments_applied`; agregados `driver_minimum_guaranteed`, `other_items_total`, `error_message`
- **Driver:** Eliminado `commission` (ahora en DriverCommissionHistory)

---

## 8. Testing Recomendado

1. **Test de migración:**
   - Crear gasto con `paid_by_admin: true` → verificar que se guarda correctamente
   - Crear gasto con `paid_by_admin: false` → verificar que se marca como reembolsable

2. **Test de compatibilidad:**
   - Verificar que gastos existentes (con `toll_paid_by` viejo) se lean correctamente después de migración

3. **Test de nómina (si se implementa UI):**
   - Generar nómina con `is_manual: false`
   - Recalcular nómina existente
   - Verificar estados de nómina (pending, error, approved, draft)

---

## Notas Importantes

- **No eliminar campos deprecados inmediatamente:** Mantener compatibilidad temporal si hay gastos antiguos en la base de datos
- **Coordinar migración:** Ejecutar script de migración del backend ANTES de actualizar el frontend
- **Backup obligatorio:** Hacer backup de la BD antes de migrar
