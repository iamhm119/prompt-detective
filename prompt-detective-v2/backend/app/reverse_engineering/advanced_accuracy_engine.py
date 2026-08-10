"""
Advanced Accuracy Engine for Maximum Reverse Engineering Precision
Uses ensemble methods, confidence scoring, and multi-stage validation
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from groq import Groq
import json
import hashlib
import re

# Import from relative path
try:
    from .config import Config
    from .utils import ImageProcessor
except ImportError:
    from config import Config
    from utils import ImageProcessor


class EnsembleAnalyzer:
    """Ensemble-based analysis for maximum accuracy through multiple perspectives"""
    
    def __init__(self, client: Groq):
        self.client = client
        self.model = Config.GROQ_MODEL
    
    def analyze_with_ensemble(self, image_b64: str, num_variations: int = 3) -> Dict[str, Any]:
        """
        Perform ensemble analysis with multiple prompt variations
        Returns consensus with confidence scores
        """
        variations = [
            self._get_prompt_variation_technical(),
            self._get_prompt_variation_artistic(),
            self._get_prompt_variation_reconstruction()
        ]
        
        results = []
        for i, (system_p, user_p) in enumerate(variations[:num_variations], 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_p},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_p},
                                {"type": "image_url", "image_url": {"url": image_b64}}
                            ]
                        }
                    ],
                    temperature=0.1 + (i * 0.05),  # Slight temperature variation
                    max_tokens=2000
                )
                
                results.append({
                    "variant": i,
                    "content": response.choices[0].message.content,
                    "approach": ["technical", "artistic", "reconstruction"][i-1]
                })
            except Exception as e:
                print(f"Ensemble variant {i} failed: {e}")
        
        if not results:
            return {"error": "All ensemble variants failed"}
        
        return self._merge_ensemble_results(results)
    
    def _merge_ensemble_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge multiple analysis results using consensus and confidence"""
        # Extract common elements across all results
        all_text = "\n\n".join([r["content"] for r in results])
        
        # Use frequency analysis to identify high-confidence elements
        consensus = {
            "ensemble_analyses": results,
            "merged_analysis": all_text,
            "confidence_score": len(results) / 3.0,  # Based on successful variants
            "consensus_elements": self._extract_consensus(results)
        }
        
        return consensus
    
    def _extract_consensus(self, results: List[Dict]) -> Dict[str, List[str]]:
        """Extract elements that appear across multiple analyses"""
        # Simple keyword frequency analysis
        all_words = {}
        for result in results:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', result["content"].lower())
            for word in set(words):
                all_words[word] = all_words.get(word, 0) + 1
        
        # Return words appearing in 2+ analyses
        consensus_words = [w for w, count in all_words.items() if count >= 2]
        
        return {
            "high_confidence_keywords": consensus_words[:20],
            "agreement_level": len(consensus_words) / max(len(all_words), 1)
        }
    
    def _get_prompt_variation_technical(self) -> Tuple[str, str]:
        """Technical forensic analysis variation"""
        system = """You are a technical forensics expert specializing in reverse-engineering visual content.
Your analysis must be FORENSICALLY PRECISE - every detail matters for accurate reconstruction."""
        
        user = """FORENSIC TECHNICAL ANALYSIS:

Analyze with MAXIMUM PRECISION:

1. RENDERING ENGINE SIGNATURES:
   - Identify noise patterns, artifacts, sampling characteristics
   - Detect specific render engine fingerprints (Cycles, Arnold, Octane, etc.)
   - Note anti-aliasing methods, ray tracing indicators
   - Look for GAN artifacts, diffusion model signatures

2. LIGHTING FORENSICS:
   - Map exact light source positions and types
   - Identify HDRI environment characteristics
   - Measure shadow softness/hardness ratios
   - Detect three-point lighting setup indicators

3. CAMERA SPECIFICATION INFERENCE:
   - Calculate approximate focal length from perspective distortion
   - Identify depth-of-field characteristics (f-stop estimation)
   - Detect lens aberrations (chromatic, spherical)
   - Measure field of view and aspect ratio

4. MATERIAL & TEXTURE ANALYSIS:
   - Identify PBR workflow signatures
   - Detect procedural vs. photographic textures
   - Analyze surface roughness, metallic properties
   - Note normal map, displacement characteristics

5. POST-PROCESSING PIPELINE:
   - Identify color grading LUT signatures
   - Detect specific filters or adjustments
   - Note compositing layer indicators
   - Identify noise reduction/sharpening artifacts

Output EXACT technical parameters, not generic descriptions."""
        
        return system, user
    
    def _get_prompt_variation_artistic(self) -> Tuple[str, str]:
        """Artistic and stylistic analysis variation"""
        system = """You are a master art director with encyclopedic knowledge of art history, visual styles, and creative techniques.
Focus on identifying EXACT artistic influences and stylistic choices."""
        
        user = """ARTISTIC STYLE FORENSICS:

Identify with PRECISION:

1. ARTISTIC MOVEMENT & INFLUENCE:
   - Specific art movements (Impressionism, Surrealism, Bauhaus, etc.)
   - Named artist influences (cite specific artists if similar)
   - Historical period indicators
   - Cultural/regional style markers

2. COMPOSITION MATHEMATICS:
   - Golden ratio, rule of thirds application
   - Fibonacci spiral presence
   - Leading lines and vanishing points
   - Symmetry vs. asymmetry balance
   - Negative space usage

3. COLOR THEORY APPLICATION:
   - Specific color harmony (complementary, triadic, analogous)
   - Color temperature analysis (warm/cool zones)
   - Saturation distribution patterns
   - Value contrast ratios
   - Psychological color associations

4. STYLISTIC TECHNIQUES:
   - Brush stroke characteristics (if applicable)
   - Texture application methods
   - Line weight and character
   - Pattern and repetition usage
   - Spatial depth techniques

5. MOOD & NARRATIVE:
   - Emotional tone indicators
   - Symbolic elements and their meanings
   - Story implications from visual cues
   - Cultural references and context

Output SPECIFIC artistic terms and named techniques, avoid generic descriptions."""
        
        return system, user
    
    def _get_prompt_variation_reconstruction(self) -> Tuple[str, str]:
        """Reconstruction-focused analysis variation"""
        system = """You are an expert prompt engineer who specializes in creating prompts that PERFECTLY recreate visual content.
Your goal: generate a prompt so precise it could recreate this image with 95%+ accuracy."""
        
        user = """RECONSTRUCTION PROMPT ENGINEERING:

Create the MOST ACCURATE prompt possible:

1. SUBJECT PRECISION:
   - Exact subject description (species, age, pose, expression)
   - Precise positioning and orientation
   - Scale and proportion relationships
   - Number and arrangement of subjects

2. ENVIRONMENT SPECIFICATION:
   - Exact setting and location type
   - Background element inventory
   - Foreground/midground/background separation
   - Environmental conditions (weather, time of day)

3. STYLE KEYWORD OPTIMIZATION:
   - AI generator-specific style terms
   - Quality/resolution modifiers
   - Rendering style specifications
   - Artistic technique keywords

4. TECHNICAL PARAMETER KEYWORDS:
   - Camera/lens simulation terms
   - Lighting setup keywords
   - Depth/focus descriptors
   - Color grading terms

5. NEGATIVE PROMPT ENGINEERING:
   - Elements to avoid
   - Common artifacts to exclude
   - Quality degradation terms to negate

6. OPTIMAL PROMPT STRUCTURE:
   - Subject → Setting → Style → Technical → Quality
   - Use comma separation for generators
   - Include weight indicators for important elements
   - Add seed-worthy descriptive terms

Output a COPY-PASTE READY prompt optimized for AI generators like Midjourney, Stable Diffusion, DALL-E."""
        
        return system, user


class ConfidenceScorer:
    """Score analysis confidence based on multiple factors"""
    
    @staticmethod
    def score_analysis_quality(analysis: Dict[str, Any]) -> float:
        """
        Score the quality/confidence of an analysis result
        Returns float between 0.0 and 1.0
        """
        score = 0.0
        weights = {
            "length": 0.15,
            "structure": 0.20,
            "specificity": 0.25,
            "technical_depth": 0.20,
            "consensus": 0.20
        }
        
        content = analysis.get("content", "") or analysis.get("raw_analysis", "")
        
        # Length check (optimal range: 800-2000 chars)
        length = len(content)
        if 800 <= length <= 2000:
            score += weights["length"]
        elif length > 500:
            score += weights["length"] * 0.5
        
        # Structure check (sections, bullets, formatting)
        structure_indicators = [
            "\n\n" in content,  # Paragraphs
            ":" in content,     # Labeled sections
            "-" in content or "•" in content,  # Bullet points
            any(digit in content for digit in "12345")  # Numbered lists
        ]
        score += weights["structure"] * (sum(structure_indicators) / len(structure_indicators))
        
        # Specificity check (technical terms, numbers, named techniques)
        specificity_indicators = [
            bool(re.search(r'\d+(?:px|mm|f|°)', content)),  # Measurements
            bool(re.search(r'\b(?:RGB|CMYK|HSV|Pantone)', content, re.I)),  # Color specs
            bool(re.search(r'\b(?:photorealistic|hyperrealistic|stylized)\b', content, re.I)),  # Style terms
            bool(re.search(r'\b(?:lighting|shadow|highlight|exposure)\b', content, re.I)),  # Technical lighting
            bool(re.search(r'\b(?:composition|framing|perspective)\b', content, re.I))  # Composition terms
        ]
        score += weights["specificity"] * (sum(specificity_indicators) / len(specificity_indicators))
        
        # Technical depth (software names, specific techniques)
        technical_indicators = [
            bool(re.search(r'\b(?:Blender|Maya|Cinema4D|Unreal|Unity)\b', content, re.I)),
            bool(re.search(r'\b(?:PBR|ray.?trac|GI|ambient.?occlusion)\b', content, re.I)),
            bool(re.search(r'\b(?:HDRI|IBL|volumetric|subsurface)\b', content, re.I)),
            bool(re.search(r'\b(?:focal.?length|aperture|ISO|shutter)\b', content, re.I))
        ]
        score += weights["technical_depth"] * (sum(technical_indicators) / max(len(technical_indicators), 1))
        
        # Consensus check (if ensemble analysis available)
        if "consensus_elements" in analysis:
            agreement = analysis["consensus_elements"].get("agreement_level", 0)
            score += weights["consensus"] * agreement
        elif "ensemble_analyses" in analysis:
            score += weights["consensus"] * 0.7  # Partial credit for ensemble attempt
        
        return min(score, 1.0)


class SemanticDeduplicator:
    """Remove redundant information across multiple analyses"""
    
    @staticmethod
    def deduplicate_analyses(analyses: List[str]) -> str:
        """Merge analyses while removing redundancy"""
        if not analyses:
            return ""
        
        if len(analyses) == 1:
            return analyses[0]
        
        # Split into sentences
        all_sentences = []
        for analysis in analyses:
            sentences = re.split(r'[.!?]\s+', analysis)
            all_sentences.extend([s.strip() for s in sentences if len(s.strip()) > 20])
        
        # Simple deduplication by similarity (hash-based for speed)
        unique_sentences = []
        seen_hashes = set()
        
        for sent in all_sentences:
            # Create normalized hash
            normalized = re.sub(r'\W+', '', sent.lower())
            sent_hash = hashlib.md5(normalized.encode()).hexdigest()[:16]
            
            if sent_hash not in seen_hashes:
                seen_hashes.add(sent_hash)
                unique_sentences.append(sent)
        
        return ". ".join(unique_sentences) + "."


class PromptOptimizer:
    """Optimize prompts for maximum generation accuracy"""
    
    def __init__(self, client: Groq):
        self.client = client
    
    def optimize_prompt(self, raw_analysis: str, target_generator: str = "universal") -> Dict[str, str]:
        """
        Optimize a prompt for specific generators
        
        Args:
            raw_analysis: Raw analysis text
            target_generator: 'midjourney', 'stable-diffusion', 'dall-e', or 'universal'
        """
        optimization_prompt = f"""Transform this analysis into optimized prompts for AI image/video generators:

ANALYSIS:
{raw_analysis[:1500]}

Generate 3 optimized prompt versions:

1. MASTER PROMPT (Universal, 500-800 chars):
   - Works across all generators
   - Balanced detail and conciseness
   - Proper keyword structure

2. QUICK PROMPT (150-250 chars):
   - Essential elements only
   - Maximum impact per word
   - Ready for fast generation

3. TECHNICAL PROMPT (300-500 chars):
   - Focus on technical/quality parameters
   - Camera, lighting, rendering specs
   - Professional production values

Format response as valid JSON:
{{
  "master_prompt": "...",
  "quick_prompt": "...",
  "technical_prompt": "...",
  "style_keywords": ["keyword1", "keyword2", ...],
  "negative_prompt": "..."
}}

Use specific terminology. Be concise but precise."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Text model for optimization
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert prompt optimizer. Create prompts that maximize generation quality. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": optimization_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback structure
                return {
                    "master_prompt": content[:800],
                    "quick_prompt": content[:200],
                    "technical_prompt": content[:500],
                    "style_keywords": [],
                    "negative_prompt": ""
                }
                
        except Exception as e:
            print(f"Prompt optimization failed: {e}")
            return {
                "master_prompt": raw_analysis[:800],
                "quick_prompt": raw_analysis[:200],
                "technical_prompt": "",
                "style_keywords": [],
                "negative_prompt": "",
                "error": str(e)
            }


class VideoTemporalAnalyzer:
    """Analyze temporal relationships and motion patterns in videos"""
    
    @staticmethod
    def analyze_temporal_flow(frames_metadata: List[Dict]) -> Dict[str, Any]:
        """Analyze motion and temporal patterns across frames"""
        if len(frames_metadata) < 2:
            return {"temporal_analysis": "insufficient_frames"}
        
        # Calculate frame-to-frame changes
        changes = []
        for i in range(len(frames_metadata) - 1):
            curr = frames_metadata[i]
            next_frame = frames_metadata[i + 1]
            
            # Motion indicators from metadata
            motion_score = curr.get("motion_score", 0)
            scene_change = curr.get("is_scene_change", False)
            
            changes.append({
                "frame_pair": f"{i+1}-{i+2}",
                "motion_intensity": motion_score,
                "scene_transition": scene_change,
                "time_delta": next_frame.get("timestamp", 0) - curr.get("timestamp", 0)
            })
        
        # Aggregate temporal characteristics
        avg_motion = np.mean([c["motion_intensity"] for c in changes])
        scene_transitions = sum(1 for c in changes if c["scene_transition"])
        
        # Categorize video pacing
        if avg_motion > 0.7:
            pacing = "fast-paced, high motion"
        elif avg_motion > 0.4:
            pacing = "moderate pacing"
        else:
            pacing = "slow, contemplative"
        
        return {
            "average_motion_intensity": float(avg_motion),
            "scene_transition_count": scene_transitions,
            "pacing_category": pacing,
            "total_temporal_span": frames_metadata[-1].get("timestamp", 0),
            "frame_changes": changes
        }


class AccuracyValidator:
    """Validate and verify analysis accuracy through cross-checks"""
    
    @staticmethod
    def validate_consistency(analysis_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Run consistency checks on analysis results"""
        issues = []
        warnings = []
        
        # Check for contradictions
        content = str(analysis_dict)
        
        # Example checks
        if "photorealistic" in content.lower() and "cartoon" in content.lower():
            warnings.append("Possible style contradiction: photorealistic vs cartoon")
        
        if "bright" in content.lower() and "dark" in content.lower():
            warnings.append("Lighting description may be ambiguous")
        
        # Check for specificity
        vague_terms = ["nice", "good", "bad", "some", "various", "multiple", "several"]
        vague_count = sum(1 for term in vague_terms if term in content.lower())
        
        if vague_count > 5:
            warnings.append(f"Analysis contains {vague_count} vague terms - may lack specificity")
        
        # Check for technical depth
        technical_terms = ["lighting", "camera", "composition", "color", "texture", "rendering"]
        technical_coverage = sum(1 for term in technical_terms if term in content.lower())
        
        if technical_coverage < 3:
            warnings.append("Limited technical depth detected")
        
        return {
            "is_valid": len(issues) == 0,
            "confidence_adjustment": 1.0 - (len(issues) * 0.2) - (len(warnings) * 0.05),
            "issues": issues,
            "warnings": warnings,
            "technical_coverage_score": technical_coverage / len(technical_terms)
        }
