import sqlite3

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

# Buscar María González
c.execute("""
    SELECT u.id, u.name, u.surname 
    FROM app_user u 
    JOIN driver d ON u.id = d.id 
    WHERE u.name LIKE '%María%' OR u.surname LIKE '%González%'
""")
user = c.fetchone()
print(f"User: {user}")

if user:
    driver_id = user[0]
    
    # Buscar comisión en history
    c.execute("""
        SELECT commission_percentage 
        FROM driver_commission_history 
        WHERE driver_id = ?
        AND effective_until IS NULL
        ORDER BY effective_from DESC
        LIMIT 1
    """, (driver_id,))
    commission_record = c.fetchone()
    commission_pct = commission_record[0] if commission_record else 0
    print(f"Comisión actual: {commission_pct} ({commission_pct*100}%)")
    
    # Buscar resumen más reciente
    c.execute("""
        SELECT id, driver_id, commission_from_trips, total_amount 
        FROM payroll_summaries
        WHERE driver_id = ?
        ORDER BY id DESC 
        LIMIT 1
    """, (driver_id,))
    summary = c.fetchone()
    
    if summary:
        summary_id = summary[0]
        print(f"\nResumen ID: {summary_id}")
        print(f"Total comisiones en campo: ${summary[2]}")
        
        # Buscar detalles de comisiones
        c.execute("""
            SELECT id, description, amount 
            FROM payroll_details 
            WHERE summary_id = ? AND detail_type = 'trip_commission'
        """, (summary_id,))
        details = c.fetchall()
        
        print(f"\n=== Detalles de comisiones ({len(details)} viajes) ===")
        total_from_details = 0
        for detail in details:
            print(f"  {detail[1]}: ${detail[2]}")
            total_from_details += detail[2]
        
        print(f"\n=== Verificación ===")
        print(f"Suma de detalles individuales:   ${total_from_details}")
        print(f"Campo commission_from_trips:     ${summary[2]}")
        diff = abs(total_from_details - summary[2])
        if diff > 0.01:
            print(f"¡ERROR! Diferencia: ${diff}")
            print(f"El campo tiene: ${summary[2] - total_from_details} de más")
        else:
            print("✓ Coinciden correctamente")

conn.close()
