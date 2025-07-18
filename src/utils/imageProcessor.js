const sharp = require('sharp');
const fs = require('fs-extra');
const path = require('path');

class ImageProcessor {
    constructor() {
        this.supportedFormats = ['.jpg', '.jpeg', '.png', '.dcm', '.dicom'];
        this.targetSize = parseInt(process.env.IMAGE_SIZE) || 224;
        this.outputFormat = 'jpeg';
        this.quality = 90;
    }

    async processImage(inputPath) {
        try {
            console.log('🖼️  Procesando imagen:', path.basename(inputPath));

            // Verificar que el archivo existe
            if (!await fs.pathExists(inputPath)) {
                throw new Error(`Archivo no encontrado: ${inputPath}`);
            }

            // Determinar el tipo de archivo
            const fileExtension = path.extname(inputPath).toLowerCase();
            
            if (!this.supportedFormats.includes(fileExtension)) {
                throw new Error(`Formato de archivo no soportado: ${fileExtension}`);
            }

            // Procesar según el tipo de archivo
            let processedPath;
            
            if (fileExtension === '.dcm' || fileExtension === '.dicom') {
                processedPath = await this.processDicomImage(inputPath);
            } else {
                processedPath = await this.processStandardImage(inputPath);
            }

            console.log('✅ Imagen procesada exitosamente');
            console.log('[DEBUG] Imagen procesada guardada en:', processedPath);
            const exists = await fs.pathExists(processedPath);
            console.log('[DEBUG] ¿Existe el archivo procesado?:', exists);
            return processedPath;

        } catch (error) {
            console.error('❌ Error al procesar imagen:', error);
            throw error;
        }
    }

    async processStandardImage(inputPath) {
        try {
            const outputPath = this.generateOutputPath(inputPath);

            // Procesar imagen con Sharp
            await sharp(inputPath)
                .resize(this.targetSize, this.targetSize, {
                    fit: 'cover',
                    position: 'center'
                })
                .grayscale() // Convertir a escala de grises para radiografías
                .normalize() // Normalizar contraste
                .jpeg({ quality: this.quality })
                .toFile(outputPath);

            return outputPath;

        } catch (error) {
            throw new Error(`Error al procesar imagen estándar: ${error.message}`);
        }
    }

    async processDicomImage(inputPath) {
        try {
            console.log('⚕️  Procesando imagen DICOM...');
            
            // Nota: Para procesar DICOM reales, necesitarías una librería como 'dicom-parser'
            // Por ahora, trataremos los archivos DICOM como imágenes estándar
            console.log('⚠️  Procesamiento DICOM simplificado - usa dicom-parser para funcionalidad completa');
            
            // Intentar procesar como imagen estándar
            return await this.processStandardImage(inputPath);

        } catch (error) {
            throw new Error(`Error al procesar imagen DICOM: ${error.message}`);
        }
    }

    async processDicomWithParser(inputPath) {
        // Función placeholder para procesamiento DICOM real
        // Requiere instalación de 'dicom-parser' o 'cornerstone-core'
        
        try {
            // const dicomParser = require('dicom-parser');
            // const dataSet = dicomParser.parseDicom(fs.readFileSync(inputPath));
            // 
            // // Extraer imagen pixel data
            // const pixelData = dataSet.elements.x7fe00010;
            // 
            // // Procesar datos de píxeles...
            
            console.log('📋 Funcionalidad DICOM completa no implementada aún');
            return await this.processStandardImage(inputPath);
            
        } catch (error) {
            throw new Error(`Error en procesamiento DICOM avanzado: ${error.message}`);
        }
    }

    generateOutputPath(inputPath) {
        const dir = path.dirname(inputPath);
        const name = path.basename(inputPath, path.extname(inputPath));
        const timestamp = Date.now();
        
        return path.join(dir, `${name}_processed_${timestamp}.${this.outputFormat}`);
    }

    async validateImage(imagePath) {
        try {
            const metadata = await sharp(imagePath).metadata();
            
            const validation = {
                isValid: true,
                format: metadata.format,
                width: metadata.width,
                height: metadata.height,
                channels: metadata.channels,
                size: (await fs.stat(imagePath)).size,
                errors: []
            };

            // Validaciones básicas
            if (metadata.width < 100 || metadata.height < 100) {
                validation.errors.push('Imagen demasiado pequeña (mínimo 100x100)');
            }

            if (validation.size > parseInt(process.env.MAX_FILE_SIZE || 10485760)) {
                validation.errors.push('Archivo demasiado grande');
            }

            if (!['jpeg', 'jpg', 'png'].includes(metadata.format)) {
                validation.errors.push('Formato de imagen no estándar');
            }

            validation.isValid = validation.errors.length === 0;
            
            return validation;

        } catch (error) {
            return {
                isValid: false,
                errors: [`Error al validar imagen: ${error.message}`]
            };
        }
    }

    async enhanceRadiographImage(imagePath) {
        try {
            console.log('✨ Mejorando calidad de radiografía...');
            
            const outputPath = this.generateOutputPath(imagePath);

            await sharp(imagePath)
                .resize(this.targetSize, this.targetSize, {
                    fit: 'cover',
                    position: 'center'
                })
                .grayscale()
                .normalize() // Mejorar contraste
                .sharpen() // Aplicar sharpening
                .gamma(1.2) // Ajustar gamma para mejor visualización
                .jpeg({ quality: 95 })
                .toFile(outputPath);

            return outputPath;

        } catch (error) {
            throw new Error(`Error al mejorar radiografía: ${error.message}`);
        }
    }

    async extractImageStats(imagePath) {
        try {
            const metadata = await sharp(imagePath).metadata();
            const stats = await sharp(imagePath).stats();

            return {
                formato: metadata.format,
                dimensiones: `${metadata.width}x${metadata.height}`,
                canales: metadata.channels,
                espacio: metadata.space,
                estadisticas: {
                    promedio: stats.channels?.map(ch => ch.mean),
                    desviacion: stats.channels?.map(ch => ch.std),
                    minimo: stats.channels?.map(ch => ch.min),
                    maximo: stats.channels?.map(ch => ch.max)
                }
            };

        } catch (error) {
            throw new Error(`Error al extraer estadísticas: ${error.message}`);
        }
    }

    async cleanup(filePath) {
        try {
            if (await fs.pathExists(filePath)) {
                await fs.remove(filePath);
                console.log('🗑️  Archivo temporal limpiado:', path.basename(filePath));
            }
        } catch (error) {
            console.warn('⚠️  No se pudo limpiar archivo temporal:', error.message);
        }
    }

    getSupportedFormats() {
        return this.supportedFormats;
    }

    getProcessingInfo() {
        return {
            formatosSoportados: this.supportedFormats,
            tamañoObjetivo: `${this.targetSize}x${this.targetSize}`,
            formatoSalida: this.outputFormat,
            calidad: this.quality
        };
    }
}

module.exports = ImageProcessor; 