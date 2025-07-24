"""
 Тесты проверяют как позитивные сценарии, так и обработку ошибок, включая:

    Отсутствие обязательных аргументов

    Некорректный тип отчета

    Отсутствие файлов

    Невалидный JSON

    Логи без нужных полей

    Пустые файлы

    Корректность расчетов среднего времени
"""

import pytest
from unittest.mock import patch, mock_open
import json
from collections import defaultdict
import argparse
from io import StringIO
import sys

from main import parse_args, read_log_files, generate_average_report, main


class TestParseArgs:
    def test_parse_valid_args(self):
        test_args = ["--file", "file1.json", "file2.json", "--report", "average"]
        with patch.object(sys, 'argv', ["script.py"] + test_args):
            args = parse_args()
            assert args.file == ["file1.json", "file2.json"]
            assert args.report == "average"

    def test_missing_required_args(self):
        with patch.object(sys, 'argv', ["script.py"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_invalid_report_type(self):
        test_args = ["--file", "file.json", "--report", "invalid"]
        with patch.object(sys, 'argv', ["script.py"] + test_args):
            with pytest.raises(SystemExit):
                parse_args()


class TestReadLogFiles:
    @pytest.fixture
    def valid_log_data(self):
        return [
            '{"url": "/api", "response_time": 0.1}\n',
            '{"url": "/home", "response_time": 0.2}\n'
        ]

    def test_read_single_file(self, valid_log_data):
        with patch("builtins.open", mock_open(read_data="".join(valid_log_data))):
            logs = read_log_files(["test.json"])
            assert len(logs) == 2
            assert logs[0]["url"] == "/api"
            assert logs[1]["response_time"] == 0.2

    def test_read_multiple_files(self, valid_log_data):
        m = mock_open(read_data="".join(valid_log_data))
        with patch("builtins.open", m):
            logs = read_log_files(["file1.json", "file2.json"])
            assert len(logs) == 4  
            assert m.call_count == 2

    def test_file_not_found(self, capsys):
        with patch("builtins.open", side_effect=FileNotFoundError("Not found")):
            logs = read_log_files(["missing.json"])
            assert len(logs) == 0
            captured = capsys.readouterr()
            assert "⚠️ File not found: missing.json" in captured.out

    def test_invalid_json(self, capsys):
        with patch("builtins.open", mock_open(read_data="invalid json")):
            logs = read_log_files(["bad.json"])
            assert len(logs) == 0
            captured = capsys.readouterr()
            assert "⚠️ Invalid JSON in file: bad.json" in captured.out


class TestGenerateAverageReport:
    @pytest.fixture
    def sample_logs(self):
        return [
            {"url": "/api", "response_time": 0.1},
            {"url": "/api", "response_time": 0.3},
            {"url": "/home", "response_time": 0.2},
            {"not_url": "value"}, 
            {"url": "/api", "response_time": None}
        ]

    def test_empty_logs(self):
        report = generate_average_report([])
        assert report == []

    def test_report_calculation(self, sample_logs):
        report = generate_average_report(sample_logs)
        assert len(report) == 2
        
        # Проверяем правильность расчета
        api_entry = next(e for e in report if e["endpoint"] == "/api")
        home_entry = next(e for e in report if e["endpoint"] == "/home")
        
        assert api_entry["request_count"] == 2
        assert api_entry["average_response_time"] == pytest.approx(0.2)
        
        assert home_entry["request_count"] == 1
        assert home_entry["average_response_time"] == 0.2

    def test_report_sorting(self, sample_logs):
        report = generate_average_report(sample_logs)
        endpoints = [e["endpoint"] for e in report]
        assert endpoints == sorted(endpoints)


class TestMain:
    @pytest.fixture
    def valid_log_data(self):
        return '{"url": "/api", "response_time": 0.1}\n'

    @pytest.fixture
    def no_url_log_data(self):
        return '{"not_url": "value"}\n'

    def test_main_success(self, valid_log_data, capsys):
        test_args = ["--file", "file.json", "--report", "average"]
        
        with patch.object(sys, 'argv', ["script.py"] + test_args), \
             patch("builtins.open", mock_open(read_data=valid_log_data)):
            main()
            
            captured = capsys.readouterr()
            assert "📊 Report: Average Response Time by Endpoint" in captured.out
            assert "/api" in captured.out
            assert "0.1" in captured.out

    def test_main_no_data(self, capsys):
        test_args = ["--file", "empty.json", "--report", "average"]
        
        with patch.object(sys, 'argv', ["script.py"] + test_args), \
             patch("builtins.open", mock_open(read_data="")):
            main()
            
            captured = capsys.readouterr()
            assert "❌ No valid log data found." in captured.out

    def test_main_no_endpoints(self, no_url_log_data, capsys):
        test_args = ["--file", "no_urls.json", "--report", "average"]
        
        with patch.object(sys, 'argv', ["script.py"] + test_args), \
             patch("builtins.open", mock_open(read_data=no_url_log_data)):
            main()
            
            captured = capsys.readouterr()
            assert "❌ No endpoints found in logs." in captured.out