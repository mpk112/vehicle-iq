"""Photo quality gate validation functions."""

import cv2
import numpy as np
from typing import Dict, Tuple
from PIL import Image
import io


class QualityCheckResult:
    """Result of a quality check."""
    
    def __init__(self, passed: bool, score: float, message: str):
        self.passed = passed
        self.score = score
        self.message = message
    
    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "score": self.score,
            "message": self.message
        }


class PhotoQualityGate:
    """Photo quality gate validation."""
    
    # Thresholds
    BLUR_THRESHOLD = 100.0  # Laplacian variance threshold
    MIN_BRIGHTNESS = 50  # Minimum mean brightness
    MAX_BRIGHTNESS = 200  # Maximum mean brightness
    MIN_WIDTH = 1024
    MIN_HEIGHT = 768
    
    @staticmethod
    def check_blur(image_bytes: bytes) -> QualityCheckResult:
        """
        Check if image is blurry using Laplacian variance.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            QualityCheckResult with blur score
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return QualityCheckResult(False, 0.0, "Failed to decode image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        passed = laplacian_var >= PhotoQualityGate.BLUR_THRESHOLD
        message = "Image is sharp" if passed else f"Image is blurry (score: {laplacian_var:.1f}, threshold: {PhotoQualityGate.BLUR_THRESHOLD})"
        
        return QualityCheckResult(passed, float(laplacian_var), message)
    
    @staticmethod
    def check_lighting(image_bytes: bytes) -> QualityCheckResult:
        """
        Check if image has adequate lighting.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            QualityCheckResult with lighting score
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return QualityCheckResult(False, 0.0, "Failed to decode image")
        
        # Convert to grayscale and calculate mean brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))
        
        if mean_brightness < PhotoQualityGate.MIN_BRIGHTNESS:
            return QualityCheckResult(
                False,
                mean_brightness,
                f"Image is too dark (brightness: {mean_brightness:.1f}, minimum: {PhotoQualityGate.MIN_BRIGHTNESS})"
            )
        elif mean_brightness > PhotoQualityGate.MAX_BRIGHTNESS:
            return QualityCheckResult(
                False,
                mean_brightness,
                f"Image is too bright (brightness: {mean_brightness:.1f}, maximum: {PhotoQualityGate.MAX_BRIGHTNESS})"
            )
        else:
            return QualityCheckResult(
                True,
                mean_brightness,
                f"Lighting is adequate (brightness: {mean_brightness:.1f})"
            )
    
    @staticmethod
    def check_resolution(image_bytes: bytes) -> QualityCheckResult:
        """
        Check if image meets minimum resolution requirements.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            QualityCheckResult with resolution info
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            
            passed = width >= PhotoQualityGate.MIN_WIDTH and height >= PhotoQualityGate.MIN_HEIGHT
            
            if passed:
                message = f"Resolution is adequate ({width}x{height})"
            else:
                message = f"Resolution too low ({width}x{height}, minimum: {PhotoQualityGate.MIN_WIDTH}x{PhotoQualityGate.MIN_HEIGHT})"
            
            # Score is the percentage of minimum resolution met
            score = min(100.0, (width * height) / (PhotoQualityGate.MIN_WIDTH * PhotoQualityGate.MIN_HEIGHT) * 100)
            
            return QualityCheckResult(passed, score, message)
        except Exception as e:
            return QualityCheckResult(False, 0.0, f"Failed to check resolution: {str(e)}")
    
    @staticmethod
    def check_framing(image_bytes: bytes) -> QualityCheckResult:
        """
        Check if image has proper framing (basic check using edge detection).
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            QualityCheckResult with framing score
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return QualityCheckResult(False, 0.0, "Failed to decode image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate edge density in center region (vehicle should be centered)
        h, w = edges.shape
        center_region = edges[h//4:3*h//4, w//4:3*w//4]
        edge_density = np.sum(center_region > 0) / center_region.size
        
        # Good framing should have significant edges in center (vehicle present)
        # but not too many (not too cluttered)
        passed = 0.05 <= edge_density <= 0.40
        score = edge_density * 100
        
        if passed:
            message = f"Framing is adequate (edge density: {edge_density:.2%})"
        elif edge_density < 0.05:
            message = f"Vehicle may not be in frame (edge density: {edge_density:.2%})"
        else:
            message = f"Image may be too cluttered (edge density: {edge_density:.2%})"
        
        return QualityCheckResult(passed, score, message)
    
    @staticmethod
    def validate_photo(image_bytes: bytes) -> Dict:
        """
        Run all quality checks on a photo.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dict with all check results and overall pass/fail
        """
        blur_result = PhotoQualityGate.check_blur(image_bytes)
        lighting_result = PhotoQualityGate.check_lighting(image_bytes)
        resolution_result = PhotoQualityGate.check_resolution(image_bytes)
        framing_result = PhotoQualityGate.check_framing(image_bytes)
        
        all_passed = all([
            blur_result.passed,
            lighting_result.passed,
            resolution_result.passed,
            framing_result.passed
        ])
        
        # Calculate overall quality score (average of all scores, normalized to 0-100)
        scores = [blur_result.score, lighting_result.score, resolution_result.score, framing_result.score]
        # Normalize blur score to 0-100 range
        normalized_blur = min(100.0, (blur_result.score / PhotoQualityGate.BLUR_THRESHOLD) * 100)
        # Normalize lighting score to 0-100 range (optimal is middle of range)
        optimal_brightness = (PhotoQualityGate.MIN_BRIGHTNESS + PhotoQualityGate.MAX_BRIGHTNESS) / 2
        normalized_lighting = 100 - abs(lighting_result.score - optimal_brightness) / optimal_brightness * 100
        normalized_lighting = max(0, min(100, normalized_lighting))
        
        overall_score = (normalized_blur + normalized_lighting + resolution_result.score + framing_result.score) / 4
        
        return {
            "passed": all_passed,
            "overall_score": round(overall_score, 2),
            "checks": {
                "blur": blur_result.to_dict(),
                "lighting": lighting_result.to_dict(),
                "resolution": resolution_result.to_dict(),
                "framing": framing_result.to_dict()
            },
            "feedback": [
                result.message for result in [blur_result, lighting_result, resolution_result, framing_result]
                if not result.passed
            ]
        }
