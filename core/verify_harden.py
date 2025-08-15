#!/usr/bin/env python3
"""
Verify & Harden script for Jarvis Core.
Runs comprehensive tests to ensure hybrid-readiness.
"""
import asyncio
import json
import time
import sys
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List


class VerifyHarden:
    """Verify and harden Jarvis Core."""
    
    def __init__(self, core_url: str = "http://127.0.0.1:8000"):
        self.core_url = core_url
        self.results: List[Dict[str, Any]] = []
        self.api_key = None
        
    def log_result(self, test_name: str, status: str, details: str = "", metadata: Dict[str, Any] = None) -> None:
        """Log test result."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.results.append(result)
        
        status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")
        print(f"{status_emoji} {test_name}: {status} - {details}")
    
    def test_api_contract(self) -> bool:
        """Test API contract and OpenAPI generation."""
        try:
            # Test OpenAPI endpoint
            response = requests.get(f"{self.core_url}/openapi.json", timeout=10)
            if response.status_code != 200:
                self.log_result("API Contract", "FAIL", f"OpenAPI endpoint returned {response.status_code}")
                return False
            
            openapi_data = response.json()
            
            # Validate OpenAPI structure
            required_fields = ["openapi", "info", "paths"]
            for field in required_fields:
                if field not in openapi_data:
                    self.log_result("API Contract", "FAIL", f"Missing OpenAPI field: {field}")
                    return False
            
            # Check API info
            info = openapi_data.get("info", {})
            if info.get("title") != "Jarvis Core API":
                self.log_result("API Contract", "WARN", f"Unexpected API title: {info.get('title')}")
            
            self.log_result("API Contract", "PASS", "OpenAPI endpoint working", {"paths_count": len(openapi_data.get("paths", {}))})
            return True
            
        except Exception as e:
            self.log_result("API Contract", "FAIL", f"Error testing API contract: {e}")
            return False
    
    def test_cors_trustedhost(self) -> bool:
        """Test CORS and TrustedHost configuration."""
        try:
            # Test CORS headers
            response = requests.get(f"{self.core_url}/health/live", timeout=10)
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            
            if not cors_headers:
                self.log_result("CORS/TrustedHost", "WARN", "No CORS headers found")
            elif "localhost:3000" not in cors_headers:
                self.log_result("CORS/TrustedHost", "WARN", f"UI origin not in CORS: {cors_headers}")
            else:
                self.log_result("CORS/TrustedHost", "PASS", "CORS properly configured")
            
            return True
            
        except Exception as e:
            self.log_result("CORS/TrustedHost", "FAIL", f"Error testing CORS: {e}")
            return False
    
    def test_api_key_auth(self) -> bool:
        """Test API key authentication."""
        try:
            # Test without API key (should be 401)
            response = requests.post(f"{self.core_url}/selftest/run", 
                                  json={"test_name": "auth_test"}, 
                                  timeout=10)
            
            if response.status_code != 401:
                self.log_result("API Key Auth", "FAIL", f"Expected 401, got {response.status_code}")
                return False
            
            # Test with invalid API key (should be 403)
            response = requests.post(f"{self.core_url}/selftest/run", 
                                  json={"test_name": "auth_test"},
                                  headers={"X-API-Key": "invalid-key"},
                                  timeout=10)
            
            if response.status_code != 403:
                self.log_result("API Key Auth", "FAIL", f"Expected 403, got {response.status_code}")
                return False
            
            # Test with valid API key (should be 200)
            # Note: This requires a valid API key in environment
            api_key = self.get_api_key()
            if api_key:
                response = requests.post(f"{self.core_url}/selftest/run", 
                                      json={"test_name": "auth_test"},
                                      headers={"X-API-Key": api_key},
                                      timeout=10)
                
                if response.status_code == 200:
                    self.log_result("API Key Auth", "PASS", "API key authentication working")
                    return True
                else:
                    self.log_result("API Key Auth", "FAIL", f"Valid API key returned {response.status_code}")
                    return False
            else:
                self.log_result("API Key Auth", "WARN", "No API key found for positive test")
                return True
            
        except Exception as e:
            self.log_result("API Key Auth", "FAIL", f"Error testing API key auth: {e}")
            return False
    
    def get_api_key(self) -> str:
        """Get API key from environment or settings."""
        # Try to read from .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("API_KEY="):
                        return line.split("=", 1)[1].strip()
        
        # Try environment variable
        import os
        return os.getenv("API_KEY")
    
    def test_observability(self) -> bool:
        """Test observability features."""
        try:
            # Test metrics endpoint
            response = requests.get(f"{self.core_url}/metrics", timeout=10)
            if response.status_code != 200:
                self.log_result("Observability", "FAIL", f"Metrics endpoint returned {response.status_code}")
                return False
            
            metrics = response.json()
            
            # Check for required metrics
            required_sections = ["router", "e2e", "errors", "system"]
            for section in required_sections:
                if section not in metrics:
                    self.log_result("Observability", "FAIL", f"Missing metrics section: {section}")
                    return False
            
            # Test logs endpoint
            response = requests.get(f"{self.core_url}/logs/stats", timeout=10)
            if response.status_code != 200:
                self.log_result("Observability", "FAIL", f"Logs stats returned {response.status_code}")
                return False
            
            logs_stats = response.json()
            if "total_entries" not in logs_stats:
                self.log_result("Observability", "FAIL", "Logs stats missing total_entries")
                return False
            
            self.log_result("Observability", "PASS", "Observability endpoints working", {
                "metrics_sections": len(required_sections),
                "logs_entries": logs_stats.get("total_entries", 0)
            })
            return True
            
        except Exception as e:
            self.log_result("Observability", "FAIL", f"Error testing observability: {e}")
            return False
    
    def test_sla_validation(self) -> bool:
        """Test SLA validation in metrics."""
        try:
            response = requests.get(f"{self.core_url}/metrics", timeout=10)
            if response.status_code != 200:
                self.log_result("SLA Validation", "FAIL", f"Metrics endpoint returned {response.status_code}")
                return False
            
            metrics = response.json()
            router_metrics = metrics.get("router", {})
            
            # Check p95 latency
            p95 = router_metrics.get("p95")
            if p95 is not None:
                if p95 > 1.0:  # SLA: p95 < 1.0s
                    self.log_result("SLA Validation", "WARN", f"Router p95 {p95}s exceeds SLA (1.0s)")
                else:
                    self.log_result("SLA Validation", "PASS", f"Router p95 {p95}s within SLA")
            else:
                self.log_result("SLA Validation", "WARN", "No p95 metrics available")
            
            return True
            
        except Exception as e:
            self.log_result("SLA Validation", "FAIL", f"Error testing SLA validation: {e}")
            return False
    
    def test_robustness(self) -> bool:
        """Test robustness features."""
        try:
            # Test health endpoints
            live_response = requests.get(f"{self.core_url}/health/live", timeout=10)
            ready_response = requests.get(f"{self.core_url}/health/ready", timeout=10)
            
            if live_response.status_code != 200:
                self.log_result("Robustness", "FAIL", f"Health live returned {live_response.status_code}")
                return False
            
            if ready_response.status_code != 200:
                self.log_result("Robustness", "FAIL", f"Health ready returned {ready_response.status_code}")
                return False
            
            # Check response times
            live_time = live_response.elapsed.total_seconds()
            ready_time = ready_response.elapsed.total_seconds()
            
            if live_time > 0.1:  # Health checks should be fast
                self.log_result("Robustness", "WARN", f"Health live slow: {live_time:.3f}s")
            
            if ready_time > 0.1:
                self.log_result("Robustness", "WARN", f"Health ready slow: {ready_time:.3f}s")
            
            self.log_result("Robustness", "PASS", "Health endpoints working", {
                "live_time": live_time,
                "ready_time": ready_time
            })
            return True
            
        except Exception as e:
            self.log_result("Robustness", "FAIL", f"Error testing robustness: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all verification tests."""
        print("🔍 Starting Verify & Harden tests...")
        print(f"🌐 Testing against: {self.core_url}")
        print("-" * 60)
        
        tests = [
            self.test_api_contract,
            self.test_cors_trustedhost,
            self.test_api_key_auth,
            self.test_observability,
            self.test_sla_validation,
            self.test_robustness
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("-" * 60)
        success_rate = (passed / total) * 100
        print(f"📊 Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        # Generate report
        self.generate_report()
        
        return passed == total
    
    def generate_report(self) -> None:
        """Generate verification report."""
        report_file = Path("verify_harden_report.json")
        
        report_data = {
            "verification_run": {
                "timestamp": time.time(),
                "core_url": self.core_url,
                "total_tests": len(self.results),
                "passed_tests": len([r for r in self.results if r["status"] == "PASS"]),
                "failed_tests": len([r for r in self.results if r["status"] == "FAIL"]),
                "warning_tests": len([r for r in self.results if r["status"] == "WARN"])
            },
            "results": self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
        
        # Print summary
        print("\n📋 Test Summary:")
        for result in self.results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(result["status"], "❓")
            print(f"  {status_emoji} {result['test']}: {result['status']}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify & Harden Jarvis Core")
    parser.add_argument("--core-url", default="http://127.0.0.1:8000", help="Core API URL")
    args = parser.parse_args()
    
    verifier = VerifyHarden(args.core_url)
    success = verifier.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
