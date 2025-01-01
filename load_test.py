import asyncio
import aiohttp
import random
import time
import json
from typing import List, Dict
import string
from datetime import datetime
import argparse
from enum import Enum

class TestType(str, Enum):
    ASYNC = "async"
    SYNC = "sync"
    BOTH = "both"

class EmbeddingLoadTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.keywords = [
            "machine learning", "artificial intelligence", "deep learning",
            "neural networks", "data science", "big data", "analytics",
            "computer vision", "natural language processing", "robotics",
            "predictive analytics", "reinforcement learning", "supervised learning",
            "unsupervised learning", "semi-supervised learning", "AI ethics",
            "generative AI", "AI-driven automation", "edge computing",
            "federated learning", "transfer learning", "decision trees",
            "random forests", "support vector machines", "gradient boosting",
            "recommender systems", "sentiment analysis", "speech recognition",
            "text mining", "chatbots", "AI-powered assistants", "image processing",
            "video analytics", "sensor data analysis", "autonomous vehicles",
            "IoT analytics", "time series forecasting", "feature engineering",
            "data wrangling", "data visualization", "big data frameworks", "Hadoop",
            "Spark", "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
            "natural language generation", "knowledge graphs", "AI in healthcare",
            "AI in finance", "AI in education", "AI in gaming", "AI in retail",
            "machine vision", "adversarial AI", "AI-driven cybersecurity",
            "anomaly detection", "algorithm optimization", "cloud-based AI",
            "explainable AI", "AI governance", "AI regulations",
            "model interpretability", "AI fairness", "cognitive computing",
            "computational linguistics", "information retrieval",
            "AI-powered marketing", "personalization engines", "data pipelines",
            "knowledge discovery", "AI for social good", "computer-aided design",
            "AI in manufacturing", "supply chain optimization",
            "robotic process automation", "virtual reality AI",
            "augmented reality AI", "AI for smart cities", "digital twins",
            "real-time data processing", "online learning algorithms", "meta-learning",
            "Bayesian networks", "fuzzy logic systems", "genetic algorithms",
            "swarm intelligence", "cognitive robotics", "AI-based diagnostics",
            "AI for climate modeling", "reinforcement policies", "multi-agent systems",
            "AI in defense", "AI in agriculture", "AI in transportation",
            "quantum machine learning", "AI-powered search engines", "data ethics",
            "AI in art and creativity", "AI in music", "AI in sports"
        ]

        self.results = {
            "async": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "response_times": [],
                "errors": {}
            },
            "sync": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "response_times": [],
                "errors": {}
            }
        }

    def generate_random_text(self, min_length: int = 900, max_length: int = 1524) -> str:
        """Generate random text with keywords for realistic testing"""
        selected_keywords = random.sample(self.keywords, random.randint(1, 3))
        words = []
        target_length = random.randint(min_length, max_length)
        
        while sum(len(word) for word in words) < target_length:
            if random.random() < 0.2 and selected_keywords:
                words.append(random.choice(selected_keywords))
            else:
                word_length = random.randint(3, 10)
                random_word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
                words.append(random_word)
        
        return ' '.join(words)

    async def send_async_request(self, session: aiohttp.ClientSession, request_id: int) -> dict:
        """Send a request to the async embedding endpoint"""
        start_time = time.time()
        result = {
            "request_id": request_id,
            "success": False,
            "response_time": 0,
            "error": None,
            "type": "async"
        }

        try:
            text = self.generate_random_text()
            priority = random.choice(["low", "medium", "high"])
            
            payload = {
                "text": text,
                "priority": priority
            }

            async with session.post(
                f"{self.base_url}/submit",
                json=payload,
                timeout=30
            ) as response:
                result["response_time"] = time.time() - start_time
                result["status_code"] = response.status
                
                if response.status == 200:
                    result["success"] = True
                    result["response"] = await response.json()
                else:
                    result["error"] = f"HTTP {response.status}"

        except Exception as e:
            result["error"] = str(e)
            result["response_time"] = time.time() - start_time

        return result

    async def send_sync_request(self, session: aiohttp.ClientSession, request_id: int) -> dict:
        """Send a request to the sync embedding endpoint"""
        start_time = time.time()
        result = {
            "request_id": request_id,
            "success": False,
            "response_time": 0,
            "error": None,
            "type": "sync"
        }

        try:
            text = self.generate_random_text()
            payload = {
                "text": text,
                "use_cache": False
            }

            async with session.post(
                f"{self.base_url}/embed_sync",
                json=payload,
                timeout=30
            ) as response:
                result["response_time"] = time.time() - start_time
                result["status_code"] = response.status
                
                if response.status == 200:
                    result["success"] = True
                    result["response"] = await response.json()
                else:
                    result["error"] = f"HTTP {response.status}"

        except Exception as e:
            result["error"] = str(e)
            result["response_time"] = time.time() - start_time

        return result

    def _process_results(self, result: dict):
        """Process and store results from a request"""
        test_type = result["type"]
        self.results[test_type]["total_requests"] += 1
        
        if result["success"]:
            self.results[test_type]["successful_requests"] += 1
        else:
            self.results[test_type]["failed_requests"] += 1
            error_type = str(result.get("error", "unknown"))
            self.results[test_type]["errors"][error_type] = self.results[test_type]["errors"].get(error_type, 0) + 1
            
        self.results[test_type]["response_times"].append(result["response_time"])

    async def run_load_test(
        self,
        num_requests: int = 1000,
        concurrent_requests: int = 50,
        test_type: TestType = TestType.BOTH
    ):
        """Run the load test with specified parameters"""
        print(f"\nStarting load test with {num_requests} requests per type, {concurrent_requests} concurrent requests")
        print(f"Test type: {test_type}")
        print(f"Target URL: {self.base_url}")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            request_counter = 0
            
            while request_counter < num_requests:
                if test_type in [TestType.ASYNC, TestType.BOTH]:
                    tasks.append(self.send_async_request(session, request_counter))
                
                if test_type in [TestType.SYNC, TestType.BOTH]:
                    tasks.append(self.send_sync_request(session, request_counter))
                
                request_counter += 1
                
                # Process in batches of concurrent_requests
                if len(tasks) >= concurrent_requests:
                    batch_results = await asyncio.gather(*tasks)
                    for result in batch_results:
                        self._process_results(result)
                    tasks = []
                    
                    # Print progress
                    progress = (request_counter / num_requests) * 100
                    print(f"\rProgress: {progress:.1f}%", end="")
            
            # Process remaining tasks
            if tasks:
                batch_results = await asyncio.gather(*tasks)
                for result in batch_results:
                    self._process_results(result)

        self._print_final_results()

    def _print_final_results(self):
        """Print the final test results"""
        print("\n\n=== Load Test Results ===")
        
        for test_type in ["async", "sync"]:
            if self.results[test_type]["total_requests"] > 0:
                print(f"\n{test_type.upper()} Endpoint Results:")
                print(f"Total Requests: {self.results[test_type]['total_requests']}")
                print(f"Successful Requests: {self.results[test_type]['successful_requests']}")
                print(f"Failed Requests: {self.results[test_type]['failed_requests']}")
                
                if self.results[test_type]["response_times"]:
                    avg_time = sum(self.results[test_type]["response_times"]) / len(self.results[test_type]["response_times"])
                    print(f"Average Response Time: {avg_time:.3f} seconds")
                    print(f"Min Response Time: {min(self.results[test_type]['response_times']):.3f} seconds")
                    print(f"Max Response Time: {max(self.results[test_type]['response_times']):.3f} seconds")
                
                success_rate = (self.results[test_type]["successful_requests"] / self.results[test_type]["total_requests"]) * 100
                print(f"Success Rate: {success_rate:.1f}%")
                
                if self.results[test_type]["errors"]:
                    print("\nErrors:")
                    for error, count in self.results[test_type]["errors"].items():
                        print(f"  {error}: {count} occurrences")

async def main():
    parser = argparse.ArgumentParser(description='Load Test for Embedding Service')
    parser.add_argument('--requests', type=int, default=10000, help='Number of requests to send')
    parser.add_argument('--concurrent', type=int, default=500, help='Number of concurrent requests')
    parser.add_argument('--type', type=TestType, default=TestType.SYNC, choices=list(TestType), help='Type of test to run')
    parser.add_argument('--url', type=str, default='http://localhost:8123', help='Base URL of the embedding service')
    
    args = parser.parse_args()
    
    load_tester = EmbeddingLoadTest(base_url=args.url)
    await load_tester.run_load_test(
        num_requests=args.requests,
        concurrent_requests=args.concurrent,
        test_type=args.type
    )

if __name__ == "__main__":
    asyncio.run(main())