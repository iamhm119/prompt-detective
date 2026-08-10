"""
Utilities for image and video processing with advanced frame selection algorithms
"""
import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import List, Tuple, Optional, Dict
import os
from skimage.metrics import structural_similarity as ssim
from skimage.feature import local_binary_pattern
from skimage.filters import sobel
from scipy.spatial.distance import cosine
from scipy.stats import entropy
import logging


class AdvancedFrameSelector:
    """Advanced frame selection using multiple computer vision techniques"""
    
    @staticmethod
    def calculate_visual_complexity(frame: np.ndarray) -> float:
        """Calculate visual complexity using edge density and entropy with error handling"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Texture complexity using Local Binary Pattern
            lbp = local_binary_pattern(gray, 8, 1, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10, range=(0, 9))
            lbp_complexity = entropy(lbp_hist + 1e-7)  # Add small value to avoid log(0)
            
            # Color diversity (histogram entropy)
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            color_entropy = entropy(hist.ravel() + 1e-7)
            
            # Combine metrics
            complexity_score = (edge_density * 0.4 + lbp_complexity * 0.3 + color_entropy * 0.3)
            return float(complexity_score)
            
        except Exception as e:
            # Fallback: simple edge-based complexity
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                return float(edge_density)
            except:
                return 0.1  # Default minimal complexity
    
    @staticmethod
    def calculate_motion_magnitude(frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate motion magnitude using optical flow with robust error handling"""
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Detect corners/features to track
            corners = cv2.goodFeaturesToTrack(gray1, maxCorners=100, 
                                            qualityLevel=0.01, 
                                            minDistance=10)
            
            # Check if we have valid corners
            if corners is None or len(corners) == 0:
                # Fallback: use frame difference method
                diff = cv2.absdiff(gray1, gray2)
                motion_magnitude = np.mean(diff) / 255.0
                return motion_magnitude
            
            # Ensure corners are in the right format
            corners = np.float32(corners).reshape(-1, 1, 2)
            
            # Calculate optical flow
            next_pts, status, error = cv2.calcOpticalFlowPyrLK(gray1, gray2, corners, None)
            
            if next_pts is not None and status is not None:
                # Select good points
                good_old = corners[status == 1]
                good_new = next_pts[status == 1]
                
                if len(good_old) > 0 and len(good_new) > 0:
                    # Calculate motion vectors
                    motion_vectors = good_new - good_old
                    motion_magnitude = np.mean(np.sqrt(np.sum(motion_vectors**2, axis=1)))
                    return float(motion_magnitude)
            
            # Fallback: use frame difference
            diff = cv2.absdiff(gray1, gray2)
            motion_magnitude = np.mean(diff) / 255.0
            return float(motion_magnitude)
            
        except Exception as e:
            # Ultimate fallback: simple frame difference
            try:
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray1, gray2)
                motion_magnitude = np.mean(diff) / 255.0
                return float(motion_magnitude)
            except:
                return 0.0
    
    @staticmethod
    def calculate_frame_importance(frame: np.ndarray, prev_frame: np.ndarray = None, 
                                  next_frame: np.ndarray = None) -> float:
        """Calculate frame importance using multiple factors with robust error handling"""
        try:
            importance_score = 0.0
            
            # Visual complexity (30%)
            complexity = AdvancedFrameSelector.calculate_visual_complexity(frame)
            importance_score += complexity * 0.3
            
            # Motion significance (40%)
            if prev_frame is not None:
                motion = AdvancedFrameSelector.calculate_motion_magnitude(prev_frame, frame)
                importance_score += min(motion / 50.0, 1.0) * 0.4  # Normalize motion
            
            # Object detection score (30%)
            object_score = AdvancedFrameSelector.detect_interesting_objects(frame)
            importance_score += object_score * 0.3
            
            return float(min(importance_score, 1.0))  # Ensure score doesn't exceed 1.0
            
        except Exception as e:
            # Fallback: simple edge-based importance
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                return edge_density
            except:
                return 0.1  # Default minimal importance
    
    @staticmethod
    def detect_interesting_objects(frame: np.ndarray) -> float:
        """Detect interesting objects using contour analysis and feature detection with error handling"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Feature detection using ORB algorithm
            orb = cv2.ORB_create(nfeatures=500)
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            if keypoints is not None:
                feature_density = len(keypoints) / (frame.shape[0] * frame.shape[1]) * 1000000
            else:
                feature_density = 0.0
            
            # Contour detection for object boundaries
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter significant contours
            significant_contours = [c for c in contours if cv2.contourArea(c) > 100]
            contour_score = min(len(significant_contours) / 20.0, 1.0)  # Normalize
            
            # Combine scores
            object_score = (feature_density * 0.6 + contour_score * 0.4)
            return float(min(object_score, 1.0))
            
        except Exception as e:
            # Fallback: use edge density as object score
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                return float(min(edge_density * 5.0, 1.0))  # Scale and normalize
            except:
                return 0.1  # Default minimal score
    
    @staticmethod
    def calculate_color_diversity(frame: np.ndarray) -> float:
        """Calculate color diversity using HSV histogram analysis"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram for each channel
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
        
        # Calculate entropy for each channel
        h_entropy = entropy(h_hist.ravel() + 1e-7)
        s_entropy = entropy(s_hist.ravel() + 1e-7)
        v_entropy = entropy(v_hist.ravel() + 1e-7)
        
        # Combine entropies
        diversity_score = (h_entropy + s_entropy + v_entropy) / 3.0
        return float(min(diversity_score / 8.0, 1.0))  # Normalize


class ImageProcessor:
    """Enhanced image processing operations"""
    
    @staticmethod
    def resize_image(image: np.ndarray, width: int = 1024) -> np.ndarray:
        """Resize image while maintaining aspect ratio with advanced interpolation"""
        height, orig_width = image.shape[:2]
        if orig_width <= width:
            return image
        
        ratio = width / orig_width
        new_height = int(height * ratio)
        
        # Use different interpolation based on scaling
        if ratio < 0.5:
            interpolation = cv2.INTER_AREA  # Better for downscaling
        else:
            interpolation = cv2.INTER_CUBIC  # Better for slight downscaling
            
        return cv2.resize(image, (width, new_height), interpolation=interpolation)
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better VLM analysis"""
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel (brightness)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        enhanced_lab = cv2.merge([l, a, b])
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Apply bilateral filter for noise reduction while preserving edges
        enhanced_bgr = cv2.bilateralFilter(enhanced_bgr, 9, 75, 75)
        
        return enhanced_bgr
    
    @staticmethod
    def convert_to_rgb(image: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB format"""
        if len(image.shape) == 3 and image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    @staticmethod
    def image_to_base64(image: np.ndarray, quality: int = 95) -> str:
        """Convert image to base64 string for API with optimized quality"""
        # Enhance image quality before encoding
        enhanced_image = ImageProcessor.enhance_image_quality(image)
        
        # Convert to PIL Image
        if len(enhanced_image.shape) == 3:
            image_rgb = ImageProcessor.convert_to_rgb(enhanced_image)
            pil_image = Image.fromarray(image_rgb)
        else:
            pil_image = Image.fromarray(enhanced_image)
        
        # Convert to base64 with optimized settings
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    
    @staticmethod
    def calculate_image_difference(img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate enhanced structural similarity between two images"""
        # Convert to grayscale if needed
        if len(img1.shape) == 3:
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        else:
            gray1 = img1
            
        if len(img2.shape) == 3:
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        else:
            gray2 = img2
        
        # Resize to same dimensions
        h, w = min(gray1.shape[0], gray2.shape[0]), min(gray1.shape[1], gray2.shape[1])
        gray1 = cv2.resize(gray1, (w, h))
        gray2 = cv2.resize(gray2, (w, h))
        
        # Calculate multiple difference metrics
        ssim_score, _ = ssim(gray1, gray2, full=True)
        
        # Calculate histogram difference
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        hist_diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # Combine metrics (lower is more different)
        combined_similarity = (ssim_score * 0.7 + hist_diff * 0.3)
        return float(1 - combined_similarity)  # Return difference


class VideoProcessor:
    """Advanced video processing with intelligent frame selection"""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        self.frame_selector = AdvancedFrameSelector()
    
    def __del__(self):
        """Release video capture"""
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def extract_key_frames_advanced(self, max_frames: int = 10, 
                                   use_scene_detection: bool = True,
                                   use_motion_analysis: bool = True,
                                   use_importance_scoring: bool = True) -> List[Tuple[np.ndarray, float, Dict]]:
        """
        Advanced key frame extraction using multiple algorithms with robust error handling
        Returns list of (frame, timestamp, metadata) tuples
        """
        try:
            print(f"🎬 Starting advanced frame extraction for {max_frames} frames...")
            frames_with_metadata = []
            
            if self.frame_count == 0:
                print("⚠️ No frames available in video")
                return frames_with_metadata
            
            # Step 1: Scene detection to identify major transitions
            scene_boundaries = []
            if use_scene_detection:
                try:
                    print("🔍 Detecting scene boundaries...")
                    scene_detector = EnhancedSceneDetector()
                    scene_boundaries = scene_detector.detect_scenes_advanced(self)
                    print(f"📊 Found {len(scene_boundaries)} scene boundaries")
                except Exception as e:
                    print(f"⚠️ Scene detection failed, using uniform sampling: {str(e)}")
                    scene_boundaries = []
            
            # Step 2: Extract candidate frames
            try:
                candidate_frames = self._extract_candidate_frames(scene_boundaries, max_frames * 3)
                print(f"🎯 Extracted {len(candidate_frames)} candidate frames")
            except Exception as e:
                print(f"⚠️ Candidate frame extraction failed, falling back to basic sampling: {str(e)}")
                # Fallback to basic uniform sampling
                candidate_frames = []
                for i in range(min(max_frames * 2, self.frame_count)):
                    frame_idx = i * (self.frame_count // min(max_frames * 2, self.frame_count))
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = self.cap.read()
                    if ret:
                        timestamp = frame_idx / self.fps
                        candidate_frames.append((frame, timestamp))
            
            if not candidate_frames:
                print("❌ No candidate frames extracted")
                return frames_with_metadata
            
            # Step 3: Score frames based on importance
            if use_importance_scoring:
                try:
                    print("⚡ Calculating frame importance scores...")
                    scored_frames = self._score_frame_importance(candidate_frames)
                except Exception as e:
                    print(f"⚠️ Importance scoring failed, using default scores: {str(e)}")
                    scored_frames = [(frame, ts, {"importance_score": 0.5}) for frame, ts in candidate_frames]
            else:
                scored_frames = [(frame, ts, {"importance_score": 0.5}) for frame, ts in candidate_frames]
            
            # Step 4: Select best frames using clustering and diversity
            try:
                print("🧠 Selecting optimal frame set...")
                selected_frames = self._select_diverse_frames(scored_frames, max_frames)
            except Exception as e:
                print(f"⚠️ Diverse selection failed, using top scored frames: {str(e)}")
                # Fallback: select top scored frames
                sorted_frames = sorted(scored_frames, key=lambda x: x[2].get("importance_score", 0), reverse=True)
                selected_frames = sorted_frames[:max_frames]
            
            # Step 5: Sort by timestamp for proper sequence
            selected_frames.sort(key=lambda x: x[1])
            
            print(f"✅ Selected {len(selected_frames)} optimal frames")
            return selected_frames
            
        except Exception as e:
            print(f"❌ Advanced frame extraction failed: {str(e)}")
            print("🔄 Falling back to basic frame extraction...")
            # Ultimate fallback: basic uniform sampling
            try:
                fallback_frames = []
                for i in range(min(max_frames, self.frame_count)):
                    frame_idx = i * (self.frame_count // min(max_frames, self.frame_count))
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = self.cap.read()
                    if ret:
                        timestamp = frame_idx / self.fps
                        metadata = {"importance_score": 0.5, "method": "fallback"}
                        fallback_frames.append((frame, timestamp, metadata))
                return fallback_frames
            except:
                return []
    
    def _extract_candidate_frames(self, scene_boundaries: List[float], max_candidates: int) -> List[Tuple[np.ndarray, float]]:
        """Extract candidate frames based on scene boundaries and uniform sampling"""
        candidate_frames = []
        
        # Always include first and last frames
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, first_frame = self.cap.read()
        if ret:
            candidate_frames.append((first_frame, 0.0))
        
        # Extract frames at scene boundaries
        for boundary_time in scene_boundaries[1:]:  # Skip first boundary (0.0)
            frame_idx = int(boundary_time * self.fps)
            if frame_idx < self.frame_count:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
                if ret:
                    candidate_frames.append((frame, boundary_time))
        
        # Fill remaining candidates with uniform sampling
        if len(candidate_frames) < max_candidates:
            remaining_slots = max_candidates - len(candidate_frames)
            uniform_interval = self.frame_count // (remaining_slots + 1)
            
            for i in range(1, remaining_slots + 1):
                frame_idx = i * uniform_interval
                if frame_idx < self.frame_count:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = self.cap.read()
                    if ret:
                        timestamp = frame_idx / self.fps
                        # Check if this timestamp is not too close to existing ones
                        if not any(abs(timestamp - existing_ts) < 1.0 for _, existing_ts in candidate_frames):
                            candidate_frames.append((frame, timestamp))
        
        # Add last frame if not already included
        if len(candidate_frames) > 0 and candidate_frames[-1][1] < self.duration - 1.0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count - 1)
            ret, last_frame = self.cap.read()
            if ret:
                candidate_frames.append((last_frame, self.duration))
        
        return candidate_frames
    
    def _score_frame_importance(self, candidate_frames: List[Tuple[np.ndarray, float]]) -> List[Tuple[np.ndarray, float, Dict]]:
        """Score frames based on multiple importance factors"""
        scored_frames = []
        
        for i, (frame, timestamp) in enumerate(candidate_frames):
            # Get previous and next frames for context
            prev_frame = candidate_frames[i-1][0] if i > 0 else None
            next_frame = candidate_frames[i+1][0] if i < len(candidate_frames) - 1 else None
            
            # Calculate importance score
            importance = self.frame_selector.calculate_frame_importance(frame, prev_frame, next_frame)
            
            # Calculate additional metrics
            complexity = self.frame_selector.calculate_visual_complexity(frame)
            color_diversity = self.frame_selector.calculate_color_diversity(frame)
            
            metadata = {
                "importance_score": float(importance),
                "visual_complexity": float(complexity),
                "color_diversity": float(color_diversity),
                "timestamp": float(timestamp)
            }
            
            scored_frames.append((frame, timestamp, metadata))
        
        return scored_frames
    
    def _select_diverse_frames(self, scored_frames: List[Tuple[np.ndarray, float, Dict]], 
                              max_frames: int) -> List[Tuple[np.ndarray, float, Dict]]:
        """Select diverse frames using importance scores and visual diversity"""
        if len(scored_frames) <= max_frames:
            return scored_frames
        
        # Sort by importance score (descending)
        scored_frames.sort(key=lambda x: x[2]["importance_score"], reverse=True)
        
        selected = []
        
        # Always include the highest importance frame
        selected.append(scored_frames[0])
        
        # Select remaining frames based on diversity and importance
        for candidate in scored_frames[1:]:
            if len(selected) >= max_frames:
                break
            
            candidate_frame, candidate_ts, candidate_meta = candidate
            
            # Check diversity with already selected frames
            is_diverse = True
            for selected_frame, selected_ts, _ in selected:
                # Temporal diversity (at least 2 seconds apart)
                if abs(candidate_ts - selected_ts) < 2.0:
                    is_diverse = False
                    break
                
                # Visual diversity
                visual_diff = ImageProcessor.calculate_image_difference(candidate_frame, selected_frame)
                if visual_diff < 0.3:  # Too similar visually
                    is_diverse = False
                    break
            
            if is_diverse:
                selected.append(candidate)
        
        # If we still need more frames, fill with best remaining candidates
        if len(selected) < max_frames:
            # Use timestamps to identify selected frames (avoid numpy array comparison)
            selected_timestamps = set(ts for _, ts, _ in selected)
            remaining_candidates = [f for f in scored_frames if f[1] not in selected_timestamps]
            remaining_candidates.sort(key=lambda x: x[2]["importance_score"], reverse=True)
            
            for candidate in remaining_candidates:
                if len(selected) >= max_frames:
                    break
                selected.append(candidate)
        
        return selected
    
    def extract_key_frames(self, max_frames: int = 10, difference_threshold: float = 0.15) -> List[Tuple[np.ndarray, float]]:
        """
        Legacy method - now uses advanced extraction internally
        """
        advanced_frames = self.extract_key_frames_advanced(max_frames)
        return [(frame, timestamp) for frame, timestamp, _ in advanced_frames]
    
    def detect_motion_areas(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """Enhanced motion detection with noise reduction"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        gray1 = cv2.GaussianBlur(gray1, (5, 5), 0)
        gray2 = cv2.GaussianBlur(gray2, (5, 5), 0)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply adaptive threshold
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return thresh
    
    def get_video_info(self) -> dict:
        """Get comprehensive video information"""
        return {
            'duration': self.duration,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'codec': int(self.cap.get(cv2.CAP_PROP_FOURCC)),
            'bitrate': self.cap.get(cv2.CAP_PROP_BITRATE) if hasattr(cv2, 'CAP_PROP_BITRATE') else 'unknown'
        }


class EnhancedSceneDetector:
    """Advanced scene detection using multiple algorithms"""
    
    def detect_scenes_advanced(self, video_processor: VideoProcessor, 
                             histogram_threshold: float = 30.0,
                             optical_flow_threshold: float = 50.0) -> List[float]:
        """
        Advanced scene detection combining multiple methods with robust error handling
        """
        try:
            scene_boundaries = [0.0]  # Always start with first frame
            
            cap = video_processor.cap
            frame_count = video_processor.frame_count
            fps = video_processor.fps
            
            if frame_count < 2:
                return scene_boundaries
            
            # Sample frames more densely for better detection
            sampling_interval = max(1, int(fps * 0.25))  # Every 0.25 seconds
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, prev_frame = cap.read()
            if not ret:
                return scene_boundaries
            
            try:
                prev_hist = self._calculate_enhanced_histogram(prev_frame)
                prev_features = self._extract_visual_features(prev_frame)
            except Exception as e:
                # Fallback to basic histogram
                prev_hist = cv2.calcHist([prev_frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                prev_features = np.mean(prev_frame, axis=(0, 1))
            
            for frame_idx in range(sampling_interval, frame_count, sampling_interval):
                try:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, current_frame = cap.read()
                    
                    if not ret:
                        continue
                    
                    try:
                        current_hist = self._calculate_enhanced_histogram(current_frame)
                        current_features = self._extract_visual_features(current_frame)
                    except Exception as e:
                        # Fallback to basic histogram
                        current_hist = cv2.calcHist([current_frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                        current_features = np.mean(current_frame, axis=(0, 1))
                    
                    # Multiple scene change indicators
                    try:
                        hist_diff = cv2.compareHist(prev_hist, current_hist, cv2.HISTCMP_CHISQR)
                        feature_diff = cosine(prev_features, current_features) if len(prev_features) == len(current_features) else 0.5
                        
                        # Optical flow analysis for camera movement
                        try:
                            optical_flow_mag = self._calculate_optical_flow_magnitude(prev_frame, current_frame)
                        except Exception as e:
                            # Fallback: frame difference
                            diff = cv2.absdiff(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY), 
                                             cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY))
                            optical_flow_mag = np.mean(diff)
                        
                        # Combine indicators for scene change decision
                        scene_change_score = (
                            (hist_diff > histogram_threshold) * 0.4 +
                            (feature_diff > 0.3) * 0.4 +
                            (optical_flow_mag > optical_flow_threshold) * 0.2
                        )
                        
                        if scene_change_score > 0.5:  # Scene change detected
                            timestamp = frame_idx / fps
                            scene_boundaries.append(timestamp)
                            
                        prev_hist = current_hist
                        prev_features = current_features
                        prev_frame = current_frame
                        
                    except Exception as e:
                        # Skip this frame if analysis fails
                        continue
                        
                except Exception as e:
                    # Skip this frame if reading fails
                    continue
            
            # Always include the last frame
            if len(scene_boundaries) == 1 or scene_boundaries[-1] != (frame_count - 1) / fps:
                scene_boundaries.append((frame_count - 1) / fps)
            
            return scene_boundaries
            
        except Exception as e:
            # Ultimate fallback: uniform sampling
            try:
                frame_count = video_processor.frame_count
                fps = video_processor.fps
                # Create 5 uniform boundaries
                boundaries = [0.0]
                for i in range(1, 5):
                    boundaries.append((frame_count * i / 5) / fps)
                return boundaries
            except:
                return [0.0]
            
            # Combine indicators for scene change decision
            scene_change_score = (
                (hist_diff > histogram_threshold) * 0.4 +
                (feature_diff > 0.3) * 0.4 +
                (optical_flow_mag > optical_flow_threshold) * 0.2
            )
            
            if scene_change_score > 0.5:  # Threshold for scene change
                timestamp = frame_idx / fps
                # Avoid too frequent scene changes (minimum 2 seconds apart)
                if not scene_boundaries or timestamp - scene_boundaries[-1] > 2.0:
                    scene_boundaries.append(timestamp)
                    prev_hist = current_hist
                    prev_features = current_features
        
        return scene_boundaries
    
    def _calculate_enhanced_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Calculate enhanced histogram with multiple color spaces and error handling"""
        try:
            # Convert to multiple color spaces
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Calculate histograms
            hsv_hist = cv2.calcHist([hsv], [0, 1, 2], None, [30, 32, 32], [0, 180, 0, 256, 0, 256])
            lab_hist = cv2.calcHist([lab], [0, 1, 2], None, [32, 32, 32], [0, 256, 0, 256, 0, 256])
            
            # Normalize and combine
            cv2.normalize(hsv_hist, hsv_hist)
            cv2.normalize(lab_hist, lab_hist)
            
            combined_hist = np.concatenate([hsv_hist.ravel(), lab_hist.ravel()])
            return combined_hist
            
        except Exception as e:
            # Fallback to basic BGR histogram
            try:
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                cv2.normalize(hist, hist)
                return hist.ravel()
            except:
                # Ultimate fallback: return mean values
                return np.mean(frame, axis=(0, 1))
    
    def _extract_visual_features(self, frame: np.ndarray) -> np.ndarray:
        """Extract visual features for scene comparison with error handling"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge features
            edges = cv2.Canny(gray, 50, 150)
            edge_hist = np.histogram(edges.ravel(), bins=50)[0]
            
            # Texture features using LBP
            lbp = local_binary_pattern(gray, 8, 1, method='uniform')
            lbp_hist = np.histogram(lbp.ravel(), bins=10)[0]
            
            # Gradient features
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_mag = np.sqrt(grad_x**2 + grad_y**2)
            grad_hist = np.histogram(grad_mag.ravel(), bins=50)[0]
            
            # Combine features
            features = np.concatenate([edge_hist, lbp_hist, grad_hist])
            features = features / (np.linalg.norm(features) + 1e-7)  # Normalize
            
            return features
            
        except Exception as e:
            # Fallback to simple features
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Simple histogram of pixel intensities
                hist = np.histogram(gray.ravel(), bins=50)[0]
                return hist / (np.linalg.norm(hist) + 1e-7)
            except:
                # Ultimate fallback: mean color values
                return np.mean(frame, axis=(0, 1))
    
    def _calculate_optical_flow_magnitude(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate optical flow magnitude for camera movement detection with error handling"""
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Use Farneback optical flow (dense flow)
            flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            if flow is not None:
                # Calculate magnitude of flow vectors
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                return np.mean(magnitude)
            
            return 0.0
            
        except Exception as e:
            # Fallback: simple frame difference
            try:
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray1, gray2)
                return np.mean(diff)
            except:
                return 0.0


class SceneDetector:
    """Legacy scene detector - redirects to enhanced version"""
    
    @staticmethod
    def detect_scenes(video_processor: VideoProcessor, threshold: float = 30.0) -> List[float]:
        """Legacy method - uses enhanced detection"""
        enhanced_detector = EnhancedSceneDetector()
        return enhanced_detector.detect_scenes_advanced(video_processor, threshold)
    
    @staticmethod
    def _calculate_histogram(frame: np.ndarray) -> np.ndarray:
        """Legacy histogram calculation"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
        cv2.normalize(hist, hist)
        return hist
