"""Main application entry point for eye blink checker."""

import argparse
import cv2
import sys
import time
import os
import platform
from blink_checker.detector import BlinkDetector
from blink_checker.plotter import MinimalBlinkPlotter


def play_alarm_sound():
    """Play alarm sound (supports custom audio files)."""
    # Search for custom alarm files in project directory
    possible_files = [
        'alarm.wav', 'alarm.mp3', 'alarm.ogg',
        'sound/alarm.wav', 'sound/alarm.mp3',
        'sounds/alarm.wav', 'sounds/alarm.mp3'
    ]
    
    alarm_file = None
    for filename in possible_files:
        if os.path.exists(filename):
            alarm_file = filename
            break
    
    # Try to play custom sound file
    if alarm_file:
        try:
            # Try pygame (best option)
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(alarm_file)
            sound.play()
            return
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ pygame error: {e}")
        
        # Try platform-specific players
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                os.system(f'afplay "{alarm_file}" &')
                return
            elif system == "Linux":
                os.system(f'aplay "{alarm_file}" 2>/dev/null &')
                return
            elif system == "Windows":
                os.system(f'start /min wmplayer "{alarm_file}"')
                return
        except Exception:
            pass
    
    # Fallback to system sounds if no custom file
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            os.system('afplay /System/Library/Sounds/Glass.aiff &')
        elif system == "Linux":
            os.system('paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null &')
        elif system == "Windows":
            import winsound
            winsound.Beep(1000, 500)
        else:
            print('\a' * 3)
    except Exception:
        # Last resort: terminal beep
        print('\a' * 3)


def main():
    """Run the eye blink detection application."""
    parser = argparse.ArgumentParser(
        description="Detect eye blinks using camera feed"
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=0,
        help="Duration to monitor blinks in seconds (default: 0 = infinite, press 'q' to quit)"
    )
    parser.add_argument(
        "-c",
        "--camera",
        type=int,
        default=0,
        help="Camera device index (default: 0)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Run without displaying video feed (headless mode)"
    )
    parser.add_argument(
        "--alarm",
        type=int,
        default=0,
        metavar="SECONDS",
        help="Enable alarm if no blink detected for N seconds (default: 0 = disabled)"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Show real-time blink rate plot in separate window"
    )
    parser.add_argument(
        "--plot-interval",
        type=int,
        default=1,
        choices=[1, 5],
        metavar="MINUTES",
        help="Plot grouping interval in minutes: 1 or 5 (default: 1)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("👁️  Eye Blink Detection Application")
    print("=" * 60)
    if args.time > 0:
        print(f"Monitoring duration: {args.time} seconds")
    else:
        print("Monitoring duration: ∞ (infinite mode)")
    print(f"Camera index: {args.camera}")
    if args.alarm > 0:
        print(f"⏰ Alarm enabled: {args.alarm}s without blink")
    else:
        print("⏰ Alarm: disabled")
    if args.plot:
        print(f"📊 Plot enabled: grouping by {args.plot_interval} min")
    else:
        print("📊 Plot: disabled")
    print("\nInstructions:")
    print("  - Look at the camera")
    print("  - Blink naturally")
    print("  - Press 'q' or ESC to quit")
    print("=" * 60)
    print()
    
    # Initialize camera
    cap = cv2.VideoCapture(args.camera)
    
    if not cap.isOpened():
        print(f"❌ Error: Could not open camera {args.camera}")
        sys.exit(1)
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Camera initialized successfully")
    print("⏳ Starting detection in 3 seconds...\n")
    time.sleep(3)
    
    # Initialize blink detector
    detector = BlinkDetector(alarm_threshold=args.alarm)
    
    # Initialize plotter if requested
    plotter = None
    if args.plot:
        try:
            plotter = MinimalBlinkPlotter(group_by_minutes=args.plot_interval)
            plotter.show()
            print("📊 Plot window opened")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize plot: {e}")
            print("   Continuing without plot...")
            plotter = None
    
    start_time = time.time()
    end_time = start_time + args.time if args.time > 0 else None
    frame_count = 0
    infinite_mode = args.time <= 0
    last_plot_update = time.time()
    
    if infinite_mode:
        print("🟢 Detection started! (infinite mode - press 'q' or ESC to stop)")
    else:
        print("🟢 Detection started!")
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Error: Failed to capture frame")
                break
            
            frame_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Check if time is up (only in timed mode)
            if not infinite_mode and current_time >= end_time:
                break
            
            # Detect blinks
            blink_detected, ear, annotated_frame = detector.detect_blink(frame)
            
            if blink_detected:
                print(f"👁️ Blink detected! Total blinks: {detector.get_blink_count()}")
                # Update plotter
                if plotter:
                    plotter.add_blink()
            
            # Check alarm
            if detector.should_alarm():
                print(f"\n🚨 ALARM! No blink detected for {args.alarm} seconds! Please blink! 🚨")
                # Play alarm sound
                play_alarm_sound()
            
            # Add timer to frame
            if infinite_mode:
                timer_text = f"Time elapsed: {elapsed_time:.1f}s"
            else:
                remaining_time = max(0, args.time - elapsed_time)
                timer_text = f"Time remaining: {remaining_time:.1f}s"
            
            cv2.putText(
                annotated_frame,
                timer_text,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )
            
            # Add time since last blink (if alarm enabled)
            if args.alarm > 0:
                time_since_blink = detector.get_time_since_last_blink()
                color = (0, 255, 0) if time_since_blink < args.alarm else (0, 0, 255)
                cv2.putText(
                    annotated_frame,
                    f"Since last blink: {time_since_blink:.1f}s",
                    (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )
            
            # Update plot periodically (every 2 seconds to reduce overhead)
            if plotter and (time.time() - last_plot_update) >= 2.0:
                try:
                    plotter.update()
                    last_plot_update = time.time()
                except Exception as e:
                    print(f"⚠️ Plot update error: {e}")
            
            # Display frame
            if not args.no_display:
                cv2.imshow("Eye Blink Detection", annotated_frame)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("\n⚠️ Quit requested by user")
                    break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        # Final plot update
        if plotter:
            try:
                plotter.update()
                # Optionally save plot
                if blink_count > 0:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"blink_plot_{timestamp}.png"
                    plotter.save(filename)
            except Exception as e:
                print(f"⚠️ Error saving plot: {e}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        if plotter:
            plotter.close()
        
        # Calculate statistics
        total_time = time.time() - start_time
        blink_count = detector.get_blink_count()
        fps = frame_count / total_time if total_time > 0 else 0
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 Detection Results")
        print("=" * 60)
        print(f"Total duration:     {total_time:.2f} seconds")
        print(f"Total blinks:       {blink_count}")
        print(f"Frames processed:   {frame_count}")
        print(f"Average FPS:        {fps:.2f}")
        
        if total_time > 0:
            blinks_per_minute = (blink_count / total_time) * 60
            print(f"Blinks per minute:  {blinks_per_minute:.2f}")
            
            # Normal blink rate is 15-20 per minute
            if blinks_per_minute < 10:
                status = "⚠️ Low (may indicate fatigue or concentration)"
            elif 10 <= blinks_per_minute <= 25:
                status = "✅ Normal"
            else:
                status = "⚠️ High (may indicate stress or eye irritation)"
            
            print(f"Blink rate status:  {status}")
        
        print("=" * 60)
        
        # Exit with appropriate code
        if blink_count == 0:
            print("\n⚠️ Warning: No blinks detected. Please ensure:")
            print("   - Your face is visible to the camera")
            print("   - Lighting is adequate")
            print("   - You are blinking naturally")
            sys.exit(1)
        else:
            print("\n✅ Detection completed successfully!")
            sys.exit(0)


if __name__ == "__main__":
    main()

