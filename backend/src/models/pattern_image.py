from src.models.user import db
from datetime import datetime
import os

class PatternImage(db.Model):
    __tablename__ = 'pattern_images'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('patterns.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Relacionamento com Pattern
    pattern = db.relationship('Pattern', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<PatternImage {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern_id': self.pattern_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_primary': self.is_primary,
            'url': f'/patterns/images/{self.filename}'
        }
    
    @staticmethod
    def create_from_file(pattern_id, file_data, filename, original_filename=None):
        """Cria uma nova imagem de padrão a partir de dados de arquivo"""
        try:
            # Criar diretório se não existir
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'pattern_images')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"pattern_{pattern_id}_{timestamp}{file_extension}"
            
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Salvar arquivo
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Criar registro no banco
            pattern_image = PatternImage(
                pattern_id=pattern_id,
                filename=unique_filename,
                original_filename=original_filename or filename,
                file_path=file_path,
                file_size=len(file_data),
                mime_type=PatternImage._get_mime_type(file_extension)
            )
            
            return pattern_image
            
        except Exception as e:
            return {"error": f"Erro ao criar imagem: {str(e)}"}
    
    @staticmethod
    def _get_mime_type(file_extension):
        """Determina o tipo MIME baseado na extensão do arquivo"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(file_extension.lower(), 'application/octet-stream')
    
    def delete_file(self):
        """Remove o arquivo físico do disco"""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            return True
        except Exception as e:
            print(f"Erro ao deletar arquivo {self.file_path}: {str(e)}")
            return False
    
    def set_as_primary(self):
        """Define esta imagem como primária para o padrão"""
        try:
            # Remover flag primária de outras imagens do mesmo padrão
            PatternImage.query.filter_by(pattern_id=self.pattern_id, is_primary=True).update({'is_primary': False})
            
            # Definir esta como primária
            self.is_primary = True
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao definir imagem primária: {str(e)}"}

