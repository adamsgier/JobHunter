"""
AI Vision Analysis Module
Intelligent screenshot comparison using Google Gemini Flash
"""

import os
import base64
import logging
from typing import Optional, Dict, Any
from PIL import Image
import io

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-genai not installed. AI analysis will be disabled.")

logger = logging.getLogger(__name__)

class AIVisionAnalyzer:
    """AI-powered screenshot analysis using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self.model_name = "gemma-3-12b-it"  # Gemma 3 12B with instruction tuning
        self.enabled = False
        
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini AI not available - install google-genai")
            return
            
        if not api_key:
            logger.warning("No Gemini API key provided - AI analysis disabled")
            return
            
        try:
            self.client = genai.Client(api_key=api_key)
            self.enabled = True
            logger.info(f"✅ Google Gemini AI vision initialized ({self.model_name})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def is_enabled(self) -> bool:
        """Check if AI analysis is available"""
        return self.enabled
    
    def analyze_screenshots(self, before_image: bytes, after_image: bytes, company: str) -> Dict[str, Any]:
        """
        Analyze two screenshots to detect meaningful changes in job listings
        
        Args:
            before_image: Previous screenshot as bytes
            after_image: Current screenshot as bytes  
            company: Company name for context
            
        Returns:
            Dict with analysis results including change detection and description
        """
        if not self.enabled:
            return {
                "has_changes": None,
                "description": "AI analysis not available",
                "confidence": 0.0,
                "error": "Gemini not initialized"
            }
        
        try:
            # Convert bytes to PIL Images for size info (not sent to API)
            before_pil = Image.open(io.BytesIO(before_image))
            after_pil = Image.open(io.BytesIO(after_image))
            
            logger.info(f"Comparing {company} screenshots: {before_pil.size} vs {after_pil.size}")
            
            # Prepare the prompt for job listing analysis
            prompt = f"""
            You are analyzing screenshots of {company}'s job listing page to detect meaningful changes in JOB CONTENT ONLY.
            
            I'm providing you with TWO screenshots:
            1. BEFORE: Previous screenshot of the job page
            2. AFTER: Current screenshot of the job page
            
            **CRITICAL**: The images may have DIFFERENT RESOLUTIONS or heights. This is NORMAL and NOT a change.
            Focus ONLY on the actual job listing content, not the page dimensions.
            
            **MEANINGFUL CHANGES** to report (ONLY these matter):
            ✅ New job posting titles that didn't exist before
            ✅ Job postings that were completely removed
            ✅ Different job titles in the same position
            ✅ Different job locations or departments (if they indicate new roles)
            ✅ Significant changes in number of visible jobs (e.g., 5 jobs → 8 jobs)
            
            **IGNORE THESE** (NOT meaningful changes):
            ❌ Page height/resolution differences (images can be different sizes!)
            ❌ Vertical spacing or layout shifts
            ❌ "Posted X days ago" or timestamp changes
            ❌ "Showing X-Y of Z results" pagination text
            ❌ Cookie banners, pop-ups, or notices
            ❌ Scrollbar presence/absence
            ❌ Loading animations or skeleton screens
            ❌ Session IDs, tracking pixels, or dynamic IDs
            ❌ Same jobs in slightly different visual positions
            ❌ Font rendering or anti-aliasing differences
            ❌ Background colors or subtle styling changes
            ❌ Jobs that appear "cut off" at bottom due to page height differences
            
            **ANALYSIS APPROACH**:
            1. Read the job titles visible in BEFORE image
            2. Read the job titles visible in AFTER image  
            3. Compare the actual job titles - are they the same jobs?
            4. Ignore everything else (layout, spacing, page size, etc.)
            
            **RESPOND** in this exact JSON format:
            {{
                "has_changes": true/false,
                "description": "Brief description of what changed or 'No meaningful job changes detected'",
                "confidence": 0.0-1.0,
                "details": ["specific job title that was added/removed", "another specific change"]
            }}
            
            Be VERY conservative - only report has_changes=true if you see ACTUAL DIFFERENT JOB TITLES.
            If the same jobs appear with slightly different layout/spacing, that's has_changes=false.
            """
            
            # Analyze with Gemma 3 via Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=before_image, mime_type="image/png"),
                    types.Part.from_bytes(data=after_image, mime_type="image/png"),
                    prompt
                ]
            )
            
            # Parse the response
            analysis_text = response.text.strip()
            
            # Try to extract JSON from response
            analysis = self._parse_ai_response(analysis_text)
            
            logger.info(f"🤖 AI Analysis for {company}: {analysis.get('description', 'Unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed for {company}: {e}")
            return {
                "has_changes": None,
                "description": f"AI analysis error: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _parse_ai_response(self, text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            import json
            
            # Look for JSON in the response
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_text = text[start_idx:end_idx+1]
                parsed = json.loads(json_text)
                
                # Validate required fields
                return {
                    "has_changes": parsed.get("has_changes", False),
                    "description": parsed.get("description", "No description provided"),
                    "confidence": float(parsed.get("confidence", 0.5)),
                    "details": parsed.get("details", [])
                }
        except Exception as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        # Fallback parsing - look for keywords
        text_lower = text.lower()
        
        # Simple heuristics for change detection
        has_changes = any(keyword in text_lower for keyword in [
            "new job", "job added", "position added", "changes detected",
            "removed", "updated", "modified", "different"
        ])
        
        no_changes = any(keyword in text_lower for keyword in [
            "no changes", "no meaningful changes", "no significant", 
            "same", "identical", "no new jobs"
        ])
        
        if no_changes:
            has_changes = False
        
        return {
            "has_changes": has_changes,
            "description": text[:200] + "..." if len(text) > 200 else text,
            "confidence": 0.7 if has_changes or no_changes else 0.3,
            "details": []
        }

    def analyze_single_screenshot(self, image_bytes: bytes, company: str, is_baseline: bool = False) -> Dict[str, Any]:
        """
        Analyze a single screenshot to extract job information
        
        Args:
            image_bytes: Screenshot as bytes
            company: Company name
            is_baseline: Whether this is the first/baseline screenshot
            
        Returns:
            Dict with job analysis results
        """
        if not self.enabled:
            return {
                "job_count": None,
                "description": "AI analysis not available",
                "error": "Gemini not initialized"
            }
        
        try:
            # Prepare prompt
            action = "baseline established" if is_baseline else "monitoring"
            
            prompt = f"""
            Analyze this screenshot of {company}'s job listing page.
            
            Please provide a brief summary in this format:
            
            {{
                "job_count": estimated_number_of_jobs,
                "description": "Brief description of what you see on the page",
                "categories": ["list", "of", "job", "categories", "seen"],
                "status": "{action}"
            }}
            
            Focus on counting visible job listings and identifying job types/categories.
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    prompt
                ]
            )
            
            analysis_text = response.text.strip()
            
            # Parse response
            analysis = self._parse_single_analysis(analysis_text)
            
            logger.info(f"🔍 Single analysis for {company}: {analysis.get('description', 'Unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Single screenshot analysis failed for {company}: {e}")
            return {
                "job_count": None,
                "description": f"Analysis error: {str(e)}",
                "error": str(e)
            }
    
    def _parse_single_analysis(self, text: str) -> Dict[str, Any]:
        """Parse single screenshot analysis response"""
        try:
            import json
            
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_text = text[start_idx:end_idx+1]
                parsed = json.loads(json_text)
                return parsed
                
        except Exception as e:
            logger.warning(f"Failed to parse single analysis JSON: {e}")
        
        # Fallback
        return {
            "job_count": "Unknown",
            "description": text[:150] + "..." if len(text) > 150 else text,
            "categories": [],
            "status": "analyzed"
        }


# Convenience functions
def create_ai_analyzer(api_key: Optional[str] = None) -> AIVisionAnalyzer:
    """Create an AI analyzer instance"""
    return AIVisionAnalyzer(api_key)

def is_ai_available() -> bool:
    """Check if AI analysis capabilities are available"""
    return GEMINI_AVAILABLE

# Export for backward compatibility
AI_VISION_AVAILABLE = GEMINI_AVAILABLE