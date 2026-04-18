from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from datetime import datetime


class PDFExporter:
    """Classe utilitaire pour exporter des données en PDF"""
    
    def __init__(self, title="Export"):
        self.title = title
        self.elements = []
        self.styles = getSampleStyleSheet()
        
        # Style personnalisé pour les titres
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=20,
            alignment=1  # Centré
        )
        
        # Style pour les sous-titres
        self.subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=10
        )
    
    def add_title(self, text):
        """Ajoute un titre"""
        self.elements.append(Paragraph(text, self.title_style))
    
    def add_paragraph(self, text, style=None):
        """Ajoute un paragraphe"""
        if style is None:
            style = self.styles['Normal']
        self.elements.append(Paragraph(text, style))
        self.elements.append(Spacer(1, 0.2*inch))
    
    def add_table(self, data, col_widths=None):
        """Ajoute un tableau"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.3*inch))
    
    def get_response(self, filename=None):
        """Retourne une réponse HTTP avec le fichier PDF"""
        if filename is None:
            filename = f"{self.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        doc.build(self.elements)
        return response


def generate_bulletin_pdf(eleve, notes, periode):
    """Génère un bulletin de notes en PDF"""
    exporter = PDFExporter(f"Bulletin_{eleve.nom_complet}")
    
    # Titre
    exporter.add_title(f"Bulletin de notes - {periode}")
    exporter.add_paragraph(f"Élève: {eleve.nom_complet}")
    exporter.add_paragraph(f"Classe: {eleve.classe.nom if eleve.classe else 'N/A'}")
    exporter.add_paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Tableau des notes
    data = [['Matière', 'Coefficient', 'Note', 'Moyenne']]
    for note in notes:
        data.append([
            note.matiere.nom if note.matiere else '',
            str(note.matiere.coefficients.first().coefficient) if note.matiere and note.matiere.coefficients.exists() else '1',
            f"{note.note}/{note.note_sur}",
            f"{note.note / note.note_sur * 20:.2f}/20"
        ])
    
    exporter.add_table(data)
    
    return exporter.get_response(f"bulletin_{eleve.matricule}")


def generate_facture_pdf(facture):
    """Génère une facture en PDF"""
    exporter = PDFExporter(f"Facture_{facture.numero_facture}")
    
    exporter.add_title(f"Facture N° {facture.numero_facture}")
    exporter.add_paragraph(f"Date: {facture.date_facture.strftime('%d/%m/%Y')}")
    exporter.add_paragraph(f"Échéance: {facture.date_echeance.strftime('%d/%m/%Y')}")
    exporter.add_paragraph(f"Élève: {facture.eleve.nom_complet}")
    
    # Tableau des lignes
    data = [['Description', 'Montant']]
    for ligne in facture.lignes.all():
        data.append([ligne.description, f"{ligne.montant:,.0f} CFA"])
    
    data.append(['', ''])
    data.append(['TOTAL', f"{facture.montant_total:,.0f} CFA"])
    
    col_widths = [4*inch, 1.5*inch]
    exporter.add_table(data, col_widths)
    
    return exporter.get_response(f"facture_{facture.numero_facture}")


def generate_recu_paiement_pdf(paiement):
    """Génère un reçu de paiement en PDF"""
    exporter = PDFExporter(f"Recu_{paiement.id}")
    
    exporter.add_title("REÇU DE PAIEMENT")
    exporter.add_paragraph(f"Date: {paiement.date_paiement.strftime('%d/%m/%Y')}")
    exporter.add_paragraph(f"Montant: {paiement.montant:,.0f} CFA")
    exporter.add_paragraph(f"Mode: {paiement.get_mode_paiement_display()}")
    exporter.add_paragraph(f"Référence: {paiement.reference or 'N/A'}")
    exporter.add_paragraph(f"Élève: {paiement.eleve.nom_complet}")
    
    if paiement.observations:
        exporter.add_paragraph(f"Observations: {paiement.observations}")
    
    exporter.add_paragraph("")
    exporter.add_paragraph("Signature et cachet")
    
    return exporter.get_response(f"recu_paiement_{paiement.id}")
