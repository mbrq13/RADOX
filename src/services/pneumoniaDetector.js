const { spawn } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

class PneumoniaDetector {
    constructor() {
        this.isInitialized = false;
        this.modelPath = process.env.CNN_MODEL_PATH || './data/models/pneumonia_resnet50.h5';
        this.pythonBridgePath = './scripts/python_cnn_bridge.py';
    }

    async initialize() {
        try {
            console.log('🧠 Cargando modelo CNN para detección de neumonía...');
            console.log('🔗 Conectando con modelo Python existente...');

            if (!await fs.pathExists(this.pythonBridgePath)) {
                throw new Error(`Script puente no encontrado en: ${this.pythonBridgePath}`);
            }

            const initResult = await this.callPythonBridge('init');

            if (!initResult.success) {
                console.warn('⚠️  Modelo Python no disponible, usando modelo mock...');
                console.warn(`Razón: ${initResult.error}`);
                this.useMockModel = true;
            } else {
                console.log('✅ Modelo CNN Python conectado exitosamente');
                console.log(`📊 Info del modelo: ${initResult.model_info?.architecture}`);
                this.useMockModel = false;
            }

            this.isInitialized = true;
            console.log('✅ Detector de neumonía inicializado');

        } catch (error) {
            console.error('❌ Error al cargar modelo CNN:', error);
            console.log('🔄 Continuando con modelo mock para demostración...');
            this.useMockModel = true;
            this.isInitialized = true;
        }
    }

    async callPythonBridge(action, imagePath = null) {
        return new Promise((resolve, reject) => {
            const args = [this.pythonBridgePath, '--action', action];
            if (imagePath) args.push('--image', imagePath);
            if (this.modelPath) args.push('--model-path', this.modelPath);

            console.log(`🐍 Ejecutando: python ${args.join(' ')}`);

            const py = spawn('python', args);
            let stdout = '';
            let stderr = '';

            py.stdout.on('data', d => stdout += d.toString());
            py.stderr.on('data', d => stderr += d.toString());

            py.on('close', code => {
                if (code !== 0) {
                    console.error(`❌ Proceso Python terminó con código ${code}`);
                    console.error(stderr);
                    return reject(new Error(`Python failed: ${stderr}`));
                }
                try {
                    resolve(JSON.parse(stdout));
                } catch (err) {
                    console.error('❌ Error parsing JSON from Python:', err);
                    console.error('stdout:', stdout);
                    reject(err);
                }
            });
            py.on('error', reject);
        });
    }

    async predict(imagePath) {
        if (!this.isInitialized) throw new Error('El detector no está inicializado');

        if (this.useMockModel) {
            return this.mockPredict(imagePath);
        } else {
            // return this.pythonPredict(imagePath); // <-- Comento la llamada al modelo CNN
            // Simulo una predicción positiva para que se genere el informe con MedGemma
            return {
                label: 'Neumonía',
                confidence: 0.85,
                rawPredictions: [1.2, -0.5],
                classProbabilities: { 'Neumonía': 0.85, 'Normal': 0.15 },
                probNeumonia: 0.85,
                hasNeumonía: true,
                heatmap: null,
                caseId: 'case_mock',
                modelInfo: { status: 'mock', architecture: 'mock', device: 'cpu', num_classes: 2 }
            };
        }
    }

    async pythonPredict(imagePath) {
        console.log('🔍 Ejecutando predicción con modelo Python...');

        const result = await this.callPythonBridge('predict', imagePath);
        if (!result.success) {
            throw new Error(result.error || 'Predicción Python falló');
        }

        const p = result.prediction;

        // 1) Salida cruda de la capa final
        if (p.raw_predictions !== undefined) {
            console.log('📊 Raw predictions:', p.raw_predictions);
        } else {
            console.log('📊 Raw predictions: (no disponible en la respuesta)');
        }
        // 2) Probabilidades por clase
        console.log('📊 Class probabilities:', p.class_probabilities);
        // 3) Diagnóstico y probabilidad de neumonía
        console.log(`📊 Diagnóstico: ${p.predicted_class || p.label} | P(neumonía) = ${(p.prob_neumonia * 100).toFixed(2)}%`);
        // 4) Heatmap (tamaño)
        if (p.heatmap) {
            console.log(`📊 Heatmap shape: ${p.heatmap.length}×${p.heatmap[0].length}`);
        }

        return {
            label: p.predicted_class || p.label,
            confidence: p.confidence,
            rawPredictions: p.raw_predictions,
            classProbabilities: p.class_probabilities,
            probNeumonia: p.prob_neumonia,
            hasNeumonía: p.has_pneumonia,
            heatmap: p.heatmap,
            caseId: result.case_id,
            modelInfo: result.model_info
        };
    }

    // ... mockPredict(), getConfidenceLevel(), getRecommendation(), etc.
}

module.exports = PneumoniaDetector;
 