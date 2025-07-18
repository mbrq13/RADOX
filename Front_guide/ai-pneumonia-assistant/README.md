# Asistente IA para Neumonía - Demo Simulado

Una aplicación web moderna para la detección de neumonía mediante inteligencia artificial, construida con Next.js, React y Tailwind CSS. **Esta es una versión completamente simulada con fines demostrativos.**

## 🎯 Características

- **Subida Drag & Drop**: Fácil carga de radiografías de tórax con vista previa
- **Análisis IA Simulado**: Detección de neumonía en tiempo real con puntuación de confianza
- **Reportes Médicos**: Reportes detallados generados por IA simulada
- **Diseño Responsivo**: Funciona perfectamente en escritorio y móvil
- **Interfaz Moderna**: Interfaz limpia y profesional con animaciones suaves
- **Completamente Simulado**: No requiere backend real, todo funciona con datos ficticios

## 🛠️ Stack Tecnológico

- **Frontend**: Next.js 14, React, TypeScript
- **Estilos**: Tailwind CSS, shadcn/ui components
- **Simulación**: Datos ficticios realistas con delays auténticos
- **Despliegue**: Configuración lista para Vercel

## 🚀 Inicio Rápido

### Prerrequisitos

- Node.js 18+
- npm o yarn

### Instalación

1. Clona el repositorio:
\`\`\`bash
git clone <repository-url>
cd ai-pneumonia-assistant-demo
\`\`\`

2. Instala las dependencias:
\`\`\`bash
npm install
\`\`\`

3. Inicia el servidor de desarrollo:
\`\`\`bash
npm run dev
\`\`\`

4. Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## 🎮 Cómo Usar la Demo

1. **Subir Imagen**: Arrastra y suelta una imagen de rayos X o haz clic para seleccionar
2. **Análisis**: El sistema simulará el análisis con IA (2-4 segundos)
3. **Resultados**: Verás el diagnóstico y nivel de confianza simulados
4. **Generar Reporte**: Crea un reporte médico detallado (3-5 segundos)
5. **Descargar/Copiar**: Guarda o copia el reporte generado

## 📊 Funcionalidades de Simulación

### Análisis IA Simulado
- Genera diagnósticos aleatorios pero realistas
- Niveles de confianza variables (10-95%)
- Diferentes escenarios: Normal, Posible Neumonía, Neumonía Detectada
- Tiempos de procesamiento realistas

### Reportes Médicos Simulados
- Reportes detallados basados en el diagnóstico
- Formato médico profesional
- Recomendaciones específicas según el resultado
- Información de metadata completa

## 🎨 Características de la Interfaz

- **Navegación Intuitiva**: Sidebar con pasos claros
- **Indicadores de Progreso**: Barras de progreso durante el procesamiento
- **Medidores de Confianza**: Visualización clara de los niveles de riesgo
- **Avisos de Demo**: Recordatorios claros de que es una simulación
- **Responsive Design**: Adaptable a todos los tamaños de pantalla

## 📱 Estructura del Proyecto

\`\`\`
├── app/
│   ├── page.tsx              # Componente principal de la aplicación
│   └── layout.tsx            # Layout raíz
├── components/
│   ├── upload-section.tsx    # Componente de subida de archivos
│   ├── analysis-display.tsx  # Componente de visualización de resultados
│   ├── report-view.tsx       # Componente de visualización de reportes
│   └── ui/                   # Componentes shadcn/ui
├── lib/
│   └── simulation.ts         # Lógica de simulación completa
└── public/                   # Recursos estáticos
\`\`\`

## 🔧 Personalización

### Modificar Escenarios de Simulación

Edita `lib/simulation.ts` para:
- Cambiar los tipos de diagnóstico
- Ajustar niveles de confianza
- Modificar el contenido de los reportes
- Personalizar tiempos de procesamiento

### Estilos y Tema

- Utiliza Tailwind CSS para modificaciones de estilo
- Los componentes shadcn/ui son completamente personalizables
- Colores y tipografía definidos en `tailwind.config.ts`

## 🚀 Despliegue

### Vercel (Recomendado)

1. Sube tu código a GitHub
2. Conecta tu repositorio a Vercel
3. Despliega automáticamente

### Otros Proveedores

La aplicación es compatible con cualquier proveedor que soporte Next.js:
- Netlify
- Railway
- DigitalOcean App Platform

## ⚠️ Aviso Importante

**Esta es una aplicación de demostración únicamente.** 

- Todos los resultados son ficticios
- No debe usarse para diagnósticos médicos reales
- Los reportes son generados aleatoriamente
- Siempre consulte con profesionales médicos calificados

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Prueba exhaustivamente
5. Envía un pull request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT.

---

**Desarrollado con ❤️ para demostrar las capacidades de IA en diagnóstico médico**
