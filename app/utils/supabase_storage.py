"""Utilidad para gestionar archivos en Supabase Storage."""
import os
from supabase import create_client, Client
from werkzeug.utils import secure_filename
from datetime import datetime


class SupabaseStorage:
    """Clase para manejar el almacenamiento de archivos en Supabase."""
    
    def __init__(self):
        """Inicializar cliente de Supabase."""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
        
        self.client: Client = create_client(url, key)
        self.bucket = os.getenv('SUPABASE_BUCKET', 'receipts')
    
    def upload_file(self, file_bytes, filename, folder='advance_receipts'):
        """
        Subir un archivo a Supabase Storage.
        
        Args:
            file_bytes: Bytes del archivo
            filename: Nombre del archivo
            folder: Carpeta dentro del bucket (default: 'advance_receipts')
        
        Returns:
            URL pública del archivo o ruta relativa
        """
        try:
            # Generar nombre seguro con timestamp
            safe_filename = secure_filename(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{safe_filename}"
            
            # Ruta completa en el bucket
            file_path = f"{folder}/{unique_filename}"
            
            # Subir archivo
            response = self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": self._get_content_type(filename)}
            )
            
            # Obtener URL pública
            public_url = self.client.storage.from_(self.bucket).get_public_url(file_path)
            
            return public_url
        except Exception as e:
            raise Exception(f"Error subiendo archivo a Supabase: {str(e)}")
    
    def delete_file(self, file_path):
        """
        Eliminar un archivo de Supabase Storage.
        
        Args:
            file_path: Ruta del archivo en el bucket o URL completa
        """
        try:
            # Si es URL completa, extraer la ruta
            if file_path.startswith('http'):
                # Extraer la ruta después de /storage/v1/object/public/bucket_name/
                parts = file_path.split(f'/storage/v1/object/public/{self.bucket}/')
                if len(parts) > 1:
                    file_path = parts[1]
            
            self.client.storage.from_(self.bucket).remove([file_path])
        except Exception as e:
            # No lanzar error si el archivo no existe
            print(f"Advertencia al eliminar archivo: {str(e)}")
    
    def _get_content_type(self, filename):
        """Determinar el content-type basado en la extensión del archivo."""
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        content_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
        }
        
        return content_types.get(extension, 'application/octet-stream')


# Instancia global
supabase_storage = SupabaseStorage()
