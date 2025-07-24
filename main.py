"""
    argparse - для обработки аргументов командной строки

    json - для работы с JSON-логами

    defaultdict - специальный словарь с дефолтными значениями

    tabulate - для красивого вывода таблиц
"""

import argparse
import json
from collections import defaultdict
from tabulate import tabulate


def parse_args():
    """
    Функция создает парсер аргументов
    --file:
        required=True - обязательный параметр
        nargs='+' - принимает один или несколько файлов
    --report:
        choices=['average'] - пока поддерживает только один тип отчета
    """
    parser = argparse.ArgumentParser(description='Process log files and generate reports.')
    parser.add_argument('--file', required=True, nargs='+', help='Paths to log files (JSON format)')
    parser.add_argument('--report', required=True, choices=['average'], help='Type of report to generate (only "average" supported)')
    return parser.parse_args()


def read_log_files(file_paths):
    logs = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                logs.extend([json.loads(line) for line in file])
        except FileNotFoundError:
            print(f"⚠️ File not found: {file_path}")
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON in file: {file_path}")
    return logs


def generate_average_report(logs):
    endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})

    for log in logs:
        endpoint = log.get('url') 
        response_time = log.get('response_time')
        if endpoint and response_time is not None:
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += response_time

    report = []
    for endpoint, stats in endpoint_stats.items():
        avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
        report.append({
            'endpoint': endpoint,
            'request_count': stats['count'],
            'average_response_time': round(avg_time, 3)
        })

    return sorted(report, key=lambda x: x['endpoint'])


def main():
    args = parse_args()

    logs = read_log_files(args.file)
    if not logs:
        print("❌ No valid log data found.")
        return

    report = generate_average_report(logs)
    if not report:
        print("❌ No endpoints found in logs.")
        return

    # Формируем таблицу
    headers = ["Endpoint", "Request Count", "Avg Response Time (ms)"]
    table = [
        [entry['endpoint'], entry['request_count'], entry['average_response_time']]
        for entry in report
    ]

    print("\n📊 Report: Average Response Time by Endpoint")
    print(tabulate(table, headers=headers, tablefmt="grid", numalign="center"))


if __name__ == '__main__':
    main()