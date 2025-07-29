"""
Performance Reporter Service - follows SRP.

This service is responsible only for generating performance reports.
"""

import json
from pathlib import Path
from typing import List, Union
import matplotlib.pyplot as plt
import numpy as np
from .performance_monitor import PerformanceMetric


class PerformanceReporter:
    """
    Reporter for performance metrics.
    
    Single Responsibility: Generate performance reports and visualizations.
    """

    def __init__(self) -> None:
        """Initialize performance reporter"""
        pass

    def generate_html_report(
        self, 
        metrics: List[PerformanceMetric], 
        output_path: Union[str, Path]
    ) -> None:
        """Generate HTML performance report"""
        if not metrics:
            return
            
        output_path = Path(output_path)
        
        # Extract metrics for plotting
        timestamps = [m.timestamp for m in metrics]
        cpu_usage = [m.cpu_usage for m in metrics]
        memory_usage = [m.memory_usage / (1024 * 1024) for m in metrics]  # Convert to MB
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # CPU Usage plot
        ax1.plot(timestamps, cpu_usage, 'b-')
        ax1.set_title('CPU Usage Over Time')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('CPU Usage (%)')
        
        # Memory Usage plot
        ax2.plot(timestamps, memory_usage, 'r-')
        ax2.set_title('Memory Usage Over Time')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Memory Usage (MB)')
        
        plt.tight_layout()
        
        # Save plots
        plot_path = output_path.with_suffix('.png')
        plt.savefig(plot_path)
        plt.close()
        
        # Generate HTML report
        html_content = f"""
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .metrics {{ margin: 20px 0; }}
                img {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>Performance Report</h1>
            <div class="metrics">
                <h2>Summary</h2>
                <p>Duration: {timestamps[-1]:.2f} seconds</p>
                <p>Average CPU Usage: {np.mean(cpu_usage):.1f}%</p>
                <p>Average Memory Usage: {np.mean(memory_usage):.1f} MB</p>
                <p>Peak CPU Usage: {max(cpu_usage):.1f}%</p>
                <p>Peak Memory Usage: {max(memory_usage):.1f} MB</p>
            </div>
            <div class="plots">
                <h2>Performance Graphs</h2>
                <img src="{plot_path.name}" alt="Performance Graphs">
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)

    def generate_json_report(
        self, 
        metrics: List[PerformanceMetric], 
        output_path: Union[str, Path]
    ) -> None:
        """Generate JSON performance report"""
        if not metrics:
            return
            
        output_path = Path(output_path)
        
        # Convert metrics to JSON-serializable format
        metrics_data = {
            'metrics': [
                {
                    'timestamp': m.timestamp,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'response_time': m.response_time
                }
                for m in metrics
            ],
            'summary': {
                'total_metrics': len(metrics),
                'duration': metrics[-1].timestamp if metrics else 0.0,
                'avg_cpu_usage': np.mean([m.cpu_usage for m in metrics]) if metrics else 0.0,
                'avg_memory_usage': np.mean([m.memory_usage for m in metrics]) if metrics else 0.0,
                'avg_response_time': np.mean([m.response_time for m in metrics]) if metrics else 0.0,
                'peak_cpu_usage': max([m.cpu_usage for m in metrics]) if metrics else 0.0,
                'peak_memory_usage': max([m.memory_usage for m in metrics]) if metrics else 0.0,
            }
        }

        with open(output_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)

    def plot_metrics(
        self, 
        metrics: List[PerformanceMetric], 
        file_path: Union[str, Path]
    ) -> None:
        """Generate performance metrics plot"""
        if not metrics:
            return
            
        file_path = Path(file_path)
        
        timestamps = [m.timestamp for m in metrics]
        cpu_usage = [m.cpu_usage for m in metrics]
        memory_usage = [m.memory_usage for m in metrics]
        response_times = [m.response_time for m in metrics]
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        
        # Plot CPU usage
        ax1.plot(timestamps, cpu_usage, 'b-')
        ax1.set_title('CPU Usage Over Time')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.grid(True)
        
        # Plot memory usage
        ax2.plot(timestamps, memory_usage, 'g-')
        ax2.set_title('Memory Usage Over Time')
        ax2.set_ylabel('Memory Usage (bytes)')
        ax2.grid(True)
        
        # Plot response times
        ax3.plot(timestamps, response_times, 'r-')
        ax3.set_title('Response Time Over Time')
        ax3.set_ylabel('Response Time (s)')
        ax3.set_xlabel('Time (s)')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close() 