from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 Starting SGFCP Backend Server...")
    print("📡 Available endpoints:")
    print("  - GET/POST    /drivers")
    print("  - GET/POST    /trucks") 
    print("  - GET/POST    /trips")
    print("  - GET/POST    /expenses")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
