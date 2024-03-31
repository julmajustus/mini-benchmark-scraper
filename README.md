# Mini Benchmark Scraper

Mini Benchmark Scraper is a Python script designed to extract and parse data from Mini Benchmarker log files, providing users with insights into system performance through benchmark analysis.


## Features

- **Data Extraction:** Extracts relevant data from Mini Benchmarker log files.
- **Parsing:** Parses the extracted data for analysis and visualization.
- **Insights:** Provides insights into system performance based on benchmark results.
- **Multi-File Processing:** Processes multiple log files and calculates the average of the results between modes run on each kernel version.

## Requirements

- Python 3.x
- Dependencies:
  - `numpy`
  - `matplotlib`

## Usage

1. Place your Mini Benchmarker log files in the same directory as `benchmark_scraper.py`.
2. Run the script:

   ```bash
   python benchmark_scraper.py```

3. Once the script has completed execution, open the generated HTML page (test_performance.html) in your web browser to view the results.

## Mini Benchmarker Repository

The Mini Benchmarker script used to generate the log files can be found at https://gitlab.com/torvic9/mini-benchmarker.
