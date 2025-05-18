import json
import math
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

def analyze_results(json_file):
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Debug: print struktur data untuk melihat format aslinya
    print("JSON structure keys:", list(data.keys()))  # Konversi ke list terlebih dahulu
    
    # Extract metrics - k6 mungkin menyimpan metrics dalam format berbeda
    metrics = {}
    
    # Coba beberapa kemungkinan struktur
    if "metrics" in data:
        metrics = data["metrics"]
    elif "data" in data and "metrics" in data["data"]:
        metrics = data["data"]["metrics"]
    else:
        # Gunakan semua data jika tidak ada struktur yang diharapkan
        metrics = data
    
    if not metrics:
        print("WARNING: No metrics found in the JSON file. Using raw data.")
        metrics = data
    
    # Create output directory for reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"stress_test_report_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write raw data for inspection
    with open(os.path.join(output_dir, "raw_data.json"), "w") as f:
        json.dump(data, f, indent=2)
    
    # Create summary text
    summary = generate_summary(metrics, timestamp)
    
    # Write summary to file
    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    # Generate charts only if there's valid data
    if has_valid_data(metrics):
        try:
            generate_charts(metrics, output_dir)
        except Exception as e:
            print(f"Error generating charts: {str(e)}")
            print("Charts generation skipped. See summary.txt for results.")
    else:
        print("No valid performance data found for charts.")
    
    print(f"Analysis completed. Reports saved to {output_dir}/")
    print(f"Summary:\n{summary}")

def has_valid_data(metrics):
    # Check if there's any non-zero performance data
    try:
        req_count = get_nested_value(metrics, ['http_reqs', 'values', 'count'], 0)
        if req_count > 0:
            return True
            
        # Also check statistics_api_calls
        api_calls = get_nested_value(metrics, ['statistics_api_calls', 'values', 'count'], 0)
        if api_calls > 0:
            return True
            
        return False
    except:
        return False
        
def get_nested_value(data, keys, default=None):
    """Safely get a nested value from a dictionary"""
    result = data
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result

def generate_summary(metrics, timestamp):
    # HTTP request metrics - akses langsung tanpa 'values'
    http_reqs = metrics.get('http_reqs', {})
    request_count = http_reqs.get('count', 0)
    request_rate = http_reqs.get('rate', 0)
    
    # Duration metrics
    duration = metrics.get('http_req_duration', {})
    min_duration = duration.get('min', 0)
    max_duration = duration.get('max', 0)
    avg_duration = duration.get('avg', 0)
    p90_duration = duration.get('p(90)', 0)
    p95_duration = duration.get('p(95)', 0)
    
    # Calculate error rate
    http_req_failed = metrics.get('http_req_failed', {}).get('values', {})
    error_rate = http_req_failed.get('rate', 0) * 100  # Convert to percentage
    
    # Custom metrics
    statistics_calls = metrics.get('statistics_api_calls', {}).get('values', {}).get('count', 0)
    statistics_errors = metrics.get('statistics_api_errors', {}).get('values', {}).get('count', 0)
    statistics_latency = metrics.get('statistics_api_latency', {}).get('values', {})
    
    # Performance assessment
    performance_rating = "EXCELLENT"
    if avg_duration > 2000:
        performance_rating = "POOR"
    elif avg_duration > 1000:
        performance_rating = "FAIR"
    elif avg_duration > 500:
        performance_rating = "GOOD"
    
    # Build summary text
    summary = f"""
==================================================
API STATISTICS STRESS TEST SUMMARY - {timestamp}
==================================================

GENERAL METRICS:
* Total Requests: {request_count}
* Request Rate: {request_rate:.2f} requests/second
* Error Rate: {error_rate:.2f}%

RESPONSE TIME (milliseconds):
* Minimum: {min_duration:.2f} ms
* Average: {avg_duration:.2f} ms
* 90th Percentile: {p90_duration:.2f} ms
* 95th Percentile: {p95_duration:.2f} ms
* Maximum: {max_duration:.2f} ms

PERFORMANCE ASSESSMENT: {performance_rating}

RECOMMENDATIONS:
"""
    
    # Add recommendations based on metrics
    if error_rate > 5:
        summary += "* HIGH ERROR RATE: Investigate server errors and exceptions\n"
    if avg_duration > 1000:
        summary += "* SLOW RESPONSE TIME: Consider optimizing database queries\n"
    if p95_duration > 2000:
        summary += "* INCONSISTENT PERFORMANCE: Some requests are very slow, check for outliers\n"
    if max_duration > 5000:
        summary += "* EXTREME OUTLIERS: Some requests took over 5 seconds\n"
    
    if performance_rating == "EXCELLENT":
        summary += "* API is performing excellently under load\n"
    
    return summary

def generate_charts(metrics, output_dir):
    plt.figure(figsize=(12, 8))
    
    # 1. Response Time Distribution
    plt.subplot(2, 2, 1)
    durations = [
        metrics.get('http_req_duration', {}).get('values', {}).get('min', 0),
        metrics.get('http_req_duration', {}).get('values', {}).get('avg', 0),
        metrics.get('http_req_duration', {}).get('values', {}).get('med', 0),
        metrics.get('http_req_duration', {}).get('values', {}).get('p(90)', 0),
        metrics.get('http_req_duration', {}).get('values', {}).get('p(95)', 0),
        metrics.get('http_req_duration', {}).get('values', {}).get('max', 0)
    ]
    
    # Periksa apakah semua nilai adalah 0 atau NaN
    if all(d == 0 or math.isnan(d) for d in durations):
        plt.text(0.5, 0.5, "No valid response time data available", 
                ha='center', va='center', transform=plt.gca().transAxes)
    else:
        # Ganti NaN dengan 0
        durations = [0 if math.isnan(d) else d for d in durations]
        labels = ['Min', 'Avg', 'Median', '90th', '95th', 'Max']
        plt.bar(labels, durations)
    
    plt.title('Response Time Distribution (ms)')
    plt.ylabel('Time (ms)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 2. Request/Error Count
    plt.subplot(2, 2, 2)
    
    # Get request count and error count
    req_count = metrics.get('http_reqs', {}).get('values', {}).get('count', 0)
    error_count = req_count * metrics.get('http_req_failed', {}).get('values', {}).get('rate', 0)
    success_count = req_count - error_count
    
    plt.bar(['Successful', 'Failed'], [success_count, error_count])
    plt.title('Request Results')
    plt.ylabel('Count')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 3. HTTP Request Components
    plt.subplot(2, 2, 3)
    components = [
        metrics.get('http_req_sending', {}).get('values', {}).get('avg', 0),
        metrics.get('http_req_waiting', {}).get('values', {}).get('avg', 0),
        metrics.get('http_req_receiving', {}).get('values', {}).get('avg', 0)
    ]
    
    # Periksa apakah semua nilai components adalah 0 atau NaN
    if all(c == 0 or math.isnan(c) for c in components):
        plt.text(0.5, 0.5, "No valid component timing data available", 
                ha='center', va='center', transform=plt.gca().transAxes)
    else:
        # Ganti NaN dengan 0 dan pastikan setidaknya satu nilai > 0 
        components = [0.01 if (math.isnan(c) or c == 0) else c for c in components]
        component_labels = ['Sending', 'Waiting', 'Receiving']
        plt.pie(components, labels=component_labels, autopct='%1.1f%%')
    
    plt.title('Average Request Time Components')
    
    # 4. Custom Text Summary
    plt.subplot(2, 2, 4)
    plt.axis('off')
    
    http_reqs = metrics.get('http_reqs', {}).get('values', {})
    request_rate = http_reqs.get('rate', 0)
    avg_duration = metrics.get('http_req_duration', {}).get('values', {}).get('avg', 0)
    if math.isnan(avg_duration):
        avg_duration = 0
    error_rate = metrics.get('http_req_failed', {}).get('values', {}).get('rate', 0) * 100
    
    summary_text = f"""
KEY METRICS SUMMARY:
    
Request Rate: {request_rate:.2f} req/sec
Average Response: {avg_duration:.2f} ms
Error Rate: {error_rate:.2f}%
    
Assessment: {"NO DATA" if req_count == 0 else "PASSED" if error_rate < 5 and avg_duration < 1000 else "NEEDS IMPROVEMENT"}
"""
    plt.text(0.1, 0.5, summary_text, fontsize=10)
    
    # Save the figure
    plt.tight_layout()
    chart_file = os.path.join(output_dir, "performance_charts.png")
    plt.savefig(chart_file)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_results.py <results_json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    
    analyze_results(json_file)