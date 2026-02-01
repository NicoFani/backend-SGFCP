import sqlite3

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

# Buscar María González
c.execute("SELECT id, full_name, current_commission_percentage FROM driver WHERE full_name LIKE '%María%'")
driver = c.fetchone()
print(f"Driver: {driver}")

if driver:
    driver_id = driver[0]
    commission_pct = driver[2]
    
    # Buscar resumen más reciente
    c.execute("""
        SELECT ps.id, ps.driver_id, ps.commission_from_trips, ps.total_amount 
        FROM payroll_summaries ps 
        WHERE ps.driver_id = ?
        ORDER BY ps.id DESC 
        LIMIT 1
    """, (driver_id,))
    summary = c.fetchone()
    print(f"\nSummary: {summary}")
    
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
        print(f"Suma de comisiones de detalles: ${total_from_details}")
        print(f"Campo commission_from_trips:    ${summary[2]}")
        print(f"Diferencia: ${abs(total_from_details - summary[2])}")
        
        # Buscar viajes finalizados
        c.execute("""
            SELECT t.id, t.document_type, t.document_number, t.calculated_per_km,
                   t.estimated_kms, t.load_weight_on_unload, t.rate
            FROM trip t
            WHERE t.driver_id = ? 
                AND t.start_date >= '2026-02-01' 
                AND t.start_date <= '2026-02-28'
                AND t.state_id = 'Finalizado'
        """, (driver_id,))
        trips = c.fetchall()
        
        print(f"\n=== Viajes finalizados en febrero 2026 ({len(trips)} viajes) ===")
        total_manual = 0
        for trip in trips:
            trip_id, doc_type, doc_num, per_km, kms, tonnage, rate = trip
            
            if per_km:
                base_amount = kms * rate
                calc_type = f"{kms} km × ${rate}/km"
            else:
                base_amount = tonnage * rate
                calc_type = f"{tonnage} t × ${rate}/t"
            
            commission = base_amount * commission_pct
            total_manual += commission
            
            print(f"\n  Viaje {trip_id}: {doc_type} {doc_num}")
            print(f"    {calc_type} = ${base_amount}")
            print(f"    Comisión ({commission_pct*100}%): ${commission}")
        
        print(f"\n=== Total calculado manualmente: ${total_manual} ===")

conn.close()
