"""
PDF Report Generator
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from io import BytesIO
import datetime
import base64

class LoanApplicationPDF:
    """
    Generate professional PDF report for loan application results
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Normal style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Status approved style
        self.approved_style = ParagraphStyle(
            'ApprovedStatus',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.green,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        # Status rejected style
        self.rejected_style = ParagraphStyle(
            'RejectedStatus',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.red,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
    
    def generate_report(self, application_data, prediction_data, shap_plots=None):
        """
        Generate comprehensive PDF report
        
        Args:
            application_data: Dictionary with application details
            prediction_data: Dictionary with prediction results
            shap_plots: Dictionary with SHAP visualization images (base64)
        
        Returns:
            BytesIO object containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add title
        title = Paragraph("LOAN APPLICATION REPORT", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add application ID and date
        app_id = Paragraph(f"<b>Application ID:</b> {application_data.get('application_id', 'N/A')}", self.normal_style)
        elements.append(app_id)
        
        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        date_para = Paragraph(f"<b>Report Date:</b> {date_str}", self.normal_style)
        elements.append(date_para)
        elements.append(Spacer(1, 20))
        
        # Add status
        status = prediction_data.get('approval_status', 'Pending')
        if status == 'Approved':
            status_para = Paragraph(f"✓ LOAN APPROVED", self.approved_style)
        else:
            status_para = Paragraph(f"✗ LOAN REJECTED", self.rejected_style)
        
        elements.append(status_para)
        elements.append(Spacer(1, 20))
        
        # Application details section
        elements.append(Paragraph("APPLICATION DETAILS", self.heading_style))
        
        app_details_data = [
            ['Field', 'Value'],
            ['Applicant Name', application_data.get('username', 'N/A')],
            ['Loan Type', application_data.get('loan_type', 'N/A')],
            ['Requested Amount', f"₹{application_data.get('requested_loan_amount', 0):,.2f}"],
            ['Loan Tenure', f"{application_data.get('loan_tenure_months', 0)} months"],
            ['Interest Rate', f"{application_data.get('interest_rate', 0):.2f}%"],
            ['Monthly Income', f"₹{application_data.get('monthly_income', 0):,.2f}"],
            ['Credit Score', str(application_data.get('credit_score', 'N/A'))],
            ['CIBIL Score', str(application_data.get('cibil_score', 'N/A'))]
        ]
        
        app_table = Table(app_details_data, colWidths=[2.5*inch, 3.5*inch])
        app_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(app_table)
        elements.append(Spacer(1, 20))
        
        # Prediction results section
        elements.append(Paragraph("ASSESSMENT RESULTS", self.heading_style))
        
        pred_details_data = [
            ['Metric', 'Value'],
            ['Approval Status', prediction_data.get('approval_status', 'Pending')],
            ['Probability of Default', f"{prediction_data.get('probability_of_default', 0):.2%}"],
            ['Safe Loan Amount', f"₹{prediction_data.get('safe_loan_amount', 0):,.2f}"],
            ['Calculated EMI', f"₹{prediction_data.get('emi_amount', 0):,.2f}"],
            ['EMI to Income Ratio', f"{prediction_data.get('emi_income_ratio', 0):.2%}"]
        ]
        
        pred_table = Table(pred_details_data, colWidths=[2.5*inch, 3.5*inch])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(pred_table)
        elements.append(Spacer(1, 20))
        
        # Recommendations section
        elements.append(Paragraph("RECOMMENDATIONS", self.heading_style))
        
        if status == 'Approved':
            recommendation_text = f"""
            Congratulations! Your loan application has been <b>approved</b>. Based on our comprehensive 
            assessment of your financial profile, you are eligible for the requested loan amount. 
            Your EMI of ₹{prediction_data.get('emi_amount', 0):,.2f} is sustainable given your monthly 
            income of ₹{application_data.get('monthly_income', 0):,.2f}.
            """
        else:
            safe_amount = prediction_data.get('safe_loan_amount', 0)
            recommendation_text = f"""
            Unfortunately, your loan application has been <b>rejected</b> for the requested amount. 
            However, based on our analysis, you may be eligible for a loan amount of 
            ₹{safe_amount:,.2f}. We recommend reapplying with this adjusted amount or working to 
            improve your credit profile before reapplying.
            """
        
        recommendation_para = Paragraph(recommendation_text, self.normal_style)
        elements.append(recommendation_para)
        elements.append(Spacer(1, 20))
        
        # Add SHAP explanations section
        if shap_plots and prediction_data.get('shap_summary'):
            elements.append(PageBreak())
            elements.append(Paragraph("DECISION EXPLANATION (AI Explainability)", self.heading_style))
            
            shap_summary = prediction_data.get('shap_summary', {})
            explanation_text = shap_summary.get('summary_text', 'Explanation not available.')
            explanation_para = Paragraph(explanation_text, self.normal_style)
            elements.append(explanation_para)
            elements.append(Spacer(1, 12))
            
            # Add top features
            if 'top_positive' in shap_summary and shap_summary['top_positive']:
                elements.append(Paragraph("Positive Factors:", self.normal_style))
                for feature in shap_summary['top_positive'][:5]:
                    feature_text = f"• <b>{feature['name']}</b>: Contributing positively"
                    elements.append(Paragraph(feature_text, self.normal_style))
                elements.append(Spacer(1, 8))
            
            if 'top_negative' in shap_summary and shap_summary['top_negative']:
                elements.append(Paragraph("Areas of Concern:", self.normal_style))
                for feature in shap_summary['top_negative'][:5]:
                    feature_text = f"• <b>{feature['name']}</b>: Contributing negatively"
                    elements.append(Paragraph(feature_text, self.normal_style))
                elements.append(Spacer(1, 12))
            
            # Add SHAP plots if available
            if shap_plots.get('importance_plot'):
                try:
                    img_data = base64.b64decode(shap_plots['importance_plot'])
                    img = Image(BytesIO(img_data), width=5*inch, height=3*inch)
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph("Feature Importance Visualization:", self.normal_style))
                    elements.append(img)
                except Exception as e:
                    print(f"Error adding importance plot: {e}")
            
            if shap_plots.get('waterfall_plot'):
                try:
                    img_data = base64.b64decode(shap_plots['waterfall_plot'])
                    img = Image(BytesIO(img_data), width=5*inch, height=3*inch)
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph("Feature Impact Analysis:", self.normal_style))
                    elements.append(img)
                except Exception as e:
                    print(f"Error adding waterfall plot: {e}")
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = """
        <i>This is an automated assessment generated by our AI-powered credit risk engine. 
        The decision is based on machine learning models trained on historical data and 
        explainable AI techniques (SHAP). For queries, please contact our support team.</i>
        """
        footer = Paragraph(footer_text, self.normal_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def save_to_file(self, buffer, filename):
        """Save PDF buffer to file"""
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
