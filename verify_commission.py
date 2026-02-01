import sqlite3

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

# Ver estructura de app_user
c.execute('PRAGMA table_info(app_user)')
print("Columnas app_user:", [col[1] for col in c.fetchall()])

# Buscar María González
c.execute("SELECT id, full_name, current_commission_percentage FROM app_user WHERE full_name LIKE '%María%'")
user = c.fetchone()
print(f"\nUser: {user}")

if user:
    user_id = user[0]
    commission_pct = user[2]
    
    # Buscar resumen más reciente
    c.execute("""
        SELECT id, driver_id, commission_from_trips, total_amount 
        FROM payroll_summaries
        WHERE driver_id = ?
        ORDER BY id DESC 
        LIMIT 1
    """, (user_id,))
    summary = c.fetchone()
    print(f"\nSummary ID: {summary[0] if summary else None}")
    print(f"Comisión en resumen: ${summary[2] if summary else 0}")
    
    if summary:
        summary_id = summary[0]
        
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
        print(f"Suma de comisiones individuales: ${total_from_details}")
        print(f"Campo commission_from_trips:     ${summary[2]}")
        if abs(total_from_details - summary[2]) > 0.01:
            print(f"¡ERROR! Diferencia: ${abs(total_from_details - summary[2])}")
        else:
            print("✓ Coinciden")
        
        # Buscar viajes finalizados
        c.execute("""
            SELECT t.id, t.document_type, t.document_number, t.calculated_per_km,
                   t.estimated_kms, t.load_weight_on_unload, t.rate
            FROM trip t
            WHERE t.driver_id = ? 
                AND t.start_date >= '2026-02-01' 
                AND t.start_date <= '2026-02-28'
                AND t.state_id = 'Finalizado'
        """, (user_id,))
        trips = c.fetchall()
        
        print(f"\n=== Viajes finalizados en febrero 2026 ({len(trips)} viajes) ===")
        total_manual = 0
        for trip in trips:
            trip_id, doc_type, doc_num, per_km, kms, tonnage, rate = trip
            
            if per_km:
                base_amount = (kms or 0) * (rate or 0)
                calc_type = f"{kms} km × ${rate}/km"
            else:
                base_amount = (tonnage or 0) * (rate or 0)
                calc_type = f"{tonnage} t × ${rate}/t"
            
            commission = base_amount * (commission_pct or 0)
            total_manual += commission
            
            print(f"\n  Viaje {trip_id}: {doc_type} {doc_num}")
            print(f"    {calc_type} = ${base_amount}")
            print(f"    Comisión ({(commission_pct or 0)*100}%): ${commission}")
        
        print(f"\n=== Total calculado manualmente: ${total_manual} ===")

conn.close()
