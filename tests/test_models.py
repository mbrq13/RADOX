"""
Pruebas para modelos de RADOX
Pruebas unitarias para CNN y Vector Store
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch
import asyncio

# Importar módulos a probar
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCNNModel:
    """Pruebas para el modelo CNN"""
    
    @pytest.fixture
    def temp_model_path(self):
        """Crear directorio temporal para modelos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_cnn_model_initialization(self, temp_model_path):
        """Probar inicialización del modelo CNN"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel(temp_model_path)
        assert model.model_path == temp_model_path
        assert model.is_loaded == False
        assert model.input_shape == (224, 224, 3)
        assert len(model.class_names) == 2
    
    def test_preprocess_image_rgb(self):
        """Probar preprocesamiento de imagen RGB"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel("/tmp")
        
        # Crear imagen de prueba
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        processed = model.preprocess_image(test_image)
        
        # Verificar dimensiones
        assert processed.shape == (1, 224, 224, 3)
        assert processed.dtype == np.float32
    
    def test_preprocess_image_grayscale(self):
        """Probar preprocesamiento de imagen en escala de grises"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel("/tmp")
        
        # Crear imagen en escala de grises
        test_image = np.random.randint(0, 255, (300, 300), dtype=np.uint8)
        
        processed = model.preprocess_image(test_image)
        
        # Verificar que se convirtió a RGB y se redimensionó
        assert processed.shape == (1, 224, 224, 3)
    
    def test_confidence_level_mapping(self):
        """Probar mapeo de niveles de confianza"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel("/tmp")
        
        assert model._get_confidence_level(0.95) == "Muy Alta"
        assert model._get_confidence_level(0.85) == "Alta"
        assert model._get_confidence_level(0.75) == "Media"
        assert model._get_confidence_level(0.65) == "Baja"
        assert model._get_confidence_level(0.45) == "Muy Baja"
    
    def test_recommendation_generation(self):
        """Probar generación de recomendaciones"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel("/tmp")
        
        # Prueba con neumonía alta confianza
        rec = model._get_recommendation("Neumonía", 0.9)
        assert "evaluación médica inmediata" in rec.lower()
        
        # Prueba con normal alta confianza
        rec = model._get_recommendation("Normal", 0.9)
        assert "normalidad" in rec.lower()

class TestVectorStore:
    """Pruebas para el Vector Store"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Crear directorio temporal para base de datos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_vector_store_initialization(self, temp_db_path):
        """Probar inicialización del vector store"""
        from backend.models.vector_store import VectorStore
        
        vs = VectorStore(temp_db_path)
        assert vs.db_path == temp_db_path
        assert vs.is_connected == False
        assert vs.collection_name == "pneumonia_cases"
    
    def test_case_embedding_generation(self, temp_db_path):
        """Probar generación de embeddings para casos"""
        from backend.models.vector_store import VectorStore
        
        vs = VectorStore(temp_db_path)
        
        # Mock del modelo de embeddings
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
            mock_st.return_value = mock_model
            
            vs.embedding_model = mock_model
            
            case_data = {
                "diagnosis": "Neumonía",
                "symptoms": "Tos, fiebre",
                "findings": "Consolidación",
                "age": 45,
                "gender": "M",
                "severity": "moderada"
            }
            
            embedding = vs._generate_case_embedding(case_data)
            
            assert isinstance(embedding, list)
            assert len(embedding) == 3
            mock_model.encode.assert_called_once()

@pytest.mark.asyncio
class TestAsyncMethods:
    """Pruebas para métodos asíncronos"""
    
    async def test_cnn_model_predict_without_model(self):
        """Probar predicción sin modelo cargado"""
        from backend.models.cnn_model import CNNModel
        
        model = CNNModel("/tmp")
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError):
            await model.predict(test_image)
    
    @patch('chromadb.PersistentClient')
    @patch('sentence_transformers.SentenceTransformer')
    async def test_vector_store_initialization_async(self, mock_st, mock_chroma):
        """Probar inicialización asíncrona del vector store"""
        from backend.models.vector_store import VectorStore
        
        # Configurar mocks
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_client.create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client
        
        mock_model = Mock()
        mock_st.return_value = mock_model
        
        vs = VectorStore("/tmp")
        result = await vs.initialize()
        
        assert result == True
        assert vs.is_connected == True

class TestImageProcessing:
    """Pruebas para utilidades de procesamiento de imágenes"""
    
    def test_image_validation(self):
        """Probar validación de imágenes médicas"""
        from backend.utils.image_processing import validate_medical_image
        
        # Crear imagen de prueba válida
        from PIL import Image
        import io
        
        image = Image.new('RGB', (512, 512), color='white')
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        result = validate_medical_image(img_data, "test.png")
        
        assert result["is_valid"] == True
        assert result["format"] == "png"
        assert result["size"] > 0
        assert "dimensions" in result
    
    def test_image_validation_too_small(self):
        """Probar validación con imagen muy pequeña"""
        from backend.utils.image_processing import validate_medical_image
        
        # Datos muy pequeños
        small_data = b"tiny"
        
        result = validate_medical_image(small_data, "test.png")
        
        assert result["is_valid"] == False
        assert "demasiado pequeño" in result["errors"][0]
    
    def test_image_processor_normalize(self):
        """Probar normalización de imágenes"""
        from backend.utils.image_processing import ImageProcessor
        
        # Crear imagen con valores fuera del rango 0-255
        test_image = np.array([[100, 200], [300, 400]], dtype=np.float32)
        
        normalized = ImageProcessor.normalize_to_uint8(test_image)
        
        assert normalized.dtype == np.uint8
        assert normalized.min() == 0
        assert normalized.max() == 255
    
    def test_image_processor_resize(self):
        """Probar redimensionamiento de imágenes"""
        from backend.utils.image_processing import ImageProcessor
        
        # Crear imagen de prueba
        test_image = np.random.randint(0, 255, (100, 150), dtype=np.uint8)
        
        resized = ImageProcessor.resize_image(test_image, (224, 224))
        
        assert resized.shape == (224, 224)

# Utilidades para pruebas
def create_sample_case_data():
    """Crear datos de caso de ejemplo para pruebas"""
    return {
        "case_id": "test_case_001",
        "diagnosis": "Neumonía bacteriana",
        "symptoms": "Tos, fiebre alta, dificultad respiratoria",
        "findings": "Consolidación en lóbulo inferior derecho",
        "age": 45,
        "gender": "M",
        "severity": "moderada",
        "confidence": 0.85
    }

def create_sample_detection_result():
    """Crear resultado de detección de ejemplo"""
    return {
        "case_id": "test_case_001",
        "prediction": {
            "predicted_class": "Neumonía",
            "confidence": 0.85,
            "has_pneumonia": True,
            "confidence_level": "Alta",
            "class_probabilities": {
                "Normal": 0.15,
                "Neumonía": 0.85
            },
            "recommendation": "Se recomienda evaluación médica inmediata"
        },
        "case_data": create_sample_case_data()
    }

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 