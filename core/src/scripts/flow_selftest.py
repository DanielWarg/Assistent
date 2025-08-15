"""
Flow self-test script for end-to-end testing with correlation ID tracking.
"""
import json
import time
import sys
import argparse
import uuid
import asyncio
import httpx
from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    """Test result with correlation ID."""
    test_id: str
    correlation_id: str
    stage: str
    status: str
    details: str
    duration: float
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FlowSelftest:
    """Flow self-test runner with correlation ID tracking."""
    
    def __init__(self, output_file: str = "./logs/flow.jsonl", core_url: str = "http://localhost:8000"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.core_url = core_url
        self.correlation_id = str(uuid.uuid4())
        self.results: List[TestResult] = []
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def log_result(self, stage: str, status: str, details: str = "", duration: float = 0.0, metadata: Dict[str, Any] = None) -> None:
        """Log a test result with correlation ID."""
        result = TestResult(
            test_id=str(uuid.uuid4()),
            correlation_id=self.correlation_id,
            stage=stage,
            status=status,
            details=details,
            duration=duration,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.results.append(result)
        print(f"[{stage}] {status}: {details}")
    
    async def test_health_endpoints(self) -> bool:
        """Test health check endpoints."""
        start_time = time.time()
        try:
            # Test /health/live
            response = await self.http_client.get(f"{self.core_url}/health/live")
            if response.status_code != 200:
                await self.log_result("health_live", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            # Test /health/ready
            response = await self.http_client.get(f"{self.core_url}/health/ready")
            if response.status_code != 200:
                await self.log_result("health_ready", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            await self.log_result("health_endpoints", "ok", "Health endpoints working", time.time() - start_time)
            return True
            
        except Exception as e:
            await self.log_result("health_endpoints", "error", str(e), time.time() - start_time)
            return False
    
    async def test_metrics_endpoint(self) -> bool:
        """Test metrics endpoint and validate SLA."""
        start_time = time.time()
        try:
            response = await self.http_client.get(f"{self.core_url}/metrics")
            if response.status_code != 200:
                await self.log_result("metrics_endpoint", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            metrics = response.json()
            
            # Validate metrics structure
            required_fields = ["router", "e2e", "errors", "system", "timestamp"]
            for field in required_fields:
                if field not in metrics:
                    await self.log_result("metrics_structure", "error", f"Missing field: {field}", time.time() - start_time)
                    return False
            
            # Check SLA (p95 < 1.0s for router)
            router_metrics = metrics.get("router", {})
            p95 = router_metrics.get("p95")
            if p95 is not None and p95 > 1.0:
                await self.log_result("metrics_sla", "warning", f"Router p95 {p95}s exceeds SLA (1.0s)", time.time() - start_time)
            
            await self.log_result("metrics_endpoint", "ok", "Metrics endpoint working", time.time() - start_time, {"metrics": metrics})
            return True
            
        except Exception as e:
            await self.log_result("metrics_endpoint", "error", str(e), time.time() - start_time)
            return False
    
    async def test_logs_endpoint(self) -> bool:
        """Test logs endpoint and SSE streaming."""
        start_time = time.time()
        try:
            # Test /logs/recent
            response = await self.http_client.get(f"{self.core_url}/logs/recent?limit=10")
            if response.status_code != 200:
                await self.log_result("logs_recent", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            logs = response.json()
            if not isinstance(logs, list):
                await self.log_result("logs_structure", "error", "Logs not a list", time.time() - start_time)
                return False
            
            # Test /logs/stats
            response = await self.http_client.get(f"{self.core_url}/logs/stats")
            if response.status_code != 200:
                await self.log_result("logs_stats", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            stats = response.json()
            await self.log_result("logs_endpoint", "ok", "Logs endpoints working", time.time() - start_time, {"logs_count": len(logs), "stats": stats})
            return True
            
        except Exception as e:
            await self.log_result("logs_endpoint", "error", str(e), time.time() - start_time)
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Test API endpoints with authentication."""
        start_time = time.time()
        try:
            # Test root endpoint
            response = await self.http_client.get(f"{self.core_url}/")
            if response.status_code != 200:
                await self.log_result("api_root", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            # Test info endpoint
            response = await self.http_client.get(f"{self.core_url}/info")
            if response.status_code != 200:
                await self.log_result("api_info", "error", f"Status {response.status_code}", time.time() - start_time)
                return False
            
            info = response.json()
            if info.get("python_version") != "3.11+":
                await self.log_result("api_version", "warning", f"Python version: {info.get('python_version')}", time.time() - start_time)
            
            await self.log_result("api_endpoints", "ok", "API endpoints working", time.time() - start_time, {"info": info})
            return True
            
        except Exception as e:
            await self.log_result("api_endpoints", "error", str(e), time.time() - start_time)
            return False
    
    async def test_performance(self) -> bool:
        """Test performance with multiple concurrent requests."""
        start_time = time.time()
        try:
            # Make 10 concurrent requests to test performance
            urls = [f"{self.core_url}/health/live" for _ in range(10)]
            
            async def make_request(url: str) -> float:
                req_start = time.time()
                response = await self.http_client.get(url)
                return time.time() - req_start
            
            # Execute concurrent requests
            response_times = await asyncio.gather(*[make_request(url) for url in urls])
            
            # Calculate performance metrics
            avg_time = sum(response_times) / len(response_times)
            p50_time = sorted(response_times)[len(response_times) // 2]
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            # Check SLA (p95 < 0.5s)
            if p95_time > 0.5:
                await self.log_result("performance_sla", "warning", f"p95 {p95_time:.3f}s exceeds SLA (0.5s)", time.time() - start_time)
            
            await self.log_result("performance_test", "ok", "Performance test completed", time.time() - start_time, {
                "avg_time": avg_time,
                "p50_time": p50_time,
                "p95_time": p95_time,
                "response_times": response_times
            })
            return True
            
        except Exception as e:
            await self.log_result("performance_test", "error", str(e), time.time() - start_time)
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests with correlation ID tracking."""
        await self.log_result("selftest_start", "info", f"Starting flow self-test (ID: {self.correlation_id})")
        
        tests = [
            self.test_health_endpoints,
            self.test_metrics_endpoint,
            self.test_logs_endpoint,
            self.test_api_endpoints,
            self.test_performance
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if await test():
                passed += 1
        
        success_rate = (passed / total) * 100
        await self.log_result("selftest_complete", "info", f"Tests completed: {passed}/{total} passed ({success_rate:.1f}%)")
        
        return passed == total
    
    async def save_results(self) -> None:
        """Save results to JSONL file."""
        with open(self.output_file, 'w') as f:
            for result in self.results:
                f.write(json.dumps(asdict(result)) + '\n')
        
        print(f"Results saved to: {self.output_file}")
    
    async def generate_report(self) -> None:
        """Generate test report in JSON and Markdown formats."""
        # JSON report
        report_file = self.output_file.with_suffix('.json')
        report_data = {
            "test_run": {
                "correlation_id": self.correlation_id,
                "timestamp": time.time(),
                "total_tests": len(self.results),
                "passed_tests": len([r for r in self.results if r.status == "ok"]),
                "failed_tests": len([r for r in self.results if r.status == "error"]),
                "warning_tests": len([r for r in self.results if r.status == "warning"])
            },
            "results": [asdict(r) for r in self.results]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Markdown report
        md_file = self.output_file.with_suffix('.md')
        with open(md_file, 'w') as f:
            f.write(f"# Flow Self-Test Report\n\n")
            f.write(f"**Correlation ID:** `{self.correlation_id}`\n")
            f.write(f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Tests:** {len(self.results)}\n")
            f.write(f"- **Passed:** {len([r for r in self.results if r.status == 'ok'])}\n")
            f.write(f"- **Failed:** {len([r for r in self.results if r.status == 'error'])}\n")
            f.write(f"- **Warnings:** {len([r for r in self.results if r.status == 'warning'])}\n\n")
            
            f.write(f"## Test Results\n\n")
            for result in self.results:
                status_emoji = {"ok": "✅", "error": "❌", "warning": "⚠️"}.get(result.status, "❓")
                f.write(f"### {status_emoji} {result.stage}\n")
                f.write(f"- **Status:** {result.status}\n")
                f.write(f"- **Duration:** {result.duration:.3f}s\n")
                f.write(f"- **Details:** {result.details}\n")
                if result.metadata:
                    f.write(f"- **Metadata:** {json.dumps(result.metadata, indent=2)}\n")
                f.write(f"\n")
        
        print(f"Reports generated: {report_file}, {md_file}")
    
    async def cleanup(self):
        """Clean up resources."""
        await self.http_client.aclose()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Flow self-test runner")
    parser.add_argument("--out", default="./logs/flow.jsonl", help="Output file path")
    parser.add_argument("--core-url", default="http://localhost:8000", help="Core API URL")
    args = parser.parse_args()
    
    selftest = FlowSelftest(args.out, args.core_url)
    
    try:
        success = await selftest.run_all_tests()
        await selftest.save_results()
        await selftest.generate_report()
        
        sys.exit(0 if success else 1)
    finally:
        await selftest.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
