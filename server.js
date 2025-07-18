// server.js

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const multer = require('multer');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config({ path: './config.env' });

const PneumoniaDetector = require('./src/services/pneumoniaDetector');
const ReportGenerator   = require('./src/services/reportGenerator');
const ImageProcessor    = require('./src/utils/imageProcessor');

class RadoxServer {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3000;
    this.pneumoniaDetector = new PneumoniaDetector();
    this.reportGenerator   = new ReportGenerator();
    this.imageProcessor    = new ImageProcessor();

    this.setupMiddleware();
    this.setupRoutes();
    this.ensureDirectories();
  }

  setupMiddleware() {
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
      credentials: true
    }));
    const limiter = rateLimit({
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) * 60 * 1000,
      max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS),
      message: 'Demasiadas solicitudes, intenta de nuevo más tarde.'
    });
    this.app.use('/api/', limiter);
    this.app.use(morgan('combined'));
    this.app.use(express.json({ limit: '1mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '1mb' }));
    this.app.use(express.static('public'));
    this.app.use('/uploads', express.static(process.env.UPLOAD_DIR || './uploads'));

    const storage = multer.diskStorage({
      destination: (req, file, cb) => {
        cb(null, process.env.UPLOAD_DIR || './uploads');
      },
      filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
      }
    });

    this.upload = multer({
      storage,
      limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760 },
      fileFilter: (req, file, cb) => {
        const allowed = /jpeg|jpg|png|dicom|dcm/;
        const extname = allowed.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowed.test(file.mimetype) || file.mimetype === 'application/dicom';
        if (mimetype && extname) cb(null, true);
        else cb(new Error('Solo se permiten archivos de imagen (JPG, PNG) o DICOM'));
      }
    });
  }

  setupRoutes() {
    this.app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, 'public', 'index.html'));
    });

    this.app.get('/health', (req, res) => {
      res.json({ status: 'OK', message: 'RADOX API funcionando correctamente', timestamp: new Date().toISOString(), version: '1.0.0' });
    });

    // ─── ANALIZAR RADIÓGRAFÍA ───────────────────────────────────────────────────
    this.app.post('/api/analyze', this.upload.single('radiografia'), async (req, res) => {
      try {
        if (!req.file) {
          return res.status(400).json({ error: 'No se proporcionó ningún archivo de imagen' });
        }

        console.log(`🔍 Analizando imagen: ${req.file.filename}`);

        // Procesar imagen
        const processedImagePath = await this.imageProcessor.processImage(req.file.path);

        console.log('→ processedImagePath:', processedImagePath);

        // Detectar neumonía
        const prediction = await this.pneumoniaDetector.predict(processedImagePath);

        console.log('→ prediction:', prediction);

        // Limpiar archivo original
        await fs.remove(req.file.path);

        const responseObj = {
          success: true,
          resultado: {
            diagnostico: prediction.label,
            confianza:  prediction.confidence,
            porcentaje:  Math.round(prediction.confidence * 100),
            tieneNeumonía: prediction.label === 'Neumonía',
            puedeGenerarInforme: prediction.label === 'Neumonía'
              && prediction.confidence >= parseFloat(process.env.CONFIDENCE_THRESHOLD),
            imagePath: processedImagePath     // <— aquí chequeamos que no sea undefined
          },
          timestamp: new Date().toISOString()
        };

        console.log('LOG /api/analyze responseObj:', responseObj);
        res.json(responseObj);

      } catch (error) {
        console.error('❌ Error al analizar imagen:', error);
        if (req.file && req.file.path) {
          await fs.remove(req.file.path).catch(() => {});
        }
        res.status(500).json({ error: 'Error interno al analizar la imagen', message: error.message });
      }
    });

    // ─── GENERAR INFORME MÉDICO ─────────────────────────────────────────────────
    this.app.post('/api/generate-report', async (req, res) => {
      console.log('BODY /api/generate-report →', req.body);
      // Si no llega imagePath, busca el archivo procesado más reciente
      if (!req.body.imagePath) {
        const fs = require('fs');
        const path = require('path');
        const uploadsDir = process.env.UPLOAD_DIR || './uploads';
        let latestFile = null;
        let latestMtime = 0;
        try {
          const files = fs.readdirSync(uploadsDir)
            .filter(f => f.endsWith('.jpeg') || f.endsWith('.jpg') || f.endsWith('.png'));
          for (const file of files) {
            const filePath = path.join(uploadsDir, file);
            const stat = fs.statSync(filePath);
            if (stat.mtimeMs > latestMtime) {
              latestMtime = stat.mtimeMs;
              latestFile = filePath;
            }
          }
          if (latestFile) {
            req.body.imagePath = latestFile;
            console.log('🛠️ Forzando imagePath al archivo más reciente:', latestFile);
          } else {
            console.log('❌ No se encontró ningún archivo procesado en uploads/');
          }
        } catch (e) {
          console.log('❌ Error buscando archivo procesado más reciente:', e);
        }
      }
      try {
        const { diagnostico, confianza, datosAdicionales, imagePath } = req.body;

        if (!diagnostico || diagnostico !== 'Neumonía') {
          return res.status(400).json({ error: 'Solo se pueden generar informes para neumonía' });
        }
        if (confianza < parseFloat(process.env.CONFIDENCE_THRESHOLD)) {
          return res.status(400).json({ error: `Confianza mínima ${process.env.CONFIDENCE_THRESHOLD}` });
        }

        console.log('📝 Generando informe, imagePath recibido:', imagePath);

        const informe = await this.reportGenerator.generateReport({
          diagnostico,
          confianza,
          datosAdicionales: datosAdicionales || {},
          imagePath      // <— asegúrate que el bridge reciba esto
        });

        res.json({ success: true, informe, timestamp: new Date().toISOString() });

      } catch (error) {
        console.error('❌ Error al generar informe:', error);
        res.status(500).json({ error: 'Error al generar informe médico', message: error.message });
      }
    });

    // 404 + manejo global
    this.app.use('*', (req, res) => {
      res.status(404).json({ error: 'Endpoint no encontrado' });
    });
    this.app.use((err, req, res, next) => {
      console.error('Error global:', err);
      res.status(500).json({ error: 'Error interno', message: err.message });
    });
  }

  async ensureDirectories() {
    const dirs = [ process.env.UPLOAD_DIR || './uploads', process.env.MODELS_DIR || './models', './logs' ];
    for (const d of dirs) await fs.ensureDir(d);
  }

  async start() {
    try {
      console.log('🚀 Inicializando RADOX...');
      await this.pneumoniaDetector.initialize();
      console.log('✅ Detector de neumonía listo');
      await this.reportGenerator.initialize();
      console.log('✅ Generador de informes listo');
      this.app.listen(this.port, () => {
        console.log(`🏥 API escuchando en http://localhost:${this.port}`);
      });
    } catch (err) {
      console.error('❌ Error al iniciar RADOX:', err);
      process.exit(1);
    }
  }
}

const server = new RadoxServer();
server.start();

module.exports = RadoxServer;
