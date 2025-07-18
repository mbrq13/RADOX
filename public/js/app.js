class RadoxApp {
    constructor() {
        this.selectedFile = null;
        this.currentAnalysis = null;
        this.isAnalyzing = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.checkServerHealth();
    }

    initializeElements() {
        // Elementos del DOM
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.imagePreview = document.getElementById('imagePreview');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resultsSection = document.getElementById('resultsSection');
        this.diagnosisResult = document.getElementById('diagnosisResult');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceText = document.getElementById('confidenceText');
        this.reportSection = document.getElementById('reportSection');
        this.generateReportBtn = document.getElementById('generateReportBtn');
        this.reportContent = document.getElementById('reportContent');
        this.reportSummary = document.getElementById('reportSummary');
        this.reportFull = document.getElementById('reportFull');
        this.reportRecommendations = document.getElementById('reportRecommendations');
        this.reportTimestamp = document.getElementById('reportTimestamp');
    }

    setupEventListeners() {
        // Eventos de carga de archivos
        this.uploadArea.addEventListener('click', () => {
            if (!this.isAnalyzing) {
                this.fileInput.click();
            }
        });

        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (!this.isAnalyzing) {
                this.uploadArea.classList.add('dragover');
            }
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            
            if (!this.isAnalyzing && e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // Botón de análisis
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeImage();
        });

        // Botón de generar informe
        this.generateReportBtn.addEventListener('click', () => {
            this.generateReport();
        });
    }

    async checkServerHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'OK') {
                console.log('✅ Servidor RADOX conectado correctamente');
            }
        } catch (error) {
            console.error('❌ Error conectando con servidor:', error);
            this.showError('Error de conexión con el servidor');
        }
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validar tipo de archivo
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/dicom'];
        const allowedExtensions = ['.jpg', '.jpeg', '.png', '.dcm', '.dicom'];
        
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            this.showError('Formato de archivo no soportado. Use JPG, PNG o DICOM.');
            return;
        }

        // Validar tamaño
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showError('El archivo es demasiado grande. Máximo 10MB.');
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        this.resetResults();
    }

    displayFileInfo(file) {
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.classList.remove('d-none');

        // Mostrar preview si es imagen
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.imagePreview.src = e.target.result;
                this.imagePreview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        } else {
            this.imagePreview.classList.add('d-none');
        }

        this.analyzeBtn.disabled = false;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async analyzeImage() {
        if (!this.selectedFile || this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.showLoading(true);
        this.analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('radiografia', this.selectedFile);

            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.currentAnalysis = result.resultado;
                this.displayResults(result.resultado);
            } else {
                throw new Error(result.error || 'Error en el análisis');
            }

        } catch (error) {
            console.error('Error al analizar imagen:', error);
            this.showError('Error al analizar la imagen: ' + error.message);
        } finally {
            this.isAnalyzing = false;
            this.showLoading(false);
            this.analyzeBtn.disabled = false;
        }
    }

    displayResults(resultado) {
        // Mostrar diagnóstico
        this.diagnosisResult.textContent = resultado.diagnostico;
        this.diagnosisResult.className = 'status-badge ';
        
        if (resultado.tieneNeumonía) {
            this.diagnosisResult.classList.add('bg-danger', 'text-white');
            document.querySelector('.result-card').classList.add('diagnosis-positive');
        } else {
            this.diagnosisResult.classList.add('bg-success', 'text-white');
            document.querySelector('.result-card').classList.add('diagnosis-negative');
        }

        // Mostrar confianza
        const confidencePercent = resultado.porcentaje;
        this.confidenceFill.style.width = confidencePercent + '%';
        this.confidenceText.textContent = `${confidencePercent}% de confianza`;

        // Mostrar sección de informe si es neumonía
        if (resultado.puedeGenerarInforme) {
            this.reportSection.style.display = 'block';
        } else {
            this.reportSection.style.display = 'none';
        }

        // Mostrar resultados
        this.resultsSection.classList.remove('d-none');
        
        // Scroll suave a resultados
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async generateReport() {
        if (!this.currentAnalysis || !this.currentAnalysis.puedeGenerarInforme) {
            this.showError('No se puede generar informe para este diagnóstico');
            return;
        }

        this.generateReportBtn.disabled = true;
        this.generateReportBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Generando...';

        try {
            const response = await fetch('/api/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    diagnostico: this.currentAnalysis.diagnostico,
                    confianza: this.currentAnalysis.confianza,
                    datosAdicionales: {
                        porcentaje: this.currentAnalysis.porcentaje,
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.displayReport(result.informe);
            } else {
                throw new Error(result.error || 'Error al generar informe');
            }

        } catch (error) {
            console.error('Error al generar informe:', error);
            this.showError('Error al generar informe: ' + error.message);
        } finally {
            this.generateReportBtn.disabled = false;
            this.generateReportBtn.innerHTML = '<i class="bi bi-file-plus me-2"></i>Generar Informe';
        }
    }

    displayReport(informe) {
        this.reportSummary.textContent = informe.resumenEjecutivo;
        this.reportFull.innerHTML = this.formatReportText(informe.informeCompleto);
        this.reportRecommendations.innerHTML = this.formatReportText(informe.recomendaciones);
        
        const timestamp = new Date(informe.metadatos.fechaGeneracion);
        this.reportTimestamp.textContent = `Generado el ${timestamp.toLocaleDateString('es-ES')} a las ${timestamp.toLocaleTimeString('es-ES')}`;
        
        this.reportContent.classList.remove('d-none');
        
        // Scroll suave al informe
        this.reportContent.scrollIntoView({ behavior: 'smooth' });
    }

    formatReportText(text) {
        // Formatear texto del informe con saltos de línea y estilos básicos
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    showLoading(show) {
        if (show) {
            this.loadingSpinner.style.display = 'block';
            this.resultsSection.classList.add('d-none');
        } else {
            this.loadingSpinner.style.display = 'none';
        }
    }

    showError(message) {
        // Crear alerta de error
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insertar después del botón de análisis
        const analyzeButtonContainer = this.analyzeBtn.closest('.text-center');
        analyzeButtonContainer.parentNode.insertBefore(alertDiv, analyzeButtonContainer.nextSibling);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        // Crear alerta de éxito
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
        alertDiv.innerHTML = `
            <i class="bi bi-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insertar después del botón de análisis
        const analyzeButtonContainer = this.analyzeBtn.closest('.text-center');
        analyzeButtonContainer.parentNode.insertBefore(alertDiv, analyzeButtonContainer.nextSibling);

        // Auto-remover después de 3 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }

    resetResults() {
        this.resultsSection.classList.add('d-none');
        this.reportContent.classList.add('d-none');
        this.reportSection.style.display = 'none';
        
        // Limpiar clases de diagnóstico
        const resultCard = document.querySelector('.result-card');
        if (resultCard) {
            resultCard.classList.remove('diagnosis-positive', 'diagnosis-negative');
        }
        
        this.currentAnalysis = null;
    }

    // Método para reiniciar la aplicación
    reset() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.fileInfo.classList.add('d-none');
        this.imagePreview.classList.add('d-none');
        this.analyzeBtn.disabled = true;
        this.resetResults();
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando RADOX App...');
    window.radoxApp = new RadoxApp();
    console.log('✅ RADOX App inicializada correctamente');
});

// Manejo de errores globales
window.addEventListener('error', (e) => {
    console.error('Error global en la aplicación:', e.error);
});

// Manejo de errores de promesas no capturadas
window.addEventListener('unhandledrejection', (e) => {
    console.error('Promesa rechazada no manejada:', e.reason);
}); 