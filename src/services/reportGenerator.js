const axios = require('axios');
const { spawn } = require('child_process');

class ReportGenerator {
    constructor() {
        this.apiToken = process.env.HUGGINGFACE_TOKEN;
        this.modelName = process.env.MEDGEMMA_MODEL || 'google/medgemma-7b';
        this.apiUrl = `https://api-inference.huggingface.co/models/${this.modelName}`;
        this.isInitialized = false;
        this.maxRetries = 3;
        this.retryDelay = 2000; // 2 segundos
    }

    async initialize() {
        try {
            console.log('📝 Inicializando generador de informes médicos...');
            console.log('DEBUG TOKEN:', this.apiToken);
            console.log('DEBUG API URL:', this.apiUrl);

            if (!this.apiToken || this.apiToken === 'your_hf_token_here' || this.apiToken === 'your2_hf_token_here') {
                console.log('⚠️  Token de Hugging Face no configurado - usando modo fallback');
                this.isInitialized = true;
                console.log('✅ Generador de informes inicializado en modo fallback');
                return;
            }

            // Si el modelo es medgemma-4b-it, saltar el test de conexión REST
            if ((this.modelName || '').toLowerCase() === 'google/medgemma-4b-it') {
                this.isInitialized = true;
                console.log('✅ Generador de informes inicializado (modo MedGemma 4b-it)');
                return;
            }

            // Verificar conexión con la API solo si tenemos token real y modelo REST
            try {
                await this.testConnection();
            } catch (err) {
                console.log('⚠️  Error conectando con Hugging Face API - usando modo fallback');
                console.log('DEBUG ERROR:', err);
                this.isInitialized = true;
                return;
            }

            this.isInitialized = true;
            console.log('✅ Generador de informes inicializado');
        } catch (err) {
            console.log('❌ Error inicializando generador de informes:', err);
            this.isInitialized = false;
        }
    }
    
    async testConnection() {
        try {
            const response = await axios.post(
                this.apiUrl,
                { inputs: 'Test connection' },
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiToken}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000
                }
            );

            console.log('✅ Conexión con Hugging Face API verificada');
            return true;

        } catch (error) {
            if (error.response?.status === 503) {
                console.log('⏳ Modelo cargándose en Hugging Face, esto es normal...');
                return true;
            }
            throw new Error(`Error de conexión con Hugging Face: ${error.message}`);
        }
    }

    async generateReport(analysisData) {
        if ((this.modelName || '').toLowerCase() === 'google/medgemma-4b-it') {
            // Construir prompt médico especializado
            const prompt = this.buildMedicalPrompt(
                analysisData.diagnostico,
                analysisData.confianza,
                analysisData.datosAdicionales
            );
            // Usar la ruta local de la imagen procesada
            const imagePath = analysisData.imagePath || analysisData.imagenPath || analysisData.image_path;
            if (!imagePath) throw new Error('No se proporcionó la ruta local de la imagen para MedGemma 4b-it');
            const informe = await this.generateReportWithMedGemma4bIT(prompt, imagePath);
            console.log('📝 INFORME GENERADO POR MEDGEMMA:\n' + informe);
            return informe;
        }

        if (!this.isInitialized) {
            throw new Error('El generador de informes no está inicializado');
        }

        // Si no tenemos token válido, usar directamente fallback
        if (!this.apiToken || this.apiToken === 'your_hf_token_here' || this.apiToken === 'your2_hf_token_here') {
            console.log('📋 Generando informe médico básico (modo demo)...');
            return this.generateFallbackReport(analysisData); // Pass prompt to fallback
        }

        try {
            console.log('📋 Generando informe médico con MedGemma...');

            // Generar informe con reintentos
            const informe = await this.generateWithRetry(analysisData);

            // Procesar y estructurar el informe
            const informeEstructurado = this.processReport(informe, analysisData);

            console.log('✅ Informe médico generado exitosamente');
            return informeEstructurado;

        } catch (error) {
            console.error('❌ Error al generar informe:', error);

            // Fallback: generar informe básico
            console.log('🔄 Usando informe básico como alternativa...');
            return this.generateFallbackReport(analysisData); // Pass prompt to fallback
        }
    }

    async generateReportWithMedGemma4bIT(prompt, imagePath) {
        return new Promise((resolve, reject) => {
            const py = spawn('python3', [
                './scripts/medgemma4b_report.py',
                '--prompt', prompt,
                '--image-path', imagePath
            ], {
                env: { ...process.env, HF_TOKEN: this.apiToken }
            });
            let output = '';
            let error = '';
            py.stdout.on('data', (data) => { output += data.toString(); });
            py.stderr.on('data', (data) => { error += data.toString(); });
            py.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error('Error Python: ' + error));
                }
            });
        });
    }

    buildMedicalPrompt(diagnostico, confianza, datosAdicionales) {
        if ((this.modelName || '').toLowerCase() === 'google/medgemma-4b-it') {
            return 'Por favor, genera un informe médico detallado sobre la presencia o ausencia de neumonía en la radiografía proporcionada. No utilices información adicional, solo analiza la imagen.';
        }
        const confianzaPorcentaje = Math.round(confianza * 100);

        const prompt = `Como médico especialista en radiología, genera un informe médico detallado para la siguiente radiografía de tórax:

RESULTADO DEL ANÁLISIS:
- Diagnóstico: ${diagnostico}
- Nivel de confianza: ${confianzaPorcentaje}%
- Fecha del análisis: ${new Date().toLocaleDateString('es-ES')}

INSTRUCCIONES:
1. Genera un informe médico profesional en español
2. Incluye hallazgos radiológicos específicos
3. Proporciona recomendaciones clínicas
4. Mantén un tono profesional y médico
5. El informe debe tener máximo 300 palabras

ESTRUCTURA REQUERIDA:
- Hallazgos radiológicos
- Impresión diagnóstica
- Recomendaciones

Informe médico:`;

        return prompt;
    }

    async generateWithRetry(analysisData) {
        let lastError;

        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`📤 Enviando prompt a MedGemma (intento ${attempt}/${this.maxRetries})...`);

                const prompt = this.buildMedicalPrompt(
                    analysisData.diagnostico,
                    analysisData.confianza,
                    analysisData.datosAdicionales
                );
                const imageUrl = analysisData.imageUrl || analysisData.imagenUrl || analysisData.image_url;

                const response = await axios.post(
                    this.apiUrl,
                    {
                        inputs: prompt,
                        parameters: {
                            max_new_tokens: 400,
                            temperature: 0.3,
                            top_p: 0.9,
                            do_sample: true,
                            return_full_text: false
                        }
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${this.apiToken}`,
                            'Content-Type': 'application/json'
                        },
                        timeout: 30000 // 30 segundos
                    }
                );

                if (response.data && response.data[0] && response.data[0].generated_text) {
                    return response.data[0].generated_text.trim();
                }

                throw new Error('Respuesta vacía de la API');

            } catch (error) {
                lastError = error;
                console.warn(`⚠️  Intento ${attempt} falló:`, error.message);

                if (error.response?.status === 503) {
                    console.log('⏳ Modelo cargándose, esperando antes del siguiente intento...');
                    await this.sleep(this.retryDelay * attempt);
                } else if (attempt < this.maxRetries) {
                    await this.sleep(this.retryDelay);
                }
            }
        }

        throw lastError;
    }

    processReport(rawReport, analysisData) {
        const { diagnostico, confianza } = analysisData;

        return {
            resumenEjecutivo: `Análisis radiológico computarizado detectó ${diagnostico.toLowerCase()} con ${Math.round(confianza * 100)}% de confianza.`,
            informeCompleto: rawReport,
            hallazgos: this.extractFindings(rawReport),
            recomendaciones: this.extractRecommendations(rawReport),
            metadatos: {
                fechaGeneracion: new Date().toISOString(),
                modeloIA: this.modelName,
                confianzaDeteccion: confianza,
                diagnosticoIA: diagnostico,
                version: '1.0.0'
            },
            disclaimer: 'Este informe fue generado por inteligencia artificial y debe ser revisado por un profesional médico cualificado antes de tomar decisiones clínicas.'
        };
    }

    extractFindings(report) {
        // Extraer hallazgos del informe usando patrones de texto
        const findingsSection = report.match(/hallazgos[\s\S]*?(?=recomendaciones|impresión|$)/i);
        return findingsSection ? findingsSection[0].trim() : 'Ver informe completo';
    }

    extractRecommendations(report) {
        // Extraer recomendaciones del informe
        const recommendationsSection = report.match(/recomendaciones[\s\S]*$/i);
        return recommendationsSection ? recommendationsSection[0].trim() : 'Consultar con especialista en neumología';
    }

    generateFallbackReport(analysisData) {
        const { diagnostico, confianza } = analysisData;
        const confianzaPorcentaje = Math.round(confianza * 100);

        console.log('📋 Generando informe básico de demostración...');

        const informeBasico = `
INFORME RADIOLÓGICO AUTOMATIZADO - VERSIÓN DEMO

HALLAZGOS RADIOLÓGICOS:
El análisis computarizado de la radiografía de tórax mediante red neuronal convolucional revela hallazgos compatibles con ${diagnostico.toLowerCase()}. El sistema ha identificado patrones radiológicos que sugieren la presencia de cambios en el parénquima pulmonar.

IMPRESIÓN DIAGNÓSTICA:
- Diagnóstico por IA: ${diagnostico}
- Nivel de confianza: ${confianzaPorcentaje}%
- Análisis realizado con modelo CNN especializado
- Fecha y hora del análisis: ${new Date().toLocaleString('es-ES')}

RECOMENDACIONES CLÍNICAS:
1. **Correlación clínica obligatoria** - Los hallazgos deben ser interpretados en el contexto clínico del paciente
2. **Evaluación por especialista** - Se recomienda revisión por radiólogo o neumólogo
3. **Estudios complementarios** - Considerar TC de tórax si está clínicamente indicado
4. **Seguimiento médico** - Establecer plan de seguimiento según protocolo institucional
5. **Historia clínica** - Correlacionar con síntomas, signos vitales y laboratorios

LIMITACIONES DEL SISTEMA:
- Este análisis es una herramienta de apoyo diagnóstico
- No reemplaza el criterio médico profesional
- Requiere validación por especialista cualificado

NOTA: Este es un informe automatizado generado para fines de demostración y prueba del sistema RADOX.
        `.trim();

        return {
            resumenEjecutivo: `Sistema de IA detectó ${diagnostico.toLowerCase()} con ${confianzaPorcentaje}% de confianza. Requiere validación médica profesional.`,
            informeCompleto: informeBasico,
            hallazgos: `Análisis automatizado sugiere hallazgos compatibles con ${diagnostico.toLowerCase()}. Confianza del sistema: ${confianzaPorcentaje}%`,
            recomendaciones: 'Evaluación médica profesional OBLIGATORIA para confirmación diagnóstica. Este resultado es solo de apoyo y no constituye diagnóstico médico definitivo.',
            metadatos: {
                fechaGeneracion: new Date().toISOString(),
                modeloIA: 'Sistema RADOX Demo',
                confianzaDeteccion: confianza,
                diagnosticoIA: diagnostico,
                version: '1.0.0',
                tipoInforme: 'Demostración'
            },
            disclaimer: '⚠️ IMPORTANTE: Este informe fue generado en modo demostración. Para uso clínico real, configure el token de Hugging Face válido. Este resultado NO debe usarse para tomar decisiones médicas.'
        };
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getStatus() {
        return {
            inicializado: this.isInitialized,
            modelo: this.modelName,
            tieneToken: !!this.apiToken && this.apiToken !== 'your_hf_token_here',
            url: this.apiUrl
        };
    }
}

module.exports = ReportGenerator; 