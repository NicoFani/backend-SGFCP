"""
Script de inicio del servidor Flask con SQLite
Inicializa la base de datos si no existe
"""
import os
import sys
from pathlib import Path

print("🔧 Iniciando SGFCP Backend...")

try:
    from app import create_app
    from app.db import db
    
    app = create_app()
    
    # Verificar si la base de datos existe, si no, crearla
    db_path = Path(__file__).parent / "sgfcp.db"
    if not db_path.exists():
        print("📦 Base de datos no encontrada, creando...")
        with app.app_context():
            db.create_all()
        print(f"✅ Base de datos creada: {db_path}")
    else:
        print(f"✅ Usando base de datos: {db_path}")
    
    print("\n🚀 Starting SGFCP Backend Server...")
    print("📡 Available endpoints:")
    print("  - GET/POST/PUT/DELETE    /drivers")
    print("  - GET/POST/PUT/DELETE    /trucks")
    print("  - GET/POST/PUT/DELETE    /trips")
    print("  - GET/POST/PUT/DELETE    /expenses")
    print("  - GET/POST/PUT/DELETE    /advance-payments")
    print("  - GET/POST/PUT/DELETE    /users")
    print("  - GET/POST/PUT/DELETE    /clients")
    print("  - GET/POST/PUT/DELETE    /commission-percentages")
    print("  - GET/POST/PUT/DELETE    /driver-trucks")
    print("  - GET/POST/PUT/DELETE    /km-rates")
    print("  - GET/POST/PUT/DELETE    /load-owners")
    print("  - GET/POST/PUT/DELETE    /monthly-summaries")
    print("🌐 Server running on http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de haber instalado las dependencias: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al iniciar el servidor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
