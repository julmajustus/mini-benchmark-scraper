import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import defaultdict

# Function to parse log files and extract test data, system information, and kernel versions
def parse_log_files():
    test_data_nano = defaultdict(list)
    test_data_mini = defaultdict(list)
    kernel_info_nano = defaultdict(dict)
    kernel_info_mini = defaultdict(dict)
    kernel_versions_nano = defaultdict(dict)
    kernel_versions_mini = defaultdict(dict)

    nano_exists = False
    mini_exists = False

    for file in os.listdir('.'):
        if file.endswith('.log') and file.startswith('benchie_'):
            with open(file, 'r') as f:
                data_text = f.read()

            mode_match = re.search(r'Mode: (\w+)', data_text)
            if mode_match:
                mode = mode_match.group(1)
            else:
                print(f"Warning: Could not determine mode from file: {file}")
                continue

            kernel_version_match = re.search(r'Kernel: (\S+)', data_text)
            if kernel_version_match:
                kernel_version = kernel_version_match.group(1)
            else:
                print(f"Warning: Could not extract kernel version from file: {file}")
                continue

            system_info_match = re.search(r'System:(.*?)$', data_text, re.DOTALL)
            if system_info_match:
                system_info = system_info_match.group(1).strip()
            else:
                print(f"Warning: Could not extract system information from file: {file}")
                continue

            if mode == 'nano':
                nano_exists = True
                for match in re.finditer(r'(y-cruncher pi 500m|kernel defconfig|xz compression|blender render|Total time \(s\)|Total score): (\d+\.\d+)', data_text):
                    test_name = match.group(1)
                    test_time = float(match.group(2))
                    test_data_nano[(kernel_version, test_name)].append(test_time)
                    kernel_versions_nano[kernel_version].setdefault(test_name, []).append(test_time)
                    kernel_info_nano[kernel_version] = system_info
            elif mode == 'mini':
                mini_exists = True
                for match in re.finditer(r'(stress-ng cpu-cache-mem|c-ray render|perf sched msg fork thread|perf sched msg pipe proc|perf memcpy|namd 92K atoms|calculating prime numbers|argon2 hashing|ffmpeg compilation|zstd compression|x265 encoding|Total time \(s\)|Total score): (\d+\.\d+)', data_text):
                    test_name = match.group(1)
                    test_time = float(match.group(2))
                    test_data_mini[(kernel_version, test_name)].append(test_time)
                    kernel_versions_mini[kernel_version].setdefault(test_name, []).append(test_time)
                    kernel_info_mini[kernel_version] = system_info
            else:
                print(f"Warning: Unknown mode detected in file: {file}")

    if nano_exists:
        return test_data_nano, test_data_mini, kernel_info_nano, kernel_info_mini, kernel_versions_nano, kernel_versions_mini
    elif mini_exists:
        return test_data_nano, test_data_mini, kernel_info_nano, kernel_info_mini, kernel_versions_nano, kernel_versions_mini
    else:
        print("Error: No logs found for any mode.")
        return None, None, None, None, None, None

# Function to aggregate test results
def aggregate_test_results(data):
    aggregated_data = {}
    for key, values in data.items():
        aggregated_data[key] = np.mean(values)
    return aggregated_data

# Function to plot horizontal bar chart with annotations
def plot_horizontal_bar_chart_with_annotations(average_times, mode, kernel_versions):
    test_names = list(average_times[0].keys())
    test_names.reverse()
    num_kernel_versions = len(average_times)
    
    fig, axes = plt.subplots(num_kernel_versions, 1, figsize=(12, num_kernel_versions * 4))
    
    for i, avg_times in enumerate(average_times):
        kernel_version = kernel_versions[i]
        ax = axes[i] if num_kernel_versions > 1 else axes
        values = list(avg_times.values())[::-1]
        ax.barh(test_names, values, color='skyblue')
        for j, value in enumerate(values):
            ax.text(value, j, f'{value:.2f}', ha='left', va='center')
        ax.set_xlabel('Average Time (s), Less is better')
        ax.set_ylabel('Mini-Benchmarker')
        ax.set_title(f'Test Performance - Kernel Version: {kernel_version} ({mode} mode)')
        ax.grid(axis='x')
    
    plt.tight_layout()
    plt.savefig(f'average_performance_comparison_horizontal_{mode}.png')
    plt.close()

# Define a color palette
colors = list(mcolors.TABLEAU_COLORS.keys())

# Function to plot performance comparison between different kernel versions
def plot_kernel_version_comparison(average_times, mode, kernel_versions):
    test_names = list(average_times[0].keys())
    test_names.reverse()
    num_tests = len(test_names)
    num_kernel_versions = len(kernel_versions)

    # Calculate the figsize based on the number of tests and kernel versions
    fig_width = 12  # base width
    fig_height = num_tests + num_kernel_versions  # base height
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Calculate the width of each bar based on the number of kernel versions
    bar_width = 0.9 / num_kernel_versions  # Adjust this value as needed

    # Calculate font size based on num_kernel_versions
    font_size = 16 - num_kernel_versions * 0.24

    for i, avg_times in enumerate(average_times):
        kernel_version = kernel_versions[i]
        values = list(avg_times.values())[::-1]
        color = colors[i % len(colors)]  # Use modulo to loop through the color palette
        ax.barh(np.arange(num_tests) + i * bar_width, values, height=bar_width, label=kernel_version, color=color)
        for j, value in enumerate(values):
            ax.text(value, j + i * bar_width, f'{value:.2f}', fontsize=font_size, ha='left', va='center', color='black')

    ax.set_yticks(np.arange(num_tests))
    ax.set_yticklabels(test_names)
    ax.set_xlabel('Average Time (s). Less is better')
    ax.set_ylabel('Mini-Benchmarker')
    ax.set_title(f'Test Performance Comparison Between Different Kernel Versions ({mode} mode)')
    ax.legend(loc='lower right')
    ax.grid(axis='x')
    
    plt.tight_layout()
    plt.savefig(f'kernel_version_comparison_{mode}.png')
    plt.close()

# Extract test data, system information, and kernel versions from .log files
test_data_nano, test_data_mini, kernel_info_nano, kernel_info_mini, kernel_versions_nano, kernel_versions_mini = parse_log_files()

# Check if logs were found for any mode
if test_data_nano or test_data_mini:
    # Get sorted kernel versions
    sorted_kernel_versions_nano = sorted(kernel_versions_nano.keys())
    sorted_kernel_versions_mini = sorted(kernel_versions_mini.keys())

    # Get kernel versions list for nano and mini modes
    kernel_versions_nano_list = [kernel_version for kernel_version in sorted_kernel_versions_nano]
    kernel_versions_mini_list = [kernel_version for kernel_version in sorted_kernel_versions_mini]

    # Calculate average test times for each kernel version for nano mode
    if test_data_nano:
        average_times_nano = [aggregate_test_results(kernel_versions_nano[kernel_version]) for kernel_version in sorted_kernel_versions_nano]
        # Plot horizontal bar chart with annotations for nano mode
        plot_horizontal_bar_chart_with_annotations(average_times_nano, 'Nano', kernel_versions_nano_list)
        # Plot performance comparison between different kernel versions for nano mode
        plot_kernel_version_comparison(average_times_nano, 'Nano', kernel_versions_nano_list)

    # Calculate average test times for each kernel version for mini mode
    if test_data_mini:
        average_times_mini = [aggregate_test_results(kernel_versions_mini[kernel_version]) for kernel_version in sorted_kernel_versions_mini]
        # Plot horizontal bar chart with annotations for mini mode
        plot_horizontal_bar_chart_with_annotations(average_times_mini, 'Mini', kernel_versions_mini_list)
        # Plot performance comparison between different kernel versions for mini mode
        plot_kernel_version_comparison(average_times_mini, 'Mini', kernel_versions_mini_list)

    # Generate HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Performance</title>
    </head>
    <body>
        <h1>Test Performance</h1>
    """

    # Include charts for comparison of different kernel version performance based on average calculations for both modes
    if test_data_nano:
        html_content += f"""
        <h2>Average Test Performance Comparison</h2>
        <h3>Nano Mode</h3>
        <img src="average_performance_comparison_horizontal_Nano.png" alt="Average Test Performance Comparison - Nano Mode" style="max-width: 100%; height: auto;">
        """
    if test_data_mini:
        html_content += f"""
        <h3>Mini Mode</h3>
        <img src="average_performance_comparison_horizontal_Mini.png" alt="Average Test Performance Comparison - Mini Mode" style="max-width: 100%; height: auto;">
        """

    # Include charts for comparison of performance between different kernel versions for both modes
    if test_data_nano:
        html_content += f"""
        <h2>Performance Comparison Between Different Kernel Versions</h2>
        <h3>Nano Mode</h3>
        <img src="kernel_version_comparison_Nano.png" alt="Performance Comparison Between Different Kernel Versions - Nano Mode" style="max-width: 100%; height: auto;">
        """
    if test_data_mini:
        html_content += f"""
        <h3>Mini Mode</h3>
        <img src="kernel_version_comparison_Mini.png" alt="Performance Comparison Between Different Kernel Versions - Mini Mode" style="max-width: 100%; height: auto;">
        """

    html_content += """
    </body>
    </html>
    """

    # Write HTML content to a file
    with open('test_performance.html', 'w') as html_file:
        html_file.write(html_content)

    print("HTML page generated successfully!")
else:
    print("No logs found for any mode. HTML page not generated.")
