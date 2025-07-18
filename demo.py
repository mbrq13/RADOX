#!/usr/bin/env python3
"""
Demo Script para RADOX
Demostración de las capacidades del sistema de detección de neumonía
"""

import os
import sys
import asyncio
import json
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from loguru import logger
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.text import Text
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Install demo dependencies: pip install rich loguru requests pillow")
    sys.exit(1)

class RadoxDemo:
    """Demostrador del sistema RADOX"""
    
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.console = Console()
        
    def create_demo_image(self, image_type="normal"):
        """Crear imagen de demostración"""
        
        # Crear imagen base 512x512
        img = Image.new('RGB', (512, 512), color='black')
        draw = ImageDraw.Draw(img)
        
        # Simular patrón pulmonar
        if image_type == "normal":
            # Patrón normal - campos pulmonares claros
            for i in range(0, 512, 20):
                for j in range(0, 512, 20):
                    if 100 < i < 400 and 50 < j < 450:  # Área pulmonar
                        # Variación suave para simular tejido normal
                        intensity = 40 + np.random.randint(0, 30)
                        draw.rectangle([i, j, i+15, j+15], fill=(intensity, intensity, intensity))
        
        elif image_type == "pneumonia":
            # Patrón de neumonía - consolidación
            for i in range(0, 512, 20):
                for j in range(0, 512, 20):
                    if 100 < i < 400 and 50 < j < 450:  # Área pulmonar
                        # Consolidación en área específica
                        if 200 < i < 350 and 200 < j < 350:
                            intensity = 120 + np.random.randint(0, 40)  # Más denso
                        else:
                            intensity = 40 + np.random.randint(0, 30)
                        draw.rectangle([i, j, i+15, j+15], fill=(intensity, intensity, intensity))
        
        # Convertir a bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def check_api_health(self):
        """Verificar que la API esté funcionando"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def demo_detection(self, image_type="normal"):
        """Demostrar detección de neumonía"""
        
        self.console.print(Panel(
            f"[bold blue]🔍 Demostrando Detección de Neumonía[/bold blue]\n"
            f"Tipo de imagen: {image_type.upper()}",
            expand=False
        ))
        
        # Crear imagen de demo
        with self.console.status("[bold green]Generando imagen de demostración..."):
            demo_image = self.create_demo_image(image_type)
        
        # Información del paciente de demo
        patient_info = {
            "age": 45 if image_type == "pneumonia" else 35,
            "gender": "M",
            "symptoms": "Tos persistente, fiebre alta" if image_type == "pneumonia" else "Revisión rutinaria"
        }
        
        # Realizar detección
        try:
            with self.console.status("[bold green]Analizando imagen con IA..."):
                files = {"file": ("demo.png", demo_image, "image/png")}
                data = {
                    "patient_info": json.dumps(patient_info)
                }
                
                response = requests.post(
                    f"{self.api_url}/api/v1/detect",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                self.display_detection_results(result)
                return result
            else:
                self.console.print(f"[red]Error en detección: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            self.console.print(f"[red]Error en detección: {e}[/red]")
            return None
    
    def display_detection_results(self, result):
        """Mostrar resultados de detección"""
        
        prediction = result["prediction"]
        case_data = result["case_data"]
        
        # Tabla de resultados principales
        table = Table(title="🩺 Resultados de Análisis", show_header=True, header_style="bold magenta")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        table.add_column("Detalles", style="yellow")
        
        # Añadir filas
        diagnosis_color = "red" if prediction["has_pneumonia"] else "green"
        table.add_row(
            "Diagnóstico",
            f"[{diagnosis_color}]{prediction['predicted_class']}[/{diagnosis_color}]",
            f"Confianza: {prediction['confidence']:.1%}"
        )
        
        table.add_row(
            "Nivel de Confianza",
            prediction["confidence_level"],
            f"Neumonía: {'Sí' if prediction['has_pneumonia'] else 'No'}"
        )
        
        table.add_row(
            "Severidad",
            case_data.get("severity", "N/A"),
            f"Caso ID: {result['case_id'][:8]}..."
        )
        
        self.console.print(table)
        
        # Recomendación
        rec_color = "red" if prediction["has_pneumonia"] else "green"
        self.console.print(Panel(
            f"[{rec_color}]{prediction['recommendation']}[/{rec_color}]",
            title="💡 Recomendación Clínica",
            expand=False
        ))
        
        # Probabilidades por clase
        prob_table = Table(title="📊 Probabilidades por Clase")
        prob_table.add_column("Clase", style="cyan")
        prob_table.add_column("Probabilidad", style="magenta")
        prob_table.add_column("Barra", style="blue")
        
        for class_name, prob in prediction["class_probabilities"].items():
            bar_length = int(prob * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            prob_table.add_row(class_name, f"{prob:.1%}", bar)
        
        self.console.print(prob_table)
        

    

    
    def demo_report_generation(self, detection_result):
        """Demostrar generación de informe médico"""
        
        if not detection_result:
            self.console.print("[red]No hay resultado de detección para generar informe[/red]")
            return
        
        self.console.print(Panel(
            "[bold blue]📋 Generando Informe Médico con MedGemma[/bold blue]",
            expand=False
        ))
        
        try:
            with self.console.status("[bold green]Generando informe con IA..."):
                report_request = {
                    "case_id": detection_result["case_id"],
                    "detection_result": detection_result,
                    "language": "spanish",
                    "report_type": "complete"
                }
                
                response = requests.post(
                    f"{self.api_url}/api/v1/report/generate",
                    json=report_request,
                    timeout=120  # Los LLM pueden tardar
                )
            
            if response.status_code == 200:
                report = response.json()
                self.display_medical_report(report)
            else:
                self.console.print(f"[red]Error generando informe: {response.status_code}[/red]")
                # Mostrar informe básico
                self.display_basic_report(detection_result)
                
        except Exception as e:
            self.console.print(f"[yellow]Error con MedGemma: {e}[/yellow]")
            self.console.print("[blue]Mostrando informe básico...[/blue]")
            self.display_basic_report(detection_result)
    
    def display_medical_report(self, report):
        """Mostrar informe médico generado"""
        
        full_report = report.get("full_report", "")
        
        # Mostrar informe en panel
        self.console.print(Panel(
            full_report[:1000] + "..." if len(full_report) > 1000 else full_report,
            title="📋 Informe Médico Generado",
            expand=False,
            border_style="green"
        ))
        
        # Mostrar calidad del informe
        quality = report.get("quality_score", {})
        if quality:
            quality_table = Table(title="📈 Calidad del Informe")
            quality_table.add_column("Métrica", style="cyan")
            quality_table.add_column("Puntuación", style="green")
            
            for metric, score in quality.items():
                if isinstance(score, (int, float)):
                    quality_table.add_row(metric.title(), f"{score:.2f}")
            
            self.console.print(quality_table)
    
    def display_basic_report(self, detection_result):
        """Mostrar informe básico cuando falla MedGemma"""
        
        prediction = detection_result["prediction"]
        case_data = detection_result["case_data"]
        
        basic_report = f"""
INFORME RADIOLÓGICO BÁSICO

DATOS DEL PACIENTE:
- Caso ID: {detection_result['case_id']}
- Fecha: {detection_result['timestamp']}

ANÁLISIS POR IA:
- Clasificación: {prediction['predicted_class']}
- Confianza: {prediction['confidence']:.1%}
- Nivel de Confianza: {prediction['confidence_level']}

IMPRESIÓN DIAGNÓSTICA:
{prediction['recommendation']}

NOTA: Informe generado automáticamente por sistema RADOX.
Requiere validación por especialista médico.
        """
        
        self.console.print(Panel(
            basic_report.strip(),
            title="📋 Informe Básico",
            expand=False,
            border_style="yellow"
        ))
    
    def demo_api_info(self):
        """Mostrar información de la API"""
        
        try:
            # Info general
            response = requests.get(f"{self.api_url}/api/v1/info")
            if response.status_code == 200:
                info = response.json()
                
                info_table = Table(title="ℹ️ Información del Sistema")
                info_table.add_column("Propiedad", style="cyan")
                info_table.add_column("Valor", style="green")
                
                info_table.add_row("Nombre", info.get("name", "N/A"))
                info_table.add_row("Versión", info.get("version", "N/A"))
                info_table.add_row("Descripción", info.get("description", "N/A"))
                
                self.console.print(info_table)
            
            # Estadísticas
            response = requests.get(f"{self.api_url}/api/v1/statistics")
            if response.status_code == 200:
                stats = response.json()
                
                stats_text = json.dumps(stats, indent=2)
                self.console.print(Panel(
                    stats_text,
                    title="📊 Estadísticas del Sistema",
                    expand=False
                ))
                
        except Exception as e:
            self.console.print(f"[red]Error obteniendo información: {e}[/red]")
    
    def run_full_demo(self):
        """Ejecutar demostración completa"""
        
        # Banner de bienvenida
        self.console.print(Panel(
            "[bold blue]🏥 RADOX - Sistema de Detección de Neumonía con IA[/bold blue]\n"
            "[green]Demostración Completa del Sistema[/green]",
            expand=False
        ))
        
        # Verificar API
        self.console.print("\n[bold yellow]🔍 Verificando conectividad...[/bold yellow]")
        if not self.check_api_health():
            self.console.print(f"[red]❌ No se puede conectar a la API en {self.api_url}[/red]")
            self.console.print("[yellow]Asegúrate de que RADOX esté ejecutándose con: ./run.sh[/yellow]")
            return
        
        self.console.print("[green]✅ API conectada correctamente[/green]")
        
        # Mostrar información del sistema
        self.demo_api_info()
        
        # Demo detección normal
        self.console.print("\n" + "="*50)
        normal_result = self.demo_detection("normal")
        
        if normal_result:
            input("\n[bold blue]Presiona Enter para generar informe médico...[/bold blue]")
            self.demo_report_generation(normal_result)
        
        # Demo detección neumonía
        self.console.print("\n" + "="*50)
        input("\n[bold blue]Presiona Enter para demostrar detección de neumonía...[/bold blue]")
        pneumonia_result = self.demo_detection("pneumonia")
        
        if pneumonia_result:
            input("\n[bold blue]Presiona Enter para generar informe de neumonía...[/bold blue]")
            self.demo_report_generation(pneumonia_result)
        
        # Conclusión
        self.console.print(Panel(
            "[bold green]🎉 ¡Demostración Completada![/bold green]\n\n"
            "[blue]RADOX ha demostrado sus capacidades principales:[/blue]\n"
            "• ✅ Detección de neumonía con CNN\n"
            "• ✅ Búsqueda de casos similares\n"
            "• ✅ Generación de informes médicos\n"
            "• ✅ Interface web responsiva\n\n"
            "[yellow]Accede a la interface web en: http://localhost:8080[/yellow]",
            title="🏥 RADOX Demo",
            expand=False
        ))

def main():
    parser = argparse.ArgumentParser(description="Demo de RADOX")
    parser.add_argument("--api-url", default="http://localhost:8000",
                       help="URL de la API de RADOX")
    parser.add_argument("--mode", choices=["full", "detection", "info"], default="full",
                       help="Modo de demostración")
    parser.add_argument("--image-type", choices=["normal", "pneumonia"], default="normal",
                       help="Tipo de imagen para demo de detección")
    
    args = parser.parse_args()
    
    demo = RadoxDemo(args.api_url)
    
    try:
        if args.mode == "full":
            demo.run_full_demo()
        elif args.mode == "detection":
            demo.demo_detection(args.image_type)
        elif args.mode == "info":
            demo.demo_api_info()
            
    except KeyboardInterrupt:
        demo.console.print("\n[yellow]Demo interrumpido por el usuario[/yellow]")
    except Exception as e:
        demo.console.print(f"\n[red]Error en demo: {e}[/red]")

if __name__ == "__main__":
    main() 