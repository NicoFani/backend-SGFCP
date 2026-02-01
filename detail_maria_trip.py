import sqlite3
import json

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

# Buscar el viaje de María
c.execute("""
    SELECT t.id, t.document_type, t.document_number, t.calculated_per_km,
           t.estimated_kms, t.load_weight_on_unload, t.rate,
           pd.calculation_data
    FROM trip t
    JOIN payroll_details pd ON pd.trip_id = t.id
    WHERE t.driver_id = 2 
        AND t.state_id = 'Finalizado'
        AND pd.detail_type = 'trip_commission'
    ORDER BY t.id DESC
    LIMIT 1
""")
trip = c.fetchone()

if trip:
    trip_id, doc_type, doc_num, per_km, kms, tonnage, rate, calc_data = trip
    
    print(f"=== Viaje {trip_id}: {doc_type} {doc_num} ===")
    print(f"Calculado por km: {bool(per_km)}")
    
    if per_km:
        print(f"Kilómetros: {kms}")
        print(f"Tarifa por km: ${rate}")
        base = (kms or 0) * (rate or 0)
        print(f"Base = {kms} km × ${rate}/km = ${base}")
    else:
        print(f"Toneladas descargadas: {tonnage}")
        print(f"Tarifa por tonelada: ${rate}")
        base = (tonnage or 0) * (rate or 0)
        print(f"Base = {tonnage} t × ${rate}/t = ${base}")
    
    # Buscar comisión
    c.execute("""
        SELECT commission_percentage 
        FROM driver_commission_history 
        WHERE driver_id = 2
        AND effective_until IS NULL
        ORDER BY effective_from DESC
        LIMIT 1
    """)
    commission_record = c.fetchone()
    commission_pct = commission_record[0] if commission_record else 0
    
    commission_calculated = base * commission_pct
    print(f"\nComisión = ${base} × {commission_pct} ({commission_pct*100}%) = ${commission_calculated}")
    
    print(f"\n=== Datos del cálculo en payroll_details ===")
    if calc_data:
        data = json.loads(calc_data)
        print(json.dumps(data, indent=2))
    
    # Verificar en payroll_details
    c.execute("""
        SELECT amount 
        FROM payroll_details 
        WHERE trip_id = ? AND detail_type = 'trip_commission'
    """, (trip_id,))
    detail_amount = c.fetchone()
    print(f"\nMonto guardado en payroll_details: ${detail_amount[0]}")
    
    if abs(commission_calculated - detail_amount[0]) > 0.01:
        print(f"¡ERROR! La comisión calculada (${commission_calculated}) no coincide con la guardada (${detail_amount[0]})")
    else:
        print("✓ El cálculo es correcto")

conn.close()
