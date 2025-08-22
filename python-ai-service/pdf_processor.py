"""
Advanced PDF Processing for Screenplay Analysis
Supports multiple extraction methods with fallback strategies
"""

import os
import io
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time
from pathlib import Path

# PDF processing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PDFProcessingResult:
    """Result from PDF processing"""
    success: bool
    extracted_text: str
    page_count: int
    file_size: int
    processing_time: float
    method_used: str
    error_message: Optional[str] = None

class PDFProcessor:
    """Advanced PDF processor with multiple extraction methods"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.min_text_length = 100  # Minimum viable text length
        
        # Log available methods
        methods = []
        if PYPDF2_AVAILABLE:
            methods.append("PyPDF2")
        if PDFPLUMBER_AVAILABLE:
            methods.append("pdfplumber")
        if OCR_AVAILABLE:
            methods.append("OCR (pdf2image + tesseract)")
        
        logger.info(f"🔧 PDF Processor initialized with methods: {', '.join(methods)}")
    
    async def process_pdf(self, pdf_content: bytes, filename: str) -> PDFProcessingResult:
        """Process PDF with multiple fallback methods"""
        
        start_time = time.time()
        file_size = len(pdf_content)
        
        logger.info(f"📄 Processing PDF: {filename} ({file_size:,} bytes)")
        
        # Validate file size
        if file_size > self.max_file_size:
            return PDFProcessingResult(
                success=False,
                extracted_text="",
                page_count=0,
                file_size=file_size,
                processing_time=time.time() - start_time,
                method_used="none",
                error_message=f"File too large: {file_size:,} bytes (max: {self.max_file_size:,})"
            )
        
        # Try extraction methods in order of preference
        methods = [
            ("pdfplumber", self._extract_with_pdfplumber),
            ("PyPDF2", self._extract_with_pypdf2),
            ("OCR", self._extract_with_ocr)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"🔄 Trying {method_name}...")
                text, page_count = await method_func(pdf_content)
                
                if text and len(text.strip()) >= self.min_text_length:
                    processing_time = time.time() - start_time
                    logger.info(f"✅ Success with {method_name}: {len(text):,} chars, {page_count} pages")
                    
                    return PDFProcessingResult(
                        success=True,
                        extracted_text=self._clean_text(text),
                        page_count=page_count,
                        file_size=file_size,
                        processing_time=processing_time,
                        method_used=method_name
                    )
                else:
                    logger.warning(f"⚠️ {method_name} extracted insufficient text: {len(text) if text else 0} chars")
                    
            except Exception as e:
                logger.warning(f"⚠️ {method_name} failed: {e}")
                continue
        
        # All methods failed
        processing_time = time.time() - start_time
        return PDFProcessingResult(
            success=False,
            extracted_text="",
            page_count=0,
            file_size=file_size,
            processing_time=processing_time,
            method_used="none",
            error_message="All extraction methods failed"
        )
    
    async def _extract_with_pdfplumber(self, pdf_content: bytes) -> Tuple[str, int]:
        """Extract text using pdfplumber (best for most PDFs)"""
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber not available")
        
        text_parts = []
        page_count = 0
        
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            page_count = len(pdf.pages)
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts), page_count
    
    async def _extract_with_pypdf2(self, pdf_content: bytes) -> Tuple[str, int]:
        """Extract text using PyPDF2 (fallback method)"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 not available")
        
        text_parts = []
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        page_count = len(pdf_reader.pages)
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        return '\n'.join(text_parts), page_count
    
    async def _extract_with_ocr(self, pdf_content: bytes) -> Tuple[str, int]:
        """Extract text using OCR (for scanned PDFs)"""
        if not OCR_AVAILABLE:
            raise ImportError("OCR libraries not available")
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_content, dpi=200)
        page_count = len(images)
        
        text_parts = []
        
        for i, image in enumerate(images):
            logger.info(f"🔍 OCR processing page {i+1}/{page_count}...")
            
            # Use OCR to extract text
            page_text = pytesseract.image_to_string(image, lang='eng')
            if page_text.strip():
                text_parts.append(page_text)
        
        return '\n'.join(text_parts), page_count
    
    def _clean_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Fix common screenplay formatting issues
        text = text.replace('\n\n\n', '\n\n')  # Reduce excessive line breaks
        text = text.replace('  ', ' ')  # Remove double spaces
        
        # Preserve screenplay formatting markers
        screenplay_markers = ['FADE IN:', 'FADE OUT:', 'CUT TO:', 'INT.', 'EXT.', 'CONT\'D']
        for marker in screenplay_markers:
            text = text.replace(marker, f'\n{marker}')
        
        # Clean up and return
        return text.strip()
    
    def save_uploaded_file(self, file_content: bytes, filename: str, user_id: str) -> str:
        """Save uploaded file to disk"""
        
        # Create uploads directory
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        timestamp = int(time.time())
        safe_filename = "".join(c for c in filename if c.isalnum() or c in '._-')
        stored_filename = f"{user_id}_{timestamp}_{safe_filename}"
        
        file_path = uploads_dir / stored_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"💾 File saved: {file_path}")
        return str(file_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a saved file"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                return {
                    'exists': True,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                }
            else:
                return {'exists': False}
        except Exception as e:
            logger.error(f"❌ Error getting file info: {e}")
            return {'exists': False, 'error': str(e)}
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a saved file"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False
