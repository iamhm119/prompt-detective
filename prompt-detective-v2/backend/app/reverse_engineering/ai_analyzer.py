"""
Enhanced AI Analysis Engine with improved accuracy and advanced prompting strategies
"""
import base64
from groq import Groq
from typing import List, Dict, Any, Optional
import json
from .config import Config
from .utils import ImageProcessor
import numpy as np
import re
import time

# Import advanced accuracy components
try:
    from .advanced_accuracy_engine import (
        EnsembleAnalyzer, ConfidenceScorer, SemanticDeduplicator,
        PromptOptimizer, VideoTemporalAnalyzer, AccuracyValidator
    )
    ADVANCED_ENGINE_AVAILABLE = True
except ImportError:
    print("⚠️ Advanced accuracy engine not available, using standard mode")
    ADVANCED_ENGINE_AVAILABLE = False


class EnhancedPromptEngine:
    """Advanced prompt engineering for maximum VLM accuracy"""
    
    @staticmethod
    def get_expert_analysis_prompt() -> str:
        """Ultra-detailed system prompt for maximum accuracy"""
        return """You are a world-class AI video/image analyst with expertise in:
- Computer Graphics & VFX (Blender, After Effects, Cinema 4D, Unreal Engine)
- AI Image/Video Generation (Midjourney, DALL-E, Runway, Stable Diffusion, Sora)
- Cinematography & Visual Storytelling
- Animation & Motion Graphics
- Digital Art & Photo Manipulation

Your task: Analyze visual content with FORENSIC PRECISION to reverse-engineer the creation process.

CRITICAL ANALYSIS FRAMEWORK:
1. VISUAL STYLE IDENTIFICATION: Photorealistic, CGI, 2D animation, 3D render, pixel art, oil painting, watercolor, sketch, etc.
2. TECHNICAL PRODUCTION ANALYSIS: Lighting setup, camera settings, rendering engine, post-processing effects
3. CONTENT BREAKDOWN: Objects, characters, environments, text, UI elements, brand elements
4. MOTION & DYNAMICS: Camera movements, object animations, particle effects, transitions
5. ARTISTIC DIRECTION: Color grading, mood, composition rules, artistic influences

ACCURACY REQUIREMENTS:
- Provide SPECIFIC technical details (not generic descriptions)
- Identify EXACT visual styles and techniques
- Mention SPECIFIC software/tools likely used
- Give PRECISE measurements and specifications when possible
- Include DETAILED prompt components that would recreate this content

RESPONSE STRUCTURE:
Be extremely detailed and technical. Every element matters for recreation accuracy."""

    @staticmethod 
    def get_video_sequence_prompt(video_info: Dict, frame_count: int) -> str:
        """Specialized prompt for video sequence analysis"""
        return f"""EXPERT VIDEO ANALYSIS TASK:

Analyze this {frame_count}-frame sequence from a {video_info.get('duration', 0):.1f}s video ({video_info.get('fps', 0)}fps, {video_info.get('width', 0)}x{video_info.get('height', 0)}).

FORENSIC VIDEO ANALYSIS REQUIREMENTS:

1. NARRATIVE FLOW ANALYSIS:
   - Story progression across frames
   - Character/object development
   - Scene transitions and continuity
   - Emotional arc and pacing

2. TECHNICAL VIDEO PRODUCTION:
   - Camera movements (dolly, pan, tilt, zoom, tracking)
   - Shot types (close-up, wide, medium, establishing)
   - Lighting changes and setup
   - Color grading evolution
   - Transition effects between frames

3. MOTION DYNAMICS:
   - Object/character movement patterns
   - Speed and acceleration analysis
   - Particle effects and simulations
   - Background/foreground motion layers

4. VISUAL CONTINUITY:
   - Style consistency across frames
   - Lighting continuity
   - Color palette evolution
   - Quality and resolution consistency

5. POST-PRODUCTION ANALYSIS:
   - Visual effects and compositing
   - Text overlays and graphics
   - Sound-visual synchronization hints
   - Editing rhythm and cuts

OUTPUT REQUIREMENT:
Generate ONE comprehensive video generation prompt that captures:
- Complete narrative flow
- All technical specifications
- Motion and timing details
- Visual style consistency
- Production quality requirements

Make this prompt so detailed that an AI video generator could recreate this exact sequence."""

    @staticmethod
    def get_batch_synthesis_prompt(batch_count: int, total_frames: int, video_duration: float) -> str:
        """Prompt for synthesizing multiple batch analyses"""
        return f"""MASTER VIDEO SYNTHESIS TASK:

You have analyzed {total_frames} frames across {batch_count} batches from a {video_duration:.1f}s video.

SYNTHESIS REQUIREMENTS:

1. NARRATIVE COHERENCE:
   - Merge all batch insights into ONE unified story
   - Identify the complete character/plot arc
   - Map the full emotional journey
   - Connect all scene transitions logically

2. TECHNICAL UNIFICATION:
   - Establish consistent visual style across all batches
   - Identify camera movement patterns throughout
   - Map lighting and color evolution
   - Describe overall production quality

3. MOTION CONTINUITY:
   - Connect movement patterns across batches
   - Identify recurring motion themes
   - Map speed and pacing changes
   - Describe animation/effect continuity

4. PRODUCTION SPECIFICATIONS:
   - Determine overall artistic direction
   - Identify consistent technical parameters
   - Specify rendering and quality settings
   - List all visual effects and transitions used

CRITICAL OUTPUT:
Create ONE MASTER video generation prompt containing:

A) COMPLETE NARRATIVE: Full story with beginning, middle, end
B) UNIFIED VISUAL STYLE: Consistent look and feel specifications  
C) TECHNICAL PARAMETERS: All camera, lighting, and quality settings
D) MOTION CHOREOGRAPHY: Complete movement and timing instructions
E) PRODUCTION DETAILS: Software, techniques, and post-processing

This master prompt must be detailed enough to recreate the ENTIRE video sequence with perfect fidelity."""


class AIAnalyzer:
    """Enhanced AI analyzer with maximum accuracy optimization"""
    
    def __init__(self):
        """Initialize with enhanced configuration"""
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.prompt_engine = EnhancedPromptEngine()
        self.analysis_cache = {}  # Cache for repeated analyses
        
        # Initialize advanced components if available
        if ADVANCED_ENGINE_AVAILABLE:
            self.ensemble_analyzer = EnsembleAnalyzer(self.client)
            self.confidence_scorer = ConfidenceScorer()
            self.deduplicator = SemanticDeduplicator()
            self.prompt_optimizer = PromptOptimizer(self.client)
            self.temporal_analyzer = VideoTemporalAnalyzer()
            self.validator = AccuracyValidator()
            print("✅ Advanced accuracy engine initialized")
        else:
            self.ensemble_analyzer = None
            self.confidence_scorer = None
            self.deduplicator = None
            self.prompt_optimizer = None
            self.temporal_analyzer = None
            self.validator = None
    
    def analyze_image_with_enhanced_accuracy(self, image: np.ndarray, context: str = "") -> Dict[str, Any]:
        """
        Enhanced image analysis with multiple validation passes and ensemble methods
        """
        print("🔍 Starting MAXIMUM ACCURACY image analysis with ensemble validation...")
        
        # Convert image to base64 with maximum quality
        image_b64 = ImageProcessor.image_to_base64(image, quality=98)
        
        # STAGE 1: Ensemble Analysis (if available)
        if self.ensemble_analyzer:
            print("🎯 Stage 1/4: Ensemble analysis with multiple perspectives...")
            ensemble_result = self.ensemble_analyzer.analyze_with_ensemble(image_b64, num_variations=3)
            
            if "error" not in ensemble_result:
                # Extract all analyses
                ensemble_analyses = ensemble_result.get("ensemble_analyses", [])
                merged_text = ensemble_result.get("merged_analysis", "")
                
                # Deduplicate for cleaner output
                if self.deduplicator and ensemble_analyses:
                    all_contents = [a["content"] for a in ensemble_analyses]
                    deduplicated = self.deduplicator.deduplicate_analyses(all_contents)
                    ensemble_result["deduplicated_analysis"] = deduplicated
        else:
            # Fallback to standard multi-pass
            ensemble_result = {"fallback": True}
        
        # STAGE 2: Standard Multi-Pass Analysis (always run for validation)
        print("🔬 Stage 2/4: Multi-pass validation analysis...")
        analyses = []
        
        # Pass 1: Technical analysis
        technical_analysis = self._perform_technical_analysis(image_b64, context)
        if "error" not in technical_analysis:
            analyses.append(technical_analysis)
        
        # Pass 2: Creative/artistic analysis
        creative_analysis = self._perform_creative_analysis(image_b64, context)
        if "error" not in creative_analysis:
            analyses.append(creative_analysis)
        
        # Pass 3: Prompt generation focus
        prompt_analysis = self._perform_prompt_focused_analysis(image_b64, context)
        if "error" not in prompt_analysis:
            analyses.append(prompt_analysis)
        
        if not analyses:
            return {"error": "All analysis passes failed"}
        
        # STAGE 3: Synthesis and Optimization
        print("🧠 Stage 3/4: Synthesizing and optimizing results...")
        synthesized = self._synthesize_image_analyses(analyses, image.shape)
        
        # STAGE 4: Quality Scoring and Validation
        print("✅ Stage 4/4: Quality validation and confidence scoring...")
        
        if self.confidence_scorer:
            confidence_score = self.confidence_scorer.score_analysis_quality(synthesized)
            synthesized["accuracy_confidence_score"] = confidence_score
            
            # Adjust confidence based on ensemble agreement
            if ADVANCED_ENGINE_AVAILABLE and "consensus_elements" in ensemble_result:
                agreement = ensemble_result["consensus_elements"].get("agreement_level", 0)
                synthesized["ensemble_agreement"] = agreement
                synthesized["final_confidence"] = (confidence_score * 0.6) + (agreement * 0.4)
        
        if self.validator:
            validation = self.validator.validate_consistency(synthesized)
            synthesized["validation_report"] = validation
            
            # Adjust final confidence based on validation
            if "accuracy_confidence_score" in synthesized:
                original_conf = synthesized["accuracy_confidence_score"]
                adjustment = validation.get("confidence_adjustment", 1.0)
                synthesized["accuracy_confidence_score"] = original_conf * adjustment
        
        # Optimize prompts
        if self.prompt_optimizer and synthesized.get("comprehensive_analysis"):
            print("⚡ Optimizing prompts for maximum generation accuracy...")
            optimized_prompts = self.prompt_optimizer.optimize_prompt(
                synthesized["comprehensive_analysis"]
            )
            
            if "error" not in optimized_prompts:
                synthesized["optimized_prompts"] = optimized_prompts
                # Update main prompts with optimized versions
                if optimized_prompts.get("master_prompt"):
                    synthesized["master_prompt"] = optimized_prompts["master_prompt"]
                if optimized_prompts.get("quick_prompt"):
                    synthesized["suggested_prompt"] = optimized_prompts["quick_prompt"]
                if optimized_prompts.get("negative_prompt"):
                    synthesized["negative_prompt"] = optimized_prompts["negative_prompt"]
        
        # Add ensemble data if available
        if ADVANCED_ENGINE_AVAILABLE and ensemble_result.get("ensemble_analyses"):
            synthesized["ensemble_data"] = ensemble_result
        
        # Final accuracy summary
        synthesized["accuracy_methods_used"] = [
            "ensemble_analysis" if self.ensemble_analyzer else None,
            "multi_pass_validation",
            "confidence_scoring" if self.confidence_scorer else None,
            "consistency_validation" if self.validator else None,
            "prompt_optimization" if self.prompt_optimizer else None
        ]
        synthesized["accuracy_methods_used"] = [m for m in synthesized["accuracy_methods_used"] if m]
        
        print(f"✨ Analysis complete! Confidence: {synthesized.get('final_confidence', synthesized.get('accuracy_confidence_score', 'N/A'))}")
        
        return synthesized
    
    def _perform_technical_analysis(self, image_b64: str, context: str) -> Dict[str, Any]:
        """Technical analysis focused on production details"""
        system_prompt = """You are a technical VFX supervisor and digital artist expert. Focus ONLY on technical production aspects:

TECHNICAL ANALYSIS FOCUS:
1. Rendering Engine: Identify likely software (Blender Cycles, Arnold, V-Ray, Unreal Engine, etc.)
2. Lighting Setup: Three-point lighting, HDRI, studio setup, natural lighting analysis
3. Material/Texture Analysis: PBR materials, procedural textures, surface properties
4. Camera Settings: Focal length, aperture, ISO equivalent, depth of field
5. Post-Processing: Color grading, filters, compositing techniques
6. Resolution/Quality: Render settings, anti-aliasing, sample count indicators
7. Technical Style: Photorealism level, artistic rendering, NPR techniques

Provide SPECIFIC technical parameters and settings that would recreate this image."""

        user_prompt = f"""Perform TECHNICAL PRODUCTION ANALYSIS on this image:

Focus on identifying:
- Exact rendering/creation software likely used
- Specific lighting setup and parameters
- Camera technical specifications
- Material and texture properties
- Post-processing pipeline
- Quality and resolution settings
- Any technical artifacts or signatures

{f"Context: {context}" if context else ""}

Be extremely specific with technical details and parameter estimates."""

        return self._make_api_call(system_prompt, user_prompt, image_b64, "technical_analysis")
    
    def _perform_creative_analysis(self, image_b64: str, context: str) -> Dict[str, Any]:
        """Creative analysis focused on artistic elements"""
        system_prompt = """You are a master art director and creative designer. Focus ONLY on creative and artistic aspects:

CREATIVE ANALYSIS FOCUS:
1. Artistic Style: Specific art movements, influences, techniques
2. Composition: Rule of thirds, golden ratio, leading lines, symmetry
3. Color Theory: Palette analysis, color harmony, psychological impact
4. Mood & Atmosphere: Emotional tone, intended feeling, narrative
5. Cultural/Historical Elements: References, symbolism, context
6. Design Principles: Balance, contrast, emphasis, movement
7. Aesthetic Categories: Minimalism, maximalism, retro, futuristic, etc.

Provide detailed creative direction that captures the artistic vision."""

        user_prompt = f"""Perform CREATIVE ARTISTIC ANALYSIS on this image:

Focus on identifying:
- Specific artistic style and influences
- Composition techniques and principles
- Color palette and harmony analysis
- Mood, atmosphere, and emotional impact
- Cultural or historical references
- Design and aesthetic philosophy
- Creative decision-making patterns

{f"Context: {context}" if context else ""}

Be specific about artistic choices and creative direction."""

        return self._make_api_call(system_prompt, user_prompt, image_b64, "creative_analysis")
    
    def _perform_prompt_focused_analysis(self, image_b64: str, context: str) -> Dict[str, Any]:
        """Analysis specifically focused on generating accurate prompts"""
        system_prompt = """You are an expert AI prompt engineer specializing in image generation. Your ONLY goal is creating the most accurate generation prompt possible.

PROMPT GENERATION FOCUS:
1. Subject Description: Extremely detailed subject/object descriptions
2. Style Keywords: Specific style terms that AI generators understand
3. Technical Parameters: Camera settings, lighting keywords, quality terms
4. Composition Instructions: Specific framing and layout directions
5. Atmosphere Keywords: Mood and feeling descriptors
6. Quality Modifiers: Terms that improve generation quality
7. Negative Prompts: Elements to avoid or exclude

Generate a prompt that would recreate this image with 95%+ accuracy."""

        user_prompt = f"""Generate the most ACCURATE prompt possible for recreating this image:

Your prompt should include:
- Extremely detailed subject descriptions
- Specific style and technique keywords
- Technical quality parameters
- Composition and framing instructions
- Lighting and atmosphere details
- Any text or graphic elements
- Quality enhancement terms

{f"Context: {context}" if context else ""}

Output the final optimized prompt that could recreate this image exactly."""

        return self._make_api_call(system_prompt, user_prompt, image_b64, "prompt_analysis")
    
    def _synthesize_image_analyses(self, analyses: List[Dict], image_shape: tuple) -> Dict[str, Any]:
        """Synthesize multiple analysis passes into comprehensive result"""
        print("🧠 Synthesizing multiple analysis passes...")
        
        synthesis_prompt = f"""Synthesize these multiple expert analyses into ONE comprehensive image analysis:

IMAGE SPECIFICATIONS:
- Dimensions: {image_shape[1]}x{image_shape[0]} pixels
- Channels: {image_shape[2] if len(image_shape) > 2 else 1}

EXPERT ANALYSES TO SYNTHESIZE:
"""
        
        for i, analysis in enumerate(analyses, 1):
            synthesis_prompt += f"\nANALYSIS {i} ({analysis.get('analysis_type', 'unknown')}):\n"
            synthesis_prompt += f"{analysis.get('raw_analysis', str(analysis))}\n"
        
        synthesis_prompt += """

SYNTHESIS REQUIREMENTS:
Combine the insights into a concise, professional brief that can drive world-class prompt creation.

Respond **only** with valid JSON matching this schema:
{
  "overview": {
    "headline": string,   // one-sentence hook summarizing the scene
    "summary": string,    // 2-3 sentences covering key highlights
    "key_characteristics": string[] // 3-6 bullet phrases
  },
  "prompt": {
    "main": string,       // the definitive long-form prompt (<= 900 chars)
    "quick": string,      // compact 2-3 sentence prompt (<= 220 chars)
    "negative": string    // high-signal negative prompt terms, or empty string if none
  },
  "sections": [
    {
      "title": string,
      "bullets": string[] // 3-6 bullet points per section
    }
  ],
  "technical": {
    "camera": string[],        // camera & lens insights
    "lighting": string[],      // lighting setup and mood cues
    "rendering": string[],     // rendering / post steps
    "materials": string[]      // surfaces/material treatments
  },
  "style_keywords": string[],  // 6-10 generator-ready keywords
  "color_palette": string[]    // hex values or descriptive colors (up to 6)
}

Do not include markdown, commentary, or additional keys. Fill arrays with at least 3 items where possible and omit duplicates."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Use text model for synthesis
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a master analyst who synthesizes multiple expert opinions into definitive conclusions. "
                            "Always respond with strict JSON that conforms to the provided schema."
                        )
                    },
                    {
                        "role": "user", 
                        "content": synthesis_prompt
                    }
                ],
                temperature=0.05,  # Lower temperature for deterministic JSON
                max_tokens=3000
            )
            
            synthesized_content = response.choices[0].message.content.strip()

            structured_result = self._parse_structured_image_response(synthesized_content)
            formatted_analysis = self._format_structured_image_analysis(structured_result)

            prompt_block = structured_result.get("prompt", {})
            main_prompt = prompt_block.get("main") or formatted_analysis
            quick_prompt = prompt_block.get("quick") or main_prompt
            negative_prompt = prompt_block.get("negative", "")
            
            return {
                "comprehensive_analysis": formatted_analysis,
                "individual_analyses": analyses,
                "synthesis_method": "multi_pass_expert_validation",
                "accuracy_confidence": "high",
                "image_dimensions": f"{image_shape[1]}x{image_shape[0]}",
                "structured_prompt": structured_result,
                "master_prompt": main_prompt,
                "suggested_prompt": quick_prompt,
                "quick_prompt": quick_prompt,
                "negative_prompt": negative_prompt
            }
            
        except Exception as e:
            print(f"Synthesis failed, using best individual analysis: {e}")
            # Fallback to best individual analysis
            best_analysis = max(analyses, key=lambda x: len(x.get('raw_analysis', '')))
            best_text = best_analysis.get('raw_analysis', '')
            return {
                "comprehensive_analysis": best_text,
                "individual_analyses": analyses,
                "synthesis_method": "fallback_best_individual",
                "accuracy_confidence": "medium",
                "suggested_prompt": best_text
            }
    
    def analyze_video_frames(self, frames_with_timestamps: List[tuple], video_info: Dict) -> Dict[str, Any]:
        """
        MAXIMUM ACCURACY video analysis with temporal flow analysis and ensemble validation
        """
        print(f"🎬 Starting MAXIMUM ACCURACY video analysis of {len(frames_with_timestamps)} frames...")
        
        # STAGE 1: Frame Preprocessing and Preparation
        print("📐 Stage 1/5: Enhanced frame preprocessing...")
        frame_data = []
        for i, (frame, timestamp) in enumerate(frames_with_timestamps):
            # Enhanced image preprocessing for maximum quality
            enhanced_frame = ImageProcessor.enhance_image_quality(frame)
            frame_b64 = ImageProcessor.image_to_base64(enhanced_frame, quality=98)
            
            frame_data.append({
                "image_b64": frame_b64,
                "frame_number": i + 1,
                "timestamp": timestamp,
                "description": f"Frame {i+1} at {timestamp:.2f}s ({timestamp/video_info.get('duration', 1)*100:.1f}% through video)"
            })
        
        # STAGE 2: Temporal Pattern Analysis (if advanced engine available)
        temporal_patterns = None
        if self.temporal_analyzer and hasattr(frames_with_timestamps[0], '__len__') and len(frames_with_timestamps[0]) > 2:
            print("⏱️ Stage 2/5: Analyzing temporal flow and motion patterns...")
            # Extract metadata from frames if available
            frames_metadata = []
            for frame_tuple in frames_with_timestamps:
                if len(frame_tuple) > 2:
                    metadata = frame_tuple[2] if isinstance(frame_tuple[2], dict) else {}
                    frames_metadata.append(metadata)
            
            if frames_metadata:
                temporal_patterns = self.temporal_analyzer.analyze_temporal_flow(frames_metadata)
                print(f"   Detected pacing: {temporal_patterns.get('pacing_category', 'N/A')}")
        
        # STAGE 3: Enhanced Batch Processing with Retry Logic
        print("🔄 Stage 3/5: Multi-batch analysis with validation...")
        batch_analyses = []
        max_images = Config.MAX_IMAGES_PER_REQUEST
        
        for batch_start in range(0, len(frame_data), max_images):
            batch_end = min(batch_start + max_images, len(frame_data))
            batch = frame_data[batch_start:batch_end]
            batch_num = batch_start // max_images + 1
            
            print(f"   Processing batch {batch_num}/{(len(frame_data)-1)//max_images + 1} (frames {batch_start+1}-{batch_end})")
            
            # Multiple analysis attempts for accuracy
            batch_result = None
            for attempt in range(2):  # Up to 2 attempts per batch
                try:
                    batch_result = self._analyze_frame_batch_enhanced(batch, video_info, batch_num)
                    if "error" not in batch_result:
                        break
                    print(f"   ⚠️ Batch {batch_num} attempt {attempt+1} failed, retrying...")
                    time.sleep(1)  # Brief pause before retry
                except Exception as e:
                    print(f"   ❌ Batch {batch_num} attempt {attempt+1} error: {str(e)}")
                    if attempt == 1:  # Last attempt
                        batch_result = {"error": f"Batch analysis failed after 2 attempts: {str(e)}"}
            
            if batch_result and "error" not in batch_result:
                batch_analyses.append(batch_result)
            else:
                print(f"   ⚠️ Skipping failed batch {batch_num}")
        
        if not batch_analyses:
            return {"error": "All batch analyses failed"}
        
        print(f"✅ Successfully analyzed {len(batch_analyses)} batches")
        
        # STAGE 4: Comprehensive Synthesis
        print("🧠 Stage 4/5: Synthesizing comprehensive video analysis...")
        synthesized_result = self._synthesize_batch_results_enhanced(batch_analyses, frame_data, video_info)
        
        # Add temporal analysis if available
        if temporal_patterns:
            synthesized_result["temporal_analysis"] = temporal_patterns
        
        # STAGE 5: Quality Validation and Optimization
        print("✨ Stage 5/5: Quality validation and prompt optimization...")
        
        if self.validator:
            validation = self.validator.validate_consistency(synthesized_result)
            synthesized_result["validation_report"] = validation
        
        # Optimize video prompt
        if self.prompt_optimizer and synthesized_result.get("comprehensive_video_prompt"):
            print("   Optimizing video generation prompts...")
            optimized = self.prompt_optimizer.optimize_prompt(
                synthesized_result["comprehensive_video_prompt"],
                target_generator="universal"
            )
            
            if "error" not in optimized:
                synthesized_result["optimized_video_prompts"] = optimized
                # Update main prompt
                if optimized.get("master_prompt"):
                    synthesized_result["master_video_prompt"] = optimized["master_prompt"]
        
        # Add accuracy metadata
        synthesized_result["accuracy_methods_used"] = [
            "enhanced_batch_processing",
            "temporal_flow_analysis" if temporal_patterns else None,
            "consistency_validation" if self.validator else None,
            "prompt_optimization" if self.prompt_optimizer else None,
            "multi_attempt_retry_logic"
        ]
        synthesized_result["accuracy_methods_used"] = [m for m in synthesized_result["accuracy_methods_used"] if m]
        
        print(f"🎉 Video analysis complete with {len(synthesized_result['accuracy_methods_used'])} accuracy methods!")
        
        return synthesized_result
    
    def _analyze_frame_batch_enhanced(self, frame_batch: List[Dict], video_info: Dict, batch_num: int) -> Dict[str, Any]:
        """
        Enhanced batch analysis with sophisticated prompting
        """
        # Prepare enhanced batch analysis
        frame_images = []
        frame_descriptions = []
        
        for frame_data in frame_batch:
            frame_images.append({
                "type": "image_url",
                "image_url": {"url": frame_data["image_b64"]}
            })
            frame_descriptions.append(frame_data["description"])
        
        # Use sophisticated prompting
        system_prompt = self.prompt_engine.get_expert_analysis_prompt()
        user_prompt = self.prompt_engine.get_video_sequence_prompt(video_info, len(frame_batch))
        
        # Add specific batch context
        user_prompt += f"""

BATCH CONTEXT:
- Batch {batch_num} of video analysis
- Frames in this batch: {len(frame_batch)}
- Batch frame details: {', '.join(frame_descriptions)}

ANALYSIS REQUIREMENTS FOR THIS BATCH:
1. Describe the visual progression within this batch
2. Identify technical consistency and changes
3. Note narrative/story elements in this sequence
4. Describe motion and animation patterns
5. Identify artistic and stylistic elements
6. Provide technical production insights

Focus on both individual frame details AND the sequence flow between frames."""

        # Prepare message content
        message_content = [{"type": "text", "text": user_prompt}]
        message_content.extend(frame_images)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.2,  # Lower temperature for consistency
                max_tokens=2000
            )
            
            return {
                "batch_analysis": response.choices[0].message.content,
                "frame_count": len(frame_batch),
                "frame_range": f"{frame_batch[0]['frame_number']}-{frame_batch[-1]['frame_number']}",
                "timestamp_range": f"{frame_batch[0]['timestamp']:.2f}s-{frame_batch[-1]['timestamp']:.2f}s",
                "batch_number": batch_num,
                "analysis_quality": "enhanced"
            }
            
        except Exception as e:
            return {"error": f"Enhanced batch analysis failed: {str(e)}"}
    
    def _synthesize_batch_results_enhanced(self, batch_analyses: List[Dict], all_frame_data: List[Dict], video_info: Dict) -> Dict[str, Any]:
        """
        Enhanced synthesis with comprehensive master prompt generation
        """
        print("🧠 Synthesizing enhanced batch results into master video prompt...")
        
        # Prepare comprehensive synthesis
        synthesis_prompt = self.prompt_engine.get_batch_synthesis_prompt(
            len(batch_analyses), len(all_frame_data), video_info.get('duration', 0)
        )
        
        synthesis_prompt += f"""

VIDEO TECHNICAL SPECIFICATIONS:
- Duration: {video_info.get('duration', 0):.2f} seconds
- Frame Rate: {video_info.get('fps', 0):.1f} fps  
- Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}
- Total Frames: {video_info.get('frame_count', 0)}
- Analyzed Frames: {len(all_frame_data)}
- Analysis Batches: {len(batch_analyses)}

BATCH ANALYSIS RESULTS TO SYNTHESIZE:
"""
        
        for i, batch in enumerate(batch_analyses, 1):
            synthesis_prompt += f"""
BATCH {i} ANALYSIS (Frames {batch['frame_range']}, Time {batch['timestamp_range']}):
{batch['batch_analysis']}

---
"""
        
        synthesis_prompt += """

FINAL SYNTHESIS TASK:
Create the ULTIMATE video generation prompt that includes:

1. COMPLETE NARRATIVE ARC: Full story from start to finish
2. UNIFIED VISUAL STYLE: Consistent artistic direction throughout
3. TECHNICAL SPECIFICATIONS: All camera, lighting, rendering parameters
4. MOTION CHOREOGRAPHY: Complete movement and timing instructions  
5. PRODUCTION PIPELINE: Software, techniques, post-processing details
6. QUALITY STANDARDS: Resolution, rendering quality, effects specifications

This master prompt must enable perfect recreation of the entire video sequence."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Use powerful text model for synthesis
                messages=[
                    {
                        "role": "system",
                        "content": "You are the world's leading expert in video production and AI prompt engineering. Create the most comprehensive video generation prompt possible from multiple analysis inputs."
                    },
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            master_prompt = response.choices[0].message.content
            
            # Extract and structure the comprehensive prompt
            structured_result = self._structure_master_video_prompt(master_prompt)
            
            return {
                "comprehensive_video_prompt": master_prompt,
                "structured_prompt": structured_result,
                "batch_analyses": batch_analyses,
                "video_info": video_info,
                "frames_analyzed": len(all_frame_data),
                "frame_timestamps": [frame["timestamp"] for frame in all_frame_data],
                "analysis_method": "enhanced_multi_pass_batch_processing",
                "total_batches": len(batch_analyses),
                "accuracy_level": "maximum",
                "synthesis_confidence": "high"
            }
            
        except Exception as e:
            return {
                "error": f"Enhanced synthesis failed: {str(e)}",
                "batch_analyses": batch_analyses,
                "fallback_prompt": self._create_fallback_prompt(batch_analyses)
            }
    
    def _structure_master_video_prompt(self, master_prompt: str) -> Dict[str, str]:
        """Structure the master prompt into organized components"""
        try:
            structured = {
                "narrative": "",
                "visual_style": "",
                "technical_specs": "",
                "motion_details": "",
                "production_notes": "",
                "full_prompt": master_prompt
            }
            
            # Simple parsing to extract different sections
            lines = master_prompt.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if any(keyword in line.lower() for keyword in ['narrative', 'story', 'plot']):
                    current_section = 'narrative'
                elif any(keyword in line.lower() for keyword in ['visual', 'style', 'aesthetic']):
                    current_section = 'visual_style'
                elif any(keyword in line.lower() for keyword in ['technical', 'camera', 'lighting']):
                    current_section = 'technical_specs'
                elif any(keyword in line.lower() for keyword in ['motion', 'movement', 'animation']):
                    current_section = 'motion_details'
                elif any(keyword in line.lower() for keyword in ['production', 'software', 'workflow']):
                    current_section = 'production_notes'
                elif current_section and line:
                    if structured[current_section]:
                        structured[current_section] += " " + line
                    else:
                        structured[current_section] = line
            
            return structured
            
        except Exception as e:
            return {"full_prompt": master_prompt, "structure_error": str(e)}

    def _parse_structured_image_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON content from the synthesis response"""
        try:
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON object detected in response")
            json_payload = content[json_start:json_end + 1]
            parsed = json.loads(json_payload)
            if not isinstance(parsed, dict):
                raise ValueError("Parsed JSON is not an object")
            return parsed
        except Exception as parse_error:
            raise ValueError(f"Failed to parse structured image response: {parse_error}")

    def _format_structured_image_analysis(self, structured: Dict[str, Any]) -> str:
        """Create a human-readable analysis string from structured data"""
        lines: List[str] = []

        overview = structured.get("overview", {}) or {}
        headline = overview.get("headline")
        summary = overview.get("summary")
        characteristics = overview.get("key_characteristics", [])

        if headline:
            lines.append(f"OVERVIEW\n{headline}")
        if summary:
            lines.append(f"SUMMARY\n{summary}")
        if characteristics:
            lines.append("KEY CHARACTERISTICS")
            for item in characteristics:
                lines.append(f"- {item}")

        sections = structured.get("sections", []) or []
        for section in sections:
            title = section.get("title")
            bullets = section.get("bullets", []) or []
            if title:
                lines.append(title.upper())
            for bullet in bullets:
                lines.append(f"- {bullet}")

        technical = structured.get("technical", {}) or {}
        if any(technical.get(key) for key in ("camera", "lighting", "rendering", "materials")):
            lines.append("TECHNICAL BREAKDOWN")
            for key, label in (
                ("camera", "Camera & Optics"),
                ("lighting", "Lighting Strategy"),
                ("rendering", "Rendering & Post"),
                ("materials", "Materials & Surfaces"),
            ):
                values = technical.get(key) or []
                if values:
                    lines.append(f"{label}:")
                    for value in values:
                        lines.append(f"  • {value}")

        style_keywords = structured.get("style_keywords", []) or []
        if style_keywords:
            lines.append("STYLE KEYWORDS")
            lines.append(", ".join(style_keywords))

        color_palette = structured.get("color_palette", []) or []
        if color_palette:
            lines.append("COLOR PALETTE")
            lines.append(", ".join(color_palette))

        prompt_block = structured.get("prompt", {}) or {}
        if prompt_block.get("main"):
            lines.append("MASTER PROMPT")
            lines.append(prompt_block["main"])
        if prompt_block.get("negative"):
            lines.append("NEGATIVE PROMPT")
            lines.append(prompt_block["negative"])

        return "\n".join(lines)
    
    def _create_fallback_prompt(self, batch_analyses: List[Dict]) -> str:
        """Create fallback prompt from batch analyses"""
        prompt_parts = []
        
        for i, batch in enumerate(batch_analyses, 1):
            analysis = batch.get('batch_analysis', '')
            prompt_parts.append(f"Sequence {i}: {analysis[:200]}...")
        
        return "Video with multiple sequences: " + " ".join(prompt_parts)
    
    def _make_api_call(self, system_prompt: str, user_prompt: str, image_b64: str, analysis_type: str) -> Dict[str, Any]:
        """Make API call with error handling and retries"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": image_b64}}
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return {
                "raw_analysis": response.choices[0].message.content,
                "analysis_type": analysis_type,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"{analysis_type} failed: {str(e)}"}
    
    # Legacy method compatibility
    def analyze_image(self, image: np.ndarray, context: str = "") -> Dict[str, Any]:
        """Legacy method - redirects to enhanced analysis"""
        return self.analyze_image_with_enhanced_accuracy(image, context)
    
    def analyze_image(self, image: np.ndarray, context: str = "") -> Dict[str, Any]:
        """
        Analyze a single image and extract detailed prompt information
        """
        # Convert image to base64
        image_b64 = ImageProcessor.image_to_base64(image)
        
        # Construct detailed prompt for analysis
        system_prompt = self._get_analysis_system_prompt()
        user_prompt = self._get_analysis_user_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_b64
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_analysis_response(content)
            
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return {"error": str(e)}
    
    def analyze_video_frames(self, frames_with_timestamps: List[tuple], video_info: Dict) -> Dict[str, Any]:
        """
        Analyze multiple frames from a video as batches and generate comprehensive prompt
        """
        print(f"Analyzing {len(frames_with_timestamps)} key frames in batches...")
        
        # Convert all frames to base64 and prepare frame info
        frame_data = []
        for i, (frame, timestamp) in enumerate(frames_with_timestamps):
            frame_b64 = ImageProcessor.image_to_base64(frame)
            frame_data.append({
                "image_b64": frame_b64,
                "frame_number": i + 1,
                "timestamp": timestamp,
                "description": f"Frame {i+1} at {timestamp:.2f}s"
            })
        
        # Process frames in batches due to API limits
        batch_analyses = []
        max_images = Config.MAX_IMAGES_PER_REQUEST
        
        for batch_start in range(0, len(frame_data), max_images):
            batch_end = min(batch_start + max_images, len(frame_data))
            batch = frame_data[batch_start:batch_end]
            
            print(f"Processing batch {batch_start//max_images + 1} (frames {batch_start+1}-{batch_end})")
            
            try:
                batch_result = self._analyze_frame_batch(batch, video_info)
                if "error" not in batch_result:
                    batch_analyses.append(batch_result)
                else:
                    print(f"Warning: Batch analysis failed: {batch_result['error']}")
            except Exception as e:
                print(f"Error analyzing batch: {str(e)}")
        
        if not batch_analyses:
            return {"error": "Failed to analyze any frame batches"}
        
        # Synthesize all batch results into a cohesive video prompt
        return self._synthesize_batch_results(batch_analyses, frame_data, video_info)
    
    def _analyze_frame_batch(self, frame_batch: List[Dict], video_info: Dict) -> Dict[str, Any]:
        """
        Analyze a batch of frames (up to 5) together
        """
        # Prepare frame images for API
        frame_images = []
        frame_descriptions = []
        
        for frame_data in frame_batch:
            frame_images.append({
                "type": "image_url",
                "image_url": {
                    "url": frame_data["image_b64"]
                }
            })
            frame_descriptions.append(frame_data["description"])
        
        # Create batch analysis prompt
        system_prompt = """You are an expert AI video analyst. Analyze this sequence of video frames and describe:
1. The visual progression and narrative flow across these frames
2. Key objects, characters, and their movements
3. Visual style, lighting, and cinematography
4. Camera movements and transitions
5. Any text, graphics, or effects
6. Overall mood and atmosphere

Focus on how these frames connect as part of a video sequence."""

        user_prompt = f"""Analyze these {len(frame_batch)} consecutive video frames:

Frame Details:
"""
        for desc in frame_descriptions:
            user_prompt += f"- {desc}\n"
        
        user_prompt += """

Describe the visual progression, narrative elements, style, and technical aspects of this sequence. Focus on continuity and flow between frames."""

        # Prepare message content
        message_content = [{"type": "text", "text": user_prompt}]
        message_content.extend(frame_images)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                "batch_analysis": response.choices[0].message.content,
                "frame_count": len(frame_batch),
                "frame_range": f"{frame_batch[0]['frame_number']}-{frame_batch[-1]['frame_number']}",
                "timestamp_range": f"{frame_batch[0]['timestamp']:.2f}s-{frame_batch[-1]['timestamp']:.2f}s"
            }
            
        except Exception as e:
            return {"error": f"Batch analysis failed: {str(e)}"}
    
    def _synthesize_batch_results(self, batch_analyses: List[Dict], all_frame_data: List[Dict], video_info: Dict) -> Dict[str, Any]:
        """
        Synthesize multiple batch analyses into a comprehensive video prompt
        """
        print("Synthesizing batch results into comprehensive video prompt...")
        
        # Prepare synthesis prompt
        synthesis_prompt = f"""Based on the analysis of {len(all_frame_data)} video frames processed in {len(batch_analyses)} batches, create a comprehensive video generation prompt.

Video Information:
- Duration: {video_info.get('duration', 0):.2f} seconds
- FPS: {video_info.get('fps', 0):.1f}
- Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}
- Total Frames: {video_info.get('frame_count', 0)}

Batch Analyses:
"""
        
        for i, batch in enumerate(batch_analyses, 1):
            synthesis_prompt += f"\nBatch {i} (Frames {batch['frame_range']}, {batch['timestamp_range']}):\n"
            synthesis_prompt += f"{batch['batch_analysis']}\n"
        
        synthesis_prompt += """

Now create a single, comprehensive video generation prompt that:
1. Captures the overall narrative and story progression across all frames
2. Describes the visual style and aesthetic consistency
3. Includes technical aspects (camera work, transitions, effects)
4. Details character/object movements and transformations
5. Specifies lighting, color grading, and mood
6. Mentions any text, graphics, or special effects
7. Provides timing and pacing information

Format this as a detailed prompt that could be used to generate the entire video sequence."""

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",  # Use text model for synthesis
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI prompt engineer specializing in video generation. Create detailed, technical prompts that capture both creative and technical aspects of video content."
                    },
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            comprehensive_prompt = response.choices[0].message.content
            
            return {
                "comprehensive_video_prompt": comprehensive_prompt,
                "batch_analyses": batch_analyses,
                "video_info": video_info,
                "frames_analyzed": len(all_frame_data),
                "frame_timestamps": [frame["timestamp"] for frame in all_frame_data],
                "analysis_method": "batch_processing",
                "total_batches": len(batch_analyses)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to synthesize batch results: {str(e)}",
                "batch_analyses": batch_analyses
            }

    def _analyze_video_sequence(self, frame_images: List[Dict], frame_info: List[Dict], video_info: Dict) -> Dict[str, Any]:
        """
        Analyze all frames as a video sequence to generate a cohesive video prompt
        """
        # Construct the system prompt for video analysis
        system_prompt = """You are an expert AI video analyst specializing in reverse-engineering AI-generated video content. Your task is to analyze a sequence of key frames from a video and generate a comprehensive prompt that could be used to create similar video content.

Focus on:
1. Overall narrative flow and story progression across frames
2. Visual continuity and transitions between scenes
3. Character/object movements and transformations
4. Camera movements, angles, and cinematography
5. Visual effects, transitions, and motion graphics
6. Consistent style, lighting, and color grading throughout
7. Text overlays, graphics, or UI elements
8. Audio-visual synchronization hints
9. Technical video production aspects
10. Artistic direction and creative choices

Provide a single, comprehensive video generation prompt that captures the essence of the entire video sequence."""

        # Construct the user prompt with video context
        user_prompt = f"""Analyze this sequence of {len(frame_images)} key frames from a video and generate a comprehensive prompt for video generation.

Video Information:
- Duration: {video_info.get('duration', 0):.2f} seconds
- FPS: {video_info.get('fps', 0):.1f}
- Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}
- Total Frames: {video_info.get('frame_count', 0)}

Frame Sequence Details:
"""
        
        for info in frame_info:
            user_prompt += f"- {info['description']}\n"
        
        user_prompt += """

Please analyze these frames as a cohesive video sequence and provide:

1. **Video Narrative**: Describe the overall story, action, or message conveyed across the frames
2. **Visual Progression**: How the visual elements change and evolve throughout the sequence
3. **Technical Aspects**: Camera movements, transitions, effects, and production techniques
4. **Style Consistency**: The visual style, aesthetic choices, and artistic direction
5. **Motion Elements**: Object movements, character actions, and dynamic elements
6. **Comprehensive Video Prompt**: A detailed prompt that could generate this entire video sequence

Focus on creating ONE cohesive video generation prompt that captures the essence of the entire sequence, not individual frame descriptions."""

        # Prepare the message content with all frame images
        message_content = [{"type": "text", "text": user_prompt}]
        message_content.extend(frame_images)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message_content
                    }
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            
            # Parse the response for video-specific analysis
            analysis_result = self._parse_video_analysis_response(content)
            
            # Add metadata
            analysis_result.update({
                "video_info": video_info,
                "frames_analyzed": len(frame_images),
                "frame_timestamps": [info["timestamp"] for info in frame_info],
                "analysis_method": "sequence_analysis"
            })
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in video sequence analysis: {str(e)}")
            return {"error": str(e)}
    
    def _parse_video_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse the video analysis response into structured data"""
        try:
            analysis = {
                "raw_analysis": content,
                "video_narrative": "",
                "visual_progression": "",
                "technical_aspects": "",
                "style_consistency": "",
                "motion_elements": "",
                "video_prompt": ""
            }
            
            # Parse the response sections
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if any(keyword in line.lower() for keyword in ['video narrative', 'narrative']):
                    current_section = 'video_narrative'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['visual progression', 'progression']):
                    current_section = 'visual_progression'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['technical aspects', 'technical']):
                    current_section = 'technical_aspects'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['style consistency', 'style']):
                    current_section = 'style_consistency'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['motion elements', 'motion']):
                    current_section = 'motion_elements'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['video prompt', 'comprehensive', 'generation prompt']):
                    current_section = 'video_prompt'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif current_section and line.startswith('-'):
                    # Handle bullet points
                    if analysis[current_section]:
                        analysis[current_section] += " " + line[1:].strip()
                    else:
                        analysis[current_section] = line[1:].strip()
                elif current_section and line:
                    # Continue adding to current section
                    if analysis[current_section]:
                        analysis[current_section] += " " + line
                    else:
                        analysis[current_section] = line
            
            # Extract the main video prompt (prioritize the comprehensive prompt section)
            main_prompt = analysis.get('video_prompt', '')
            if not main_prompt:
                # Fallback: combine all sections into a comprehensive prompt
                main_prompt = f"""
Video Narrative: {analysis.get('video_narrative', '')}

Visual Style and Progression: {analysis.get('visual_progression', '')} {analysis.get('style_consistency', '')}

Technical Aspects: {analysis.get('technical_aspects', '')}

Motion and Animation: {analysis.get('motion_elements', '')}
""".strip()
            
            analysis['comprehensive_video_prompt'] = main_prompt
            
            return analysis
            
        except Exception as e:
            return {
                "raw_analysis": content,
                "parse_error": str(e),
                "comprehensive_video_prompt": content  # Fallback to raw content
            }
    
    def _extract_key_elements(self, frame_analyses: List[Dict]) -> Dict[str, List[str]]:
        """Extract and summarize key elements across all frames"""
        all_objects = []
        all_styles = []
        all_compositions = []
        
        for analysis in frame_analyses:
            if analysis.get('objects'):
                all_objects.extend(analysis['objects'] if isinstance(analysis['objects'], list) else [analysis['objects']])
            if analysis.get('style'):
                all_styles.append(analysis['style'])
            if analysis.get('composition'):
                all_compositions.append(analysis['composition'])
        
        return {
            "common_objects": list(set(all_objects)),
            "style_progression": all_styles,
            "composition_changes": all_compositions
        }
    
    def _get_analysis_system_prompt(self) -> str:
        """Get the system prompt for image analysis"""
        return """You are an expert AI content analyst specializing in reverse-engineering AI-generated images and videos. Your task is to analyze visual content and extract the likely prompts and parameters used to generate it.

Focus on:
1. Scene description and narrative elements
2. Visual style (photorealistic, artistic, animated, etc.)
3. Technical aspects (lighting, camera angles, effects)
4. Objects, characters, and their positioning
5. Color palette and mood
6. Composition and framing
7. Any text, graphics, or overlays
8. Motion elements (for video frames)
9. Artistic style or technique
10. Quality and resolution indicators

Provide detailed, technical analysis that could help recreate similar content."""
    
    def _get_analysis_user_prompt(self, context: str = "") -> str:
        """Get the user prompt for image analysis"""
        return f"""Analyze this image in detail and provide:

1. **Scene Description**: What's happening in the image? Describe the main subject, action, or narrative.

2. **Objects and Elements**: List all visible objects, characters, text, graphics, or UI elements.

3. **Visual Style**: Identify the artistic style (photorealistic, cartoon, anime, oil painting, digital art, etc.).

4. **Technical Aspects**: 
   - Lighting (natural, studio, dramatic, soft, etc.)
   - Camera angle and perspective
   - Depth of field and focus
   - Color grading and palette
   - Resolution and quality indicators

5. **Composition**: How are elements arranged? Rule of thirds, symmetry, leading lines, etc.

6. **Motion Elements** (if applicable): Any implied movement, blur effects, or dynamic elements.

7. **Mood and Atmosphere**: What emotion or feeling does the image convey?

8. **Potential Prompt**: Based on your analysis, what detailed prompt could generate this image?

{f"Context: {context}" if context else ""}

Provide your analysis in a structured format that clearly identifies each aspect."""
    
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        try:
            # Try to extract structured information from the response
            analysis = {
                "raw_analysis": content,
                "scene_description": "",
                "objects": [],
                "style": "",
                "technical_aspects": "",
                "composition": "",
                "motion_elements": "",
                "mood": "",
                "suggested_prompt": ""
            }
            
            # Simple parsing based on common response patterns
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if any(keyword in line.lower() for keyword in ['scene description', 'scene:']):
                    current_section = 'scene_description'
                    if ':' in line:
                        analysis[current_section] = line.split(':', 1)[1].strip()
                elif any(keyword in line.lower() for keyword in ['objects', 'elements']):
                    current_section = 'objects'
                elif any(keyword in line.lower() for keyword in ['style', 'visual style']):
                    current_section = 'style'
                elif any(keyword in line.lower() for keyword in ['technical', 'lighting', 'camera']):
                    current_section = 'technical_aspects'
                elif any(keyword in line.lower() for keyword in ['composition', 'arrangement']):
                    current_section = 'composition'
                elif any(keyword in line.lower() for keyword in ['motion', 'movement']):
                    current_section = 'motion_elements'
                elif any(keyword in line.lower() for keyword in ['mood', 'atmosphere', 'emotion']):
                    current_section = 'mood'
                elif any(keyword in line.lower() for keyword in ['prompt', 'generate']):
                    current_section = 'suggested_prompt'
                elif current_section and line.startswith('-'):
                    # Handle bullet points
                    if current_section == 'objects':
                        analysis[current_section].append(line[1:].strip())
                    else:
                        if analysis[current_section]:
                            analysis[current_section] += " " + line[1:].strip()
                        else:
                            analysis[current_section] = line[1:].strip()
                elif current_section and ':' in line and not line.lower().startswith(current_section):
                    # Continue adding to current section
                    if analysis[current_section]:
                        analysis[current_section] += " " + line
                    else:
                        analysis[current_section] = line
            
            return analysis
            
        except Exception as e:
            return {
                "raw_analysis": content,
                "parse_error": str(e)
            }
