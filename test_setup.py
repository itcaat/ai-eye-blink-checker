"""Quick test to verify setup."""

import sys

print("Testing imports...")

try:
    import cv2
    print(f"✅ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")
    sys.exit(1)

try:
    import mediapipe as mp
    print(f"✅ MediaPipe version: {mp.__version__}")
except ImportError as e:
    print(f"❌ MediaPipe import failed: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"✅ NumPy version: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")
    sys.exit(1)

try:
    from blink_checker.detector import BlinkDetector
    print(f"✅ BlinkDetector imported successfully")
except ImportError as e:
    print(f"❌ BlinkDetector import failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful! Setup is complete.")
print("\nYou can now run the application with:")
print("  uv run blink-checker")
print("or:")
print("  uv run blink-checker --time 60")

