import sqlite3

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

# Buscar Carlos Rodríguez
c.execute("""
    SELECT u.id, u.name, u.surname 
    FROM app_user u 
    JOIN driver d ON u.id = d.id 
    WHERE u.name LIKE '%Carlos%' AND u.surname LIKE '%Rodríguez%'
""")
user = c.fetchone()
print(f"Usuario: {user}")

if user:
    driver_id = user[0]
    
    # Buscar todos los resúmenes de Carlos en febrero 2026
    c.execute("""
        SELECT ps.id, pp.year, pp.month, ps.status, ps.commission_from_trips, ps.total_amount,
               ps.created_at, ps.updated_at
        FROM payroll_summaries ps
        JOIN payroll_periods pp ON ps.period_id = pp.id
        WHERE ps.driver_id = ?
        AND pp.start_date >= '2026-02-01'
        AND pp.end_date <= '2026-02-28'
        ORDER BY ps.id DESC
    """, (driver_id,))
    summaries = c.fetchall()
    
    print(f"\n=== Resúmenes de Carlos Rodríguez en Febrero 2026 ===")
    for summary in summaries:
        summary_id, year, month, status, commission, total, created, updated = summary
        print(f"\nResumen #{summary_id}:")
        print(f"  Período: {month}/{year}")
        print(f"  Estado: {status}")
        print(f"  Comisiones: ${commission}")
        print(f"  Total: ${total}")
        print(f"  Creado: {created}")
        print(f"  Actualizado: {updated}")
        
        # Ver si tiene viajes asociados
        c.execute("""
            SELECT COUNT(*) 
            FROM payroll_details 
            WHERE summary_id = ? AND detail_type = 'trip_commission'
        """, (summary_id,))
        trip_count = c.fetchone()[0]
        print(f"  Viajes con comisión: {trip_count}")
    
    # Ver viajes de Carlos en febrero
    c.execute("""
        SELECT id, document_type, document_number, state_id, start_date, end_date
        FROM trip
        WHERE driver_id = ?
        AND start_date >= '2026-02-01'
        AND start_date <= '2026-02-28'
        ORDER BY id
    """, (driver_id,))
    trips = c.fetchall()
    
    print(f"\n=== Viajes de Carlos en Febrero 2026 ===")
    for trip in trips:
        trip_id, doc_type, doc_num, state, start, end = trip
        print(f"\nViaje #{trip_id}: {doc_type} {doc_num}")
        print(f"  Estado: {state}")
        print(f"  Inicio: {start}")
        print(f"  Fin: {end}")

conn.close()
