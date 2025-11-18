"""Real-time blink rate plotting with time grouping."""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
from collections import deque
import time
import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta


class BlinkPlotter:
    """Real-time plotter for blink statistics."""
    
    def __init__(self, group_by_minutes: int = 1, max_points: int = 60):
        """
        Initialize the blink plotter.
        
        Args:
            group_by_minutes: Group blinks by N minutes (1 or 5)
            max_points: Maximum number of points to display
        """
        self.group_by_minutes = group_by_minutes
        self.max_points = max_points
        self.blink_timestamps = deque()
        self.start_time = time.time()
        
        # Setup plot
        plt.ion()  # Interactive mode
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('Blink Statistics')
        
        # Initialize data
        self.time_points = deque(maxlen=max_points)
        self.blink_counts = deque(maxlen=max_points)
        self.cumulative_blinks = deque(maxlen=max_points)
        
        # Lines
        self.line1, = self.ax1.plot([], [], 'b-o', linewidth=2, markersize=6, label='Blinks per interval')
        self.line2, = self.ax2.plot([], [], 'g-', linewidth=2, label='Cumulative blinks')
        
        self._setup_axes()
        
    def _setup_axes(self):
        """Setup plot axes."""
        # Top plot - blinks per interval
        self.ax1.set_xlabel(f'Time (intervals of {self.group_by_minutes} min)')
        self.ax1.set_ylabel('Blinks per interval')
        self.ax1.set_title('Blink Rate Over Time')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()
        
        # Bottom plot - cumulative
        self.ax2.set_xlabel(f'Time (intervals of {self.group_by_minutes} min)')
        self.ax2.set_ylabel('Total blinks')
        self.ax2.set_title('Cumulative Blinks')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()
        
        self.fig.tight_layout()
        
    def add_blink(self):
        """Record a new blink."""
        self.blink_timestamps.append(time.time())
        
    def update(self):
        """Update the plot with current data."""
        current_time = time.time()
        elapsed_minutes = (current_time - self.start_time) / 60
        
        # Calculate time intervals
        interval_seconds = self.group_by_minutes * 60
        num_intervals = int(elapsed_minutes / self.group_by_minutes) + 1
        
        # Group blinks by intervals
        interval_counts = [0] * min(num_intervals, self.max_points)
        
        for timestamp in self.blink_timestamps:
            interval_idx = int((timestamp - self.start_time) / interval_seconds)
            if 0 <= interval_idx < len(interval_counts):
                interval_counts[interval_idx] += 1
        
        # Update data
        self.time_points = deque(range(len(interval_counts)), maxlen=self.max_points)
        self.blink_counts = deque(interval_counts, maxlen=self.max_points)
        
        # Calculate cumulative
        cumulative = []
        total = 0
        for count in self.blink_counts:
            total += count
            cumulative.append(total)
        self.cumulative_blinks = deque(cumulative, maxlen=self.max_points)
        
        # Update plots
        if len(self.time_points) > 0:
            x_data = list(self.time_points)
            
            # Top plot - blinks per interval
            self.line1.set_data(x_data, list(self.blink_counts))
            self.ax1.relim()
            self.ax1.autoscale_view()
            
            # Add horizontal line for normal rate
            if self.group_by_minutes == 1:
                normal_rate = 15 / 60 * self.group_by_minutes * 60  # ~0.25 per second * interval
            else:
                normal_rate = 15 / 60 * self.group_by_minutes * 60
            
            # Remove old reference line if exists
            for line in self.ax1.lines[1:]:
                line.remove()
            self.ax1.axhline(y=normal_rate, color='r', linestyle='--', 
                           alpha=0.5, label=f'Normal rate (~{normal_rate:.0f}/interval)')
            self.ax1.legend()
            
            # Bottom plot - cumulative
            self.line2.set_data(x_data, list(self.cumulative_blinks))
            self.ax2.relim()
            self.ax2.autoscale_view()
            
            # Update statistics text
            if len(self.blink_timestamps) > 0:
                total_blinks = len(self.blink_timestamps)
                elapsed_time = current_time - self.start_time
                blinks_per_minute = (total_blinks / elapsed_time) * 60 if elapsed_time > 0 else 0
                
                stats_text = f'Total: {total_blinks} blinks | Rate: {blinks_per_minute:.1f}/min | Time: {elapsed_time/60:.1f} min'
                self.fig.suptitle(stats_text, fontsize=12, fontweight='bold')
        
        # Redraw
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
    def show(self):
        """Show the plot window."""
        plt.show(block=False)
        
    def close(self):
        """Close the plot window."""
        plt.close(self.fig)
        
    def save(self, filename: str):
        """Save the current plot to a file."""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"📊 График сохранен: {filename}")


class MinimalBlinkPlotter:
    """Lightweight plotter with minimal overhead."""
    
    def __init__(self, group_by_minutes: int = 1):
        """
        Initialize minimal plotter.
        
        Args:
            group_by_minutes: Group blinks by N minutes
        """
        self.group_by_minutes = group_by_minutes
        self.blink_timestamps = []
        self.start_time = time.time()
        
        # Setup simple plot
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.canvas.manager.set_window_title(f'Blink Rate (grouped by {group_by_minutes} min)')
        
        self.bars = None
        self.ax.set_xlabel(f'Time interval ({group_by_minutes} min)')
        self.ax.set_ylabel('Blinks per interval')
        self.ax.set_title('Blink Rate Over Time')
        self.ax.grid(True, alpha=0.3, axis='y')
        
    def add_blink(self):
        """Record a blink."""
        self.blink_timestamps.append(time.time())
        
    def update(self):
        """Update the plot."""
        if not self.blink_timestamps:
            return
            
        current_time = time.time()
        elapsed_minutes = (current_time - self.start_time) / 60
        
        # Calculate intervals
        interval_seconds = self.group_by_minutes * 60
        num_intervals = int(elapsed_minutes / self.group_by_minutes) + 1
        
        # Count blinks per interval
        counts = [0] * num_intervals
        for timestamp in self.blink_timestamps:
            interval_idx = int((timestamp - self.start_time) / interval_seconds)
            if 0 <= interval_idx < len(counts):
                counts[interval_idx] += 1
        
        # Clear and redraw
        self.ax.clear()
        
        x = range(len(counts))
        colors = ['green' if c >= 10 else 'orange' if c >= 5 else 'red' for c in counts]
        
        self.bars = self.ax.bar(x, counts, color=colors, alpha=0.7, edgecolor='black')
        
        # Reference line
        normal_rate = 15  # per minute
        expected_per_interval = normal_rate * self.group_by_minutes
        self.ax.axhline(y=expected_per_interval, color='blue', linestyle='--', 
                       alpha=0.5, label=f'Normal (~{expected_per_interval:.0f}/interval)')
        
        self.ax.set_xlabel(f'Time interval ({self.group_by_minutes} min)')
        self.ax.set_ylabel('Blinks per interval')
        self.ax.set_title('Blink Rate Over Time')
        self.ax.grid(True, alpha=0.3, axis='y')
        self.ax.legend()
        
        # Add statistics
        total = len(self.blink_timestamps)
        elapsed = current_time - self.start_time
        rate = (total / elapsed) * 60 if elapsed > 0 else 0
        self.ax.text(0.02, 0.98, f'Total: {total} | Rate: {rate:.1f}/min | Time: {elapsed/60:.1f} min',
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
    def show(self):
        """Show plot."""
        plt.show(block=False)
        
    def close(self):
        """Close plot."""
        plt.close(self.fig)
        
    def save(self, filename: str):
        """Save plot."""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"📊 График сохранен: {filename}")

