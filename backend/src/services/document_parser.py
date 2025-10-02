"""
Document parsing service for extracting text from TXT, PDF, and Word documents.
"""
from pathlib import Path
from fastapi import HTTPException
import PyPDF2
import docx


class DocumentParser:
    """Handles parsing of various document formats"""
    
    def extract_brand_and_product(self, text: str) -> dict:
        """
        Extract brand and product name from document text.
        Looks for common patterns like "Brand:", "Product:", etc.
        """
        import re
        
        brand = None
        product_name = None
        
        # Try to find brand
        brand_patterns = [
            r'brand[:\s]+([^\n]+)',
            r'brand name[:\s]+([^\n]+)',
            r'company[:\s]+([^\n]+)'
        ]
        for pattern in brand_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                brand = match.group(1).strip()
                break
        
        # Try to find product name
        product_patterns = [
            r'product[:\s]+([^\n]+)',
            r'product name[:\s]+([^\n]+)'
        ]
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                break
        
        return {'brand': brand, 'product_name': product_name}
    
    def parse_document(self, file_path: str, source_type: str) -> str:
        """
        Parse document and extract text content.
        
        Args:
            file_path: Path to document file
            source_type: Type of document ('txt', 'pdf', 'docx')
        
        Returns:
            Extracted text content
        
        Raises:
            HTTPException: If parsing fails
        """
        try:
            if source_type == "txt":
                return self._parse_txt(file_path)
            elif source_type == "pdf":
                return self._parse_pdf(file_path)
            elif source_type == "docx":
                return self._parse_docx(file_path)
            else:
                raise ValueError(f"Unsupported document type: {source_type}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse document: {str(e)}"
            )
    
    def _parse_txt(self, file_path: str) -> str:
        """Parse plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file and extract text"""
        text_content = []
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        if not text_content:
            raise ValueError("No text content found in PDF")
        
        return "\n".join(text_content)
    
    def _parse_docx(self, file_path: str) -> str:
        """Parse Word document and extract text"""
        doc = docx.Document(file_path)
        
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        if not text_content:
            raise ValueError("No text content found in Word document")
        
        return "\n".join(text_content)


# Singleton instance
document_parser = DocumentParser()
