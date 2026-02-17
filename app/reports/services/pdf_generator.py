"""PDF report generator for pitcher scouting reports using ReportLab."""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak,
)
from app.pitchers.services.pitcher_stats import PitcherStatsService
from app.reports.services.heatmap_generator import HeatmapGenerator
from app.utils.team_config import get_team_config


class PitcherReportPDF:
    """Generate an opponent pitcher scouting report PDF (Report 7).

    Layout per page:
    - Header with pitcher name, team, hand
    - Pitch arsenal table
    - Heatmaps: Overall, vs LHH, vs RHH
    - Usage by batter hand
    """

    def __init__(self, pitcher_id, pitcher_name, filters=None):
        self.pitcher_id = pitcher_id
        self.pitcher_name = pitcher_name
        self.filters = filters or {}
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=13,
            spaceAfter=6,
            spaceBefore=12,
        ))
        self.styles.add(ParagraphStyle(
            'SubInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.gray,
            spaceAfter=12,
        ))

    def generate(self):
        """Generate the PDF and return a BytesIO buffer."""
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )

        elements = []

        # Header
        team_config = get_team_config()
        elements.append(Paragraph(
            f"{team_config['name']} | {team_config['season_year']}",
            self.styles['SubInfo'],
        ))
        elements.append(Paragraph(
            f"Pitcher Report: {self.pitcher_name}",
            self.styles['ReportTitle'],
        ))

        # Arsenal table
        elements.append(Paragraph("Pitch Arsenal", self.styles['SectionTitle']))
        arsenal_table = self._build_arsenal_table()
        if arsenal_table:
            elements.append(arsenal_table)
        elements.append(Spacer(1, 12))

        # Heatmaps
        elements.append(Paragraph("Pitch Location Heatmaps", self.styles['SectionTitle']))
        heatmap_row = self._build_heatmap_row()
        if heatmap_row:
            elements.append(heatmap_row)

        doc.build(elements)
        return buf

    def _build_arsenal_table(self):
        """Build the pitch arsenal table."""
        arsenal = PitcherStatsService.get_pitcher_arsenal(self.pitcher_id, self.filters)
        if not arsenal:
            return Paragraph("No pitch data available.", self.styles['Normal'])

        headers = ['Pitch', 'P%', '#', 'Vel', 'Range', 'Spin', 'IVB', 'HB', 'Zone%', 'Whiff%', 'CSW%']
        data = [headers]

        for row in arsenal:
            data.append([
                row.get('pitch_type', ''),
                f"{row['pct']:.1f}%" if row.get('pct') is not None else '\u2014',
                str(row.get('count', '')),
                f"{row['avg_velo']:.1f}" if row.get('avg_velo') is not None else '\u2014',
                row.get('velo_range', '\u2014') or '\u2014',
                f"{row['avg_spin']:.0f}" if row.get('avg_spin') is not None else '\u2014',
                f"{row['avg_ivb']:.1f}" if row.get('avg_ivb') is not None else '\u2014',
                f"{row['avg_hb']:.1f}" if row.get('avg_hb') is not None else '\u2014',
                f"{row['in_zone_pct']:.1f}%" if row.get('in_zone_pct') is not None else '\u2014',
                f"{row['whiff_pct']:.1f}%" if row.get('whiff_pct') is not None else '\u2014',
                f"{row['csw_pct']:.1f}%" if row.get('csw_pct') is not None else '\u2014',
            ])

        col_widths = [80, 40, 30, 40, 55, 45, 35, 35, 45, 50, 45]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table

    def _build_heatmap_row(self):
        """Build a row of 3 heatmaps: Overall, vs LHH, vs RHH."""
        gen = HeatmapGenerator(self.pitcher_id, self.filters)

        heatmap_images = []
        for split in ['overall', 'vs_lhh', 'vs_rhh']:
            buf = gen.generate_heatmap(split=split)
            buf.seek(0)
            img = Image(buf, width=2.2 * inch, height=2.2 * inch)
            heatmap_images.append(img)

        if not heatmap_images:
            return None

        table = Table([heatmap_images], colWidths=[2.4 * inch] * 3)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table
