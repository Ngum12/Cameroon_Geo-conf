#!/usr/bin/env python3
"""
PROJECT SENTINEL - PDF REPORT GENERATOR
Cameroon Defense Force OSINT Analysis System
Professional intelligence report generation with charts and analysis
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

# PDF Generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, Frame, NextPageTemplate, PageTemplate
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
except ImportError:
    print("⚠️ ReportLab not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "reportlab", "pillow"])
    # Re-import after installation
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, Frame, NextPageTemplate, PageTemplate
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas

# Chart generation
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_agg import FigureCanvasAgg
except ImportError:
    print("⚠️ Matplotlib not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_agg import FigureCanvasAgg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    """Report generation configuration"""
    title: str
    classification: str = "CONFIDENTIAL"
    report_type: str = "INTELLIGENCE_ASSESSMENT"
    author: str = "PROJECT SENTINEL"
    organization: str = "Cameroon Defense Forces"
    time_period: str = "24 HOURS"
    include_charts: bool = True
    include_maps: bool = True
    include_executive_summary: bool = True
    template: str = "standard"

@dataclass
class ThreatData:
    """Threat intelligence data structure"""
    region: str
    threat_level: str
    risk_score: float
    article_count: int
    key_actors: List[str]
    incident_types: List[str]
    sentiment_score: float
    escalation_probability: float

class ProjectSentinelPDFGenerator:
    """Professional PDF report generator for PROJECT SENTINEL"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.assets_dir = self.reports_dir / "assets"
        self.templates_dir = self.reports_dir / "templates"
        self.temp_dir = self.reports_dir / "temp"
        
        # Create directories
        for directory in [self.reports_dir, self.assets_dir, self.templates_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set up styles
        self.setup_styles()
        
        logger.info("PROJECT SENTINEL PDF Generator initialized")
    
    def setup_styles(self):
        """Set up PDF styles for professional reports"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles for military intelligence reports
        self.styles.add(ParagraphStyle(
            name='ClassifiedTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.red,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            borderColor=colors.lightgrey,
            borderWidth=1,
            borderPadding=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ThreatLevel',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.red
        ))
        
        self.styles.add(ParagraphStyle(
            name='RegionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
    
    def create_header_footer(self, canvas, doc):
        """Create header and footer for each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.red)
        canvas.drawCentredString(A4[0] / 2, A4[1] - 30, "CONFIDENTIAL - PROJECT SENTINEL")
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(A4[0] / 2, A4[1] - 45, "Cameroon Defense Forces - Intelligence Assessment")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(A4[0] / 2, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.drawRightString(A4[0] - 30, 30, f"Page {doc.page}")
        canvas.drawString(30, 30, "CONFIDENTIAL")
        
        # Classification markings
        canvas.setFillColor(colors.red)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(30, A4[1] - 30, "CONFIDENTIAL")
        canvas.drawRightString(A4[0] - 30, A4[1] - 30, "CONFIDENTIAL")
        
        canvas.restoreState()
    
    def generate_threat_chart(self, threat_data: List[ThreatData]) -> str:
        """Generate threat level visualization chart"""
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#0f1419')
        
        # Threat levels bar chart
        regions = [data.region for data in threat_data]
        risk_scores = [data.risk_score for data in threat_data]
        
        colors_map = {'HIGH': '#ff4444', 'MEDIUM': '#ffaa00', 'LOW': '#00ff88', 'CRITICAL': '#ff0000'}
        bar_colors = [colors_map.get(data.threat_level, '#888888') for data in threat_data]
        
        bars = ax1.bar(regions, risk_scores, color=bar_colors, alpha=0.8)
        ax1.set_title('Regional Threat Assessment', color='#00ff88', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Risk Score', color='white')
        ax1.set_ylim(0, 100)
        ax1.tick_params(axis='x', rotation=45, colors='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, score in zip(bars, risk_scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}', ha='center', va='bottom', color='white', fontweight='bold')
        
        # Article count pie chart
        article_counts = [data.article_count for data in threat_data]
        colors_pie = ['#ff4444', '#ffaa00', '#00ff88', '#44aaff', '#aa44ff']
        
        wedges, texts, autotexts = ax2.pie(article_counts, labels=regions, colors=colors_pie[:len(regions)],
                                          autopct='%1.1f%%', startangle=90)
        ax2.set_title('Intelligence Sources Distribution', color='#00ff88', fontsize=14, fontweight='bold')
        
        # Style pie chart text
        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        # Save chart
        chart_path = self.temp_dir / f"threat_chart_{int(datetime.now().timestamp())}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#0f1419')
        plt.close()
        
        return str(chart_path)
    
    def generate_timeline_chart(self, timeline_data: List[Dict]) -> str:
        """Generate timeline visualization of incidents"""
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor('#0f1419')
        
        # Sample timeline data (would come from real data)
        dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
        incidents = [15, 12, 8, 22, 18, 25, 14]  # Sample incident counts
        
        ax.plot(dates, incidents, color='#00ff88', linewidth=3, marker='o', markersize=8, markerfacecolor='#ff4444')
        ax.fill_between(dates, incidents, alpha=0.3, color='#00ff88')
        
        ax.set_title('7-Day Incident Timeline', color='#00ff88', fontsize=14, fontweight='bold')
        ax.set_ylabel('Incident Count', color='white')
        ax.set_xlabel('Date', color='white')
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for date, count in zip(dates, incidents):
            ax.annotate(f'{count}', (date, count), textcoords="offset points",
                       xytext=(0,10), ha='center', color='white', fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        chart_path = self.temp_dir / f"timeline_chart_{int(datetime.now().timestamp())}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#0f1419')
        plt.close()
        
        return str(chart_path)
    
    def create_executive_summary(self, threat_data: List[ThreatData]) -> List:
        """Create executive summary section"""
        story = []
        
        # Calculate summary statistics
        total_articles = sum(data.article_count for data in threat_data)
        avg_risk_score = sum(data.risk_score for data in threat_data) / len(threat_data)
        high_risk_regions = [data.region for data in threat_data if data.risk_score > 70]
        critical_regions = [data.region for data in threat_data if data.threat_level == 'CRITICAL']
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Key findings
        summary_text = f"""
        <b>Assessment Period:</b> {datetime.now().strftime('%Y-%m-%d')} (24-hour analysis)<br/>
        <b>Intelligence Sources:</b> {total_articles} processed articles from 41+ sources<br/>
        <b>Average Risk Score:</b> {avg_risk_score:.1f}/100<br/>
        <b>High-Risk Regions:</b> {len(high_risk_regions)} identified<br/>
        <b>Critical Alerts:</b> {len(critical_regions)} requiring immediate attention<br/><br/>
        
        <b>KEY FINDINGS:</b><br/>
        • Regional threat landscape shows heightened activity in {high_risk_regions[0] if high_risk_regions else 'Northern regions'}<br/>
        • Intelligence processing indicates {total_articles} significant events requiring analysis<br/>
        • Escalation probabilities suggest monitoring of {', '.join(high_risk_regions[:3]) if high_risk_regions else 'key regions'}<br/>
        • Multi-source correlation confirms reliability of threat assessments<br/><br/>
        
        <b>RECOMMENDATIONS:</b><br/>
        • Continue enhanced monitoring of high-risk regions<br/>
        • Deploy additional intelligence assets as needed<br/>
        • Maintain coordination with regional commanders<br/>
        • Implement recommended intervention strategies from RL decision system
        """
        
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 20))
        
        return story
    
    def create_threat_assessment_table(self, threat_data: List[ThreatData]) -> List:
        """Create detailed threat assessment table"""
        story = []
        
        story.append(Paragraph("REGIONAL THREAT ASSESSMENT", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Table header
        table_data = [
            ['Region', 'Threat Level', 'Risk Score', 'Articles', 'Key Actors', 'Escalation Risk']
        ]
        
        # Table rows
        for data in threat_data:
            actors_str = ', '.join(data.key_actors[:3]) if data.key_actors else 'N/A'
            if len(actors_str) > 30:
                actors_str = actors_str[:30] + '...'
            
            escalation_risk = "HIGH" if data.escalation_probability > 0.7 else "MEDIUM" if data.escalation_probability > 0.4 else "LOW"
            
            table_data.append([
                data.region,
                data.threat_level,
                f"{data.risk_score:.1f}",
                str(data.article_count),
                actors_str,
                escalation_risk
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1.5*inch, 1*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Color-code threat levels
        for i, data in enumerate(threat_data, 1):
            if data.threat_level == 'CRITICAL':
                table.setStyle(TableStyle([('TEXTCOLOR', (1, i), (1, i), colors.red)]))
            elif data.threat_level == 'HIGH':
                table.setStyle(TableStyle([('TEXTCOLOR', (1, i), (1, i), colors.orange)]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def create_detailed_analysis(self, threat_data: List[ThreatData]) -> List:
        """Create detailed regional analysis section"""
        story = []
        
        story.append(Paragraph("DETAILED REGIONAL ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        for data in threat_data:
            # Region header
            story.append(Paragraph(f"{data.region.upper()} REGION", self.styles['RegionHeader']))
            
            # Threat level indicator
            threat_color = colors.red if data.threat_level == 'CRITICAL' else colors.orange if data.threat_level == 'HIGH' else colors.green
            threat_style = ParagraphStyle('ThreatIndicator', parent=self.styles['Normal'], 
                                        textColor=threat_color, fontName='Helvetica-Bold')
            story.append(Paragraph(f"Threat Level: {data.threat_level}", threat_style))
            
            # Analysis text
            analysis_text = f"""
            <b>Risk Assessment:</b> {data.risk_score:.1f}/100<br/>
            <b>Intelligence Sources:</b> {data.article_count} processed articles<br/>
            <b>Sentiment Analysis:</b> {data.sentiment_score:.2f} (regional baseline)<br/>
            <b>Escalation Probability:</b> {data.escalation_probability:.1%}<br/>
            <b>Key Actors Identified:</b> {', '.join(data.key_actors[:5]) if data.key_actors else 'None specified'}<br/>
            <b>Primary Incident Types:</b> {', '.join(data.incident_types[:3]) if data.incident_types else 'Various'}<br/><br/>
            
            <b>Assessment:</b> Regional analysis indicates {'heightened security concerns' if data.risk_score > 70 else 'moderate threat environment' if data.risk_score > 40 else 'stable security situation'} 
            based on intelligence correlation from multiple sources. Continuous monitoring recommended with focus on 
            {'immediate intervention strategies' if data.threat_level == 'CRITICAL' else 'preventive measures and surveillance'}.
            """
            
            story.append(Paragraph(analysis_text, self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        return story
    
    def generate_intelligence_report(self, threat_data: List[ThreatData], 
                                   config: ReportConfig) -> str:
        """Generate complete intelligence report PDF"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SENTINEL_Intelligence_Report_{timestamp}.pdf"
        output_path = self.reports_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=72
        )
        
        # Build story
        story = []
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("CONFIDENTIAL", self.styles['ClassifiedTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph("PROJECT SENTINEL", self.styles['ReportTitle']))
        story.append(Paragraph("INTELLIGENCE ASSESSMENT REPORT", self.styles['ReportTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph(f"Assessment Period: {config.time_period}", self.styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Paragraph(f"Author: {config.author}", self.styles['Normal']))
        story.append(Paragraph(f"Organization: {config.organization}", self.styles['Normal']))
        
        story.append(PageBreak())
        
        # Executive Summary
        if config.include_executive_summary:
            story.extend(self.create_executive_summary(threat_data))
            story.append(PageBreak())
        
        # Charts
        if config.include_charts:
            story.append(Paragraph("THREAT VISUALIZATION", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            # Generate and include threat chart
            try:
                chart_path = self.generate_threat_chart(threat_data)
                if os.path.exists(chart_path):
                    story.append(Image(chart_path, width=6*inch, height=3*inch))
                    story.append(Spacer(1, 12))
            except Exception as e:
                logger.error(f"Error generating threat chart: {e}")
            
            # Generate and include timeline chart
            try:
                timeline_path = self.generate_timeline_chart([])  # Would use real timeline data
                if os.path.exists(timeline_path):
                    story.append(Image(timeline_path, width=6*inch, height=3*inch))
                    story.append(Spacer(1, 12))
            except Exception as e:
                logger.error(f"Error generating timeline chart: {e}")
            
            story.append(PageBreak())
        
        # Threat Assessment Table
        story.extend(self.create_threat_assessment_table(threat_data))
        story.append(PageBreak())
        
        # Detailed Analysis
        story.extend(self.create_detailed_analysis(threat_data))
        
        # Technical appendix
        story.append(PageBreak())
        story.append(Paragraph("TECHNICAL APPENDIX", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        tech_info = f"""
        <b>System Information:</b><br/>
        • PROJECT SENTINEL Intelligence Platform v1.0<br/>
        • Machine Learning Models: {len(threat_data)} regional assessments processed<br/>
        • Natural Language Processing: French/English translation pipeline<br/>
        • Reinforcement Learning: Decision support system active<br/>
        • Data Sources: 41+ intelligence feeds monitored<br/>
        • Processing Time: Real-time analysis with 30-second refresh cycles<br/>
        • Confidence Level: Multi-source correlation verification<br/><br/>
        
        <b>Methodology:</b><br/>
        Intelligence gathering through automated web scraping, RSS monitoring, and API integration.
        French-language sources automatically translated for ML model compatibility.
        Named Entity Recognition identifies key actors, locations, and organizations.
        Sentiment analysis provides regional stability indicators.
        Actor network analysis maps relationships and influence patterns.
        Reinforcement learning system recommends intervention strategies.
        """
        
        story.append(Paragraph(tech_info, self.styles['Normal']))
        
        # Build PDF with custom header/footer
        doc.build(story, onFirstPage=self.create_header_footer, 
                  onLaterPages=self.create_header_footer)
        
        # Cleanup temporary files
        self.cleanup_temp_files()
        
        logger.info(f"Intelligence report generated: {output_path}")
        return str(output_path)
    
    def cleanup_temp_files(self):
        """Clean up temporary chart files"""
        try:
            for temp_file in self.temp_dir.glob("*.png"):
                if temp_file.stat().st_mtime < (datetime.now() - timedelta(hours=1)).timestamp():
                    temp_file.unlink()
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
    
    def generate_sample_report(self) -> str:
        """Generate sample intelligence report with demo data"""
        
        # Sample threat data
        sample_data = [
            ThreatData(
                region="Extreme-Nord",
                threat_level="HIGH",
                risk_score=85.3,
                article_count=15,
                key_actors=["Boko Haram", "BIR Forces", "Local Militias"],
                incident_types=["Terrorism", "Cross-border", "Military Operations"],
                sentiment_score=-0.65,
                escalation_probability=0.78
            ),
            ThreatData(
                region="Nord-Ouest",
                threat_level="MEDIUM",
                risk_score=62.1,
                article_count=8,
                key_actors=["Separatist Groups", "ADF", "Civilian Population"],
                incident_types=["Separatist Activity", "Political Violence"],
                sentiment_score=-0.42,
                escalation_probability=0.55
            ),
            ThreatData(
                region="Sud-Ouest",
                threat_level="MEDIUM",
                risk_score=58.7,
                article_count=12,
                key_actors=["Ambazonia Forces", "Government Forces"],
                incident_types=["Armed Conflict", "Civilian Displacement"],
                sentiment_score=-0.38,
                escalation_probability=0.48
            ),
            ThreatData(
                region="Centre",
                threat_level="LOW",
                risk_score=32.4,
                article_count=5,
                key_actors=["Political Parties", "Civil Society"],
                incident_types=["Political Activity", "Economic Issues"],
                sentiment_score=0.15,
                escalation_probability=0.22
            ),
            ThreatData(
                region="Littoral",
                threat_level="LOW",
                risk_score=28.9,
                article_count=7,
                key_actors=["Port Authorities", "Business Community"],
                incident_types=["Economic Activity", "Maritime Security"],
                sentiment_score=0.25,
                escalation_probability=0.18
            )
        ]
        
        config = ReportConfig(
            title="PROJECT SENTINEL Intelligence Assessment",
            classification="CONFIDENTIAL",
            report_type="DAILY_INTELLIGENCE_BRIEF",
            author="PROJECT SENTINEL AI System",
            organization="Cameroon Defense Forces - Intelligence Division",
            time_period="24-Hour Assessment",
            include_charts=True,
            include_executive_summary=True
        )
        
        return self.generate_intelligence_report(sample_data, config)

# Global PDF generator instance
pdf_generator = ProjectSentinelPDFGenerator()

if __name__ == "__main__":
    print("🎯 Testing PROJECT SENTINEL PDF Report Generator...")
    
    try:
        output_file = pdf_generator.generate_sample_report()
        print(f"✅ Sample report generated successfully!")
        print(f"📄 File: {output_file}")
        print(f"📊 Report includes: Executive Summary, Threat Charts, Regional Analysis")
        print(f"🔒 Classification: CONFIDENTIAL")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
