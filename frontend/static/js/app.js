// RADOX - Frontend JavaScript
// Sistema de Detección de Neumonía con IA

class RadoxApp {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.currentFile = null;
        this.currentResults = null;
        this.uploadProgress = 0;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.checkApiHealth();
    }

    // Event Listeners Setup
    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }

        // Upload area click
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('click', () => {
                document.getElementById('file-input').click();
            });
        }

        // Window resize for responsive handling
        window.addEventListener('resize', () => this.handleResize());
    }

    // Drag and Drop Setup
    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');
        if (!uploadArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlight(uploadArea), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.unhighlight(uploadArea), false);
        });

        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(element) {
        element.classList.add('dragover');
    }

    unhighlight(element) {
        element.classList.remove('dragover');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            this.handleFileSelect({ target: { files: files } });
        }
    }

    // File Handling
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file
        if (!this.validateFile(file)) {
            return;
        }

        this.currentFile = file;
        this.displayFileInfo(file);
        this.enableAnalyzeButton();
    }

    validateFile(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'image/jpeg', 
            'image/jpg', 
            'image/png', 
            'application/dicom',
            'application/octet-stream' // DICOM files might appear as this
        ];

        // Check file size
        if (file.size > maxSize) {
            this.showError('El archivo es demasiado grande. Máximo 50MB permitido.');
            return false;
        }

        // Check file extension for DICOM files
        const fileName = file.name.toLowerCase();
        const validExtensions = ['.jpg', '.jpeg', '.png', '.dicom', '.dcm'];
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

        if (!allowedTypes.includes(file.type) && !hasValidExtension) {
            this.showError('Formato de archivo no soportado. Use JPG, PNG o DICOM.');
            return false;
        }

        return true;
    }

    displayFileInfo(file) {
        const fileInfo = document.getElementById('file-info');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');

        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            fileInfo.classList.remove('d-none');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    enableAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.classList.add('pulse');
        }
    }

    clearFile() {
        this.currentFile = null;
        const fileInput = document.getElementById('file-input');
        const fileInfo = document.getElementById('file-info');
        const analyzeBtn = document.getElementById('analyze-btn');

        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.classList.add('d-none');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.classList.remove('pulse');
        }
    }

    // API Functions
    async checkApiHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();
            
            if (health.status === 'healthy') {
                console.log('✅ API está funcionando correctamente');
            } else {
                console.warn('⚠️ API en estado degradado:', health);
                this.showWarning('El sistema está en estado degradado. Algunas funciones pueden estar limitadas.');
            }
        } catch (error) {
            console.error('❌ Error al conectar con la API:', error);
            this.showError('No se puede conectar con el servidor. Verifique su conexión.');
        }
    }

    async analyzeImage() {
        if (!this.currentFile) {
            this.showError('Por favor seleccione una imagen primero.');
            return;
        }

        try {
            this.showLoading();
            this.hideResults();

            // Prepare form data
            const formData = new FormData();
            formData.append('file', this.currentFile);

            // Get patient info
            const patientInfo = this.getPatientInfo();
            if (patientInfo && Object.keys(patientInfo).length > 0) {
                formData.append('patient_info', JSON.stringify(patientInfo));
            }

            // Eliminar o comentar referencias a casos similares en la UI y llamadas API

            // Start progress simulation
            this.simulateProgress();

            // Make API request
            const response = await fetch(`${this.apiBaseUrl}/detect`, {
                method: 'POST',
                body: formData
            });

            this.stopProgress();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en el análisis');
            }

            const results = await response.json();
            this.currentResults = results;

            // Display results
            this.displayResults(results);

            // Generate medical report if requested
            if (generateReport) {
                await this.generateMedicalReport(results);
            }

            this.hideLoading();

        } catch (error) {
            console.error('Error en análisis:', error);
            this.hideLoading();
            this.showError(`Error en el análisis: ${error.message}`);
        }
    }

    getPatientInfo() {
        const age = document.getElementById('patient-age')?.value;
        const gender = document.getElementById('patient-gender')?.value;
        const symptoms = document.getElementById('patient-symptoms')?.value;

        const info = {};
        if (age) info.age = parseInt(age);
        if (gender) info.gender = gender;
        if (symptoms) info.symptoms = symptoms.trim();

        return Object.keys(info).length > 0 ? info : null;
    }

    // Progress Simulation
    simulateProgress() {
        this.uploadProgress = 0;
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');

        const steps = [
            { progress: 20, text: 'Cargando imagen...' },
            { progress: 40, text: 'Preprocesando imagen...' },
            { progress: 60, text: 'Ejecutando modelo CNN...' },
            { progress: 80, text: 'Buscando casos similares...' },
            { progress: 95, text: 'Finalizando análisis...' }
        ];

        let currentStep = 0;
        this.progressInterval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                this.uploadProgress = step.progress;
                
                if (progressBar) {
                    progressBar.style.width = `${this.uploadProgress}%`;
                }
                if (progressText) {
                    progressText.textContent = step.text;
                }
                currentStep++;
            }
        }, 1000);
    }

    stopProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = '100%';
        }
        if (progressText) {
            progressText.textContent = 'Análisis completado';
        }
    }

    // Results Display
    displayResults(results) {
        const prediction = results.prediction;
        const caseData = results.case_data;

        // Update diagnosis
        this.updateDiagnosis(prediction);

        // Update probability (prob_neumonia)
        this.updateProbability(prediction);

        // Update heatmap
        this.updateHeatmap(prediction);

        // Update recommendation
        this.updateRecommendation(prediction);

        // Update image preview
        this.updateImagePreview(results);

        // Show results section
        this.showResults();
    }

    updateDiagnosis(prediction) {
        const diagnosisText = document.getElementById('diagnosis-text');
        const diagnosisIcon = document.getElementById('diagnosis-icon');

        // Usar prob_neumonia explícitamente
        const prob = prediction.prob_neumonia !== undefined ? prediction.prob_neumonia : (prediction.probNeumonia !== undefined ? prediction.probNeumonia : 0);
        const hasPneumonia = prob >= 0.5;
        const predictedClass = hasPneumonia ? 'Neumonía' : 'Normal';

        if (diagnosisText && diagnosisIcon) {
            diagnosisText.textContent = predictedClass;
            if (hasPneumonia) {
                diagnosisIcon.className = 'fas fa-exclamation-triangle fa-2x text-warning';
                diagnosisText.className = 'text-warning';
            } else {
                diagnosisIcon.className = 'fas fa-check-circle fa-2x text-success';
                diagnosisText.className = 'text-success';
            }
        }
    }

    updateProbability(prediction) {
        const confidenceText = document.getElementById('confidence-text');
        // Usar prob_neumonia explícitamente
        const prob = prediction.prob_neumonia !== undefined ? prediction.prob_neumonia : (prediction.probNeumonia !== undefined ? prediction.probNeumonia : 0);
        if (confidenceText) {
            confidenceText.innerHTML = `
                <span class="fw-bold">${(prob * 100).toFixed(1)}%</span>
                <small class="d-block text-muted">Probabilidad de Neumonía</small>
            `;
        }
    }

    updateHeatmap(prediction) {
        const heatmapContainer = document.getElementById('heatmap-container');
        if (heatmapContainer && prediction.heatmap) {
            heatmapContainer.innerHTML = `<img src="data:image/png;base64,${prediction.heatmap}" alt="Heatmap" class="img-fluid rounded" style="max-width: 100%;"/>`;
        } else if (heatmapContainer) {
            heatmapContainer.innerHTML = '<span class="text-muted">No disponible</span>';
        }
    }

    updateRecommendation(prediction) {
        const recommendationText = document.getElementById('recommendation-text');
        const recommendationAlert = document.getElementById('recommendation-alert');

        if (recommendationText && recommendationAlert) {
            recommendationText.textContent = prediction.recommendation;
            
            // Update alert class based on pneumonia detection
            recommendationAlert.className = prediction.has_pneumonia 
                ? 'alert alert-warning' 
                : 'alert alert-info';
        }
    }

    updateDetailedResults(prediction, processingInfo) {
        // Class probabilities
        const classProbabilities = document.getElementById('class-probabilities');
        if (classProbabilities && prediction.class_probabilities) {
            let html = '';
            for (const [className, probability] of Object.entries(prediction.class_probabilities)) {
                const percent = (probability * 100).toFixed(1);
                html += `
                    <div class="mb-2">
                        <div class="d-flex justify-content-between">
                            <span>${className}:</span>
                            <span>${percent}%</span>
                        </div>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar" style="width: ${percent}%"></div>
                        </div>
                    </div>
                `;
            }
            classProbabilities.innerHTML = html;
        }

        // Processing info
        const processingInfoElement = document.getElementById('processing-info');
        if (processingInfoElement && processingInfo) {
            processingInfoElement.innerHTML = `
                <p><strong>Formato:</strong> ${processingInfo.image_format?.toUpperCase()}</p>
                <p><strong>Modelo:</strong> ${processingInfo.model_version}</p>
                <p><strong>DICOM:</strong> ${processingInfo.has_dicom_metadata ? 'Sí' : 'No'}</p>
            `;
        }
    }

    updateImagePreview(results) {
        const analyzedImage = document.getElementById('analyzed-image');
        const imageDetails = document.getElementById('image-details');

        if (analyzedImage && this.currentFile) {
            const reader = new FileReader();
            reader.onload = (e) => {
                analyzedImage.src = e.target.result;
            };
            reader.readAsDataURL(this.currentFile);
        }

        if (imageDetails) {
            imageDetails.textContent = `Archivo: ${results.filename} | Caso ID: ${results.case_id}`;
        }
    }

    // Eliminar o comentar referencias a casos similares en la UI y llamadas API

    async generateMedicalReport(results) {
        try {
            console.log('LOG FRONTEND: results recibido en generateMedicalReport:', results);
            const reportRequest = {
                diagnostico: results.resultado?.diagnostico,
                confianza: results.resultado?.confianza,
                datosAdicionales: {
                    porcentaje: results.resultado?.porcentaje,
                    timestamp: results.timestamp
                },
                imagePath: results.resultado?.imagePath
            };
            console.log('LOG FRONTEND: reportRequest a /api/generate-report:', reportRequest);
            const response = await fetch('/api/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reportRequest)
            });

            if (!response.ok) {
                throw new Error('Error al generar informe médico');
            }

            const reportData = await response.json();
            this.displayMedicalReport(reportData);

        } catch (error) {
            console.error('Error generando informe:', error);
            this.showWarning('No se pudo generar el informe médico automáticamente.');
        }
    }

    displayMedicalReport(reportData) {
        const reportContent = document.getElementById('medical-report-content');
        if (!reportContent) return;

        // Format the report for display
        const fullReport = reportData.full_report;
        const sections = reportData.report_sections || {};

        let formattedReport = `
            <div class="report-header">
                <h1>INFORME RADIOLÓGICO</h1>
                <p><strong>Caso ID:</strong> ${reportData.case_id}</p>
                <p><strong>Fecha:</strong> ${new Date(reportData.timestamp).toLocaleString()}</p>
                <p><strong>Generado por:</strong> ${reportData.generated_by}</p>
            </div>
        `;

        // Add sections if available
        if (Object.keys(sections).length > 0) {
            for (const [sectionKey, sectionContent] of Object.entries(sections)) {
                const sectionTitle = this.getSectionTitle(sectionKey);
                formattedReport += `
                    <div class="report-section">
                        <h3>${sectionTitle}</h3>
                        <p>${sectionContent}</p>
                    </div>
                `;
            }
        } else {
            // Use full report if sections not available
            formattedReport += `<div class="report-section">${fullReport}</div>`;
        }

        // Add disclaimer
        formattedReport += `
            <div class="report-footer">
                <p><small>${reportData.medical_disclaimer}</small></p>
            </div>
        `;

        reportContent.innerHTML = formattedReport;
        this.showMedicalReport();
    }

    getSectionTitle(sectionKey) {
        const titles = {
            'datos_paciente': 'DATOS DEL PACIENTE',
            'tecnica': 'TÉCNICA DE ESTUDIO',
            'hallazgos': 'HALLAZGOS RADIOLÓGICOS',
            'impresion': 'IMPRESIÓN DIAGNÓSTICA',
            'recomendaciones': 'RECOMENDACIONES CLÍNICAS',
            'notas': 'NOTAS ADICIONALES'
        };
        return titles[sectionKey] || sectionKey.toUpperCase();
    }

    // UI State Management
    showLoading() {
        document.getElementById('upload')?.classList.add('d-none');
        document.getElementById('loading')?.classList.remove('d-none');
    }

    hideLoading() {
        document.getElementById('loading')?.classList.add('d-none');
    }

    showResults() {
        document.getElementById('results')?.classList.remove('d-none');
        document.getElementById('results')?.classList.add('fade-in');
        
        // Smooth scroll to results
        document.getElementById('results')?.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    hideResults() {
        document.getElementById('results')?.classList.add('d-none');
        document.getElementById('similar-cases')?.classList.add('d-none');
        document.getElementById('medical-report')?.classList.add('d-none');
    }

    // Eliminar o comentar referencias a casos similares en la UI y llamadas API

    showMedicalReport() {
        document.getElementById('medical-report')?.classList.remove('d-none');
        document.getElementById('medical-report')?.classList.add('fade-in');
    }

    // Error Handling
    showError(message) {
        this.showModal('Error', message, 'danger');
    }

    showWarning(message) {
        this.showModal('Advertencia', message, 'warning');
    }

    showSuccess(message) {
        this.showModal('Éxito', message, 'success');
    }

    showModal(title, message, type = 'info') {
        const modal = document.getElementById('errorModal');
        const modalTitle = modal?.querySelector('.modal-title');
        const modalBody = modal?.querySelector('.modal-body p');
        const modalHeader = modal?.querySelector('.modal-header');

        if (modal && modalTitle && modalBody && modalHeader) {
            modalTitle.innerHTML = `<i class="fas fa-${this.getIconForType(type)} me-2"></i>${title}`;
            modalBody.textContent = message;
            
            // Update header class
            modalHeader.className = `modal-header bg-${type} text-white`;
            
            // Show modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    getIconForType(type) {
        const icons = {
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'success': 'check-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility Functions
    downloadReport() {
        if (!this.currentResults) {
            this.showError('No hay informe para descargar.');
            return;
        }

        const reportContent = document.getElementById('medical-report-content');
        if (!reportContent) {
            this.showError('No se puede acceder al contenido del informe.');
            return;
        }

        // Create downloadable content
        const reportData = {
            case_id: this.currentResults.case_id,
            timestamp: new Date().toISOString(),
            report_html: reportContent.innerHTML,
            diagnosis: this.currentResults.prediction.predicted_class,
            confidence: this.currentResults.prediction.confidence
        };

        const dataStr = JSON.stringify(reportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `informe_${this.currentResults.case_id}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        this.showSuccess('Informe descargado correctamente.');
    }

    handleResize() {
        // Handle responsive behavior if needed
        console.log('Window resized');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.radoxApp = new RadoxApp();
});

// Global functions for onclick handlers
function clearFile() {
    if (window.radoxApp) {
        window.radoxApp.clearFile();
    }
}

function analyzeImage() {
    if (window.radoxApp) {
        window.radoxApp.analyzeImage();
    }
}

function downloadReport() {
    if (window.radoxApp) {
        window.radoxApp.downloadReport();
    }
} 