#!/usr/bin/env python3
"""
Backend API Testing for Geo Intel (Radar) Module
Tests all backend endpoints using the public URL from REACT_APP_BACKEND_URL
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class GeoIntelAPITester:
    def __init__(self, base_url="https://tg-full-stack.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.headers = {'Content-Type': 'application/json'}
        self.critical_failures = []

    def log_result(self, test_name: str, passed: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        else:
            if "health" in test_name.lower() or "connection" in details.lower():
                self.critical_failures.append(test_name)
        
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, data: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=15)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=15)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=15)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers=self.headers, timeout=15)
            else:
                self.log_result(name, False, f"Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status
            response_json = {}
            
            try:
                response_json = response.json()
            except:
                response_json = {"raw_response": response.text[:500]}

            if success:
                self.log_result(name, True, f"Status: {response.status_code}", response_json)
            else:
                self.log_result(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}")

            return success, response_json

        except requests.exceptions.ConnectionError:
            self.log_result(name, False, "Connection refused - Backend server not accessible")
            return False, {}
        except requests.exceptions.Timeout:
            self.log_result(name, False, "Request timeout")
            return False, {}
        except Exception as e:
            self.log_result(name, False, f"Unexpected error: {str(e)}")
            return False, {}

    def test_geo_health(self):
        """Test /api/geo/health endpoint - CRITICAL"""
        print("\n🔍 Testing Geo Health Endpoint...")
        success, data = self.run_test("Geo Health Check", "GET", "/api/geo/health", 200)
        
        if success and data:
            # Verify expected fields in health response
            expected_fields = ["ok", "module", "version"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Health Response Structure", True, "All required fields present")
            else:
                self.log_result("Health Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if module name is correct
            if data.get("module") == "geo-intel":
                self.log_result("Module Name", True, "Correct module name 'geo-intel'")
            else:
                self.log_result("Module Name", False, f"Expected 'geo-intel', got '{data.get('module')}'")
                
        return success

    def test_geo_map(self):
        """Test /api/geo/map endpoint"""
        print("\n🗺️  Testing Geo Map Endpoint...")
        success, data = self.run_test("Geo Map Points", "GET", "/api/geo/map", 200)
        
        if success and data:
            # Verify expected fields in map response
            expected_fields = ["ok", "items"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Map Response Structure", True, "All required fields present")
            else:
                self.log_result("Map Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if items is a list
            if isinstance(data.get("items"), list):
                item_count = len(data['items'])
                self.log_result("Map Items Type", True, f"Items is list with {item_count} map points")
                
                # If we have items, check structure of first item
                if item_count > 0:
                    first_item = data['items'][0]
                    required_item_fields = ["lat", "lng", "title"]
                    missing_item_fields = [field for field in required_item_fields if field not in first_item]
                    
                    if not missing_item_fields:
                        self.log_result("Map Item Structure", True, "Map items have required fields")
                    else:
                        self.log_result("Map Item Structure", False, f"Missing fields in items: {missing_item_fields}")
            else:
                self.log_result("Map Items Type", False, "Items should be a list")
                
        # Test with parameters
        success_params, data_params = self.run_test("Geo Map with Params", "GET", "/api/geo/map?days=7&limit=100", 200)
        
        return success and success_params

    def test_geo_radar(self):
        """Test /api/geo/radar endpoint with specific parameters"""
        print("\n📡 Testing Geo Radar Endpoint...")
        # Test with specific coordinates as mentioned in review request
        radar_params = "lat=50.45&lng=30.52&radius=1000"
        success, data = self.run_test("Geo Radar", "GET", f"/api/geo/radar?{radar_params}", 200)
        
        if success and data:
            # Verify expected fields in radar response
            expected_fields = ["ok", "items", "userLocation", "count", "insideRadius"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Radar Response Structure", True, "All required fields present")
            else:
                self.log_result("Radar Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if items is a list
            if isinstance(data.get("items"), list):
                item_count = len(data['items'])
                self.log_result("Radar Items Type", True, f"Items is list with {item_count} radar points")
                
                # If we have items, check for distanceMeters and isInsideRadius fields
                if item_count > 0:
                    first_item = data['items'][0]
                    required_radar_fields = ["distanceMeters", "isInsideRadius", "lat", "lng"]
                    missing_radar_fields = [field for field in required_radar_fields if field not in first_item]
                    
                    if not missing_radar_fields:
                        self.log_result("Radar Item Structure", True, "Radar items have distanceMeters, isInsideRadius fields")
                    else:
                        self.log_result("Radar Item Structure", False, f"Missing fields in radar items: {missing_radar_fields}")
            else:
                self.log_result("Radar Items Type", False, "Items should be a list")
                
            # Check userLocation structure
            user_location = data.get("userLocation", {})
            if "lat" in user_location and "lng" in user_location and "radius" in user_location:
                self.log_result("Radar User Location", True, "User location has required fields")
            else:
                self.log_result("Radar User Location", False, "User location missing required fields")
                
        return success

    def test_geo_stats(self):
        """Test /api/geo/stats endpoint"""
        print("\n📊 Testing Geo Stats Endpoint...")
        success, data = self.run_test("Geo Stats", "GET", "/api/geo/stats", 200)
        
        if success and data:
            # Verify expected fields in stats response
            expected_fields = ["ok", "totalEvents", "totalChannels", "enabledChannels"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Stats Response Structure", True, "All required fields present")
            else:
                self.log_result("Stats Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if numeric fields are actually numbers
            numeric_fields = ["totalEvents", "totalChannels", "enabledChannels"]
            for field in numeric_fields:
                if field in data and isinstance(data[field], (int, float)):
                    self.log_result(f"Stats {field} Type", True, f"{field}: {data[field]}")
                else:
                    self.log_result(f"Stats {field} Type", False, f"{field} should be numeric")
                    
        return success

    def test_geo_stats_full(self):
        """Test /api/geo/stats/full endpoint"""
        print("\n📈 Testing Geo Stats Full Endpoint...")
        success, data = self.run_test("Geo Stats Full", "GET", "/api/geo/stats/full", 200)
        
        if success and data:
            # Verify expected fields in full stats response
            expected_fields = ["ok", "topPlaces", "hourly", "weekday"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Stats Full Response Structure", True, "All required fields present")
            else:
                self.log_result("Stats Full Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if arrays are present
            array_fields = ["topPlaces", "hourly", "weekday"]
            for field in array_fields:
                if field in data and isinstance(data[field], list):
                    self.log_result(f"Stats Full {field} Type", True, f"{field} is list with {len(data[field])} items")
                else:
                    self.log_result(f"Stats Full {field} Type", False, f"{field} should be a list")
                    
        return success

    def test_geo_predict(self):
        """Test /api/geo/predict endpoint"""
        print("\n🔮 Testing Geo Predict Endpoint...")
        success, data = self.run_test("Geo Predict", "GET", "/api/geo/predict", 200)
        
        if success and data:
            # Verify expected fields in predictions response
            expected_fields = ["ok", "predictions"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Predict Response Structure", True, "All required fields present")
            else:
                self.log_result("Predict Response Structure", False, f"Missing fields: {missing_fields}")
                
            # Check if predictions is a list
            if isinstance(data.get("predictions"), list):
                pred_count = len(data['predictions'])
                self.log_result("Predict Items Type", True, f"Predictions is list with {pred_count} items")
            else:
                self.log_result("Predict Items Type", False, "Predictions should be a list")
                
        return success

    def test_geo_seed_data(self):
        """Test /api/geo/admin/seed endpoint"""
        print("\n🌱 Testing Geo Seed Data Endpoint...")
        seed_data = {"count": 50}  # Smaller count for testing
        success, data = self.run_test("Geo Seed Data", "POST", "/api/geo/admin/seed?count=50", 200, seed_data)
        
        if success and data:
            # Verify expected fields in seed response
            expected_fields = ["ok"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Seed Response Structure", True, "All required fields present")
            else:
                self.log_result("Seed Response Structure", False, f"Missing fields: {missing_fields}")
                
        return success

    def test_additional_endpoints(self):
        """Test additional geo endpoints for completeness"""
        print("\n🔍 Testing Additional Geo Endpoints...")
        
        # Test version endpoint
        self.run_test("Geo Version", "GET", "/api/geo/version", 200)
        
        # Test channels endpoint
        self.run_test("Geo Channels", "GET", "/api/geo/channels", 200)
        
        # Test top places
        self.run_test("Geo Top Places", "GET", "/api/geo/top", 200)
        
        # Test search endpoint
        self.run_test("Search Channels", "GET", "/api/geo/search/channels?q=test", 200)
        
        # Test summary endpoint (might take longer)
        print("⏳ Testing AI Summary endpoint (may take a few seconds)...")
        time.sleep(2)  # Give AI time if needed
        self.run_test("Geo Summary", "GET", "/api/geo/summary?days=7", 200)
        
        # Test event types endpoint
        self.run_test("Event Types", "GET", "/api/geo/event-types", 200)

    def run_all_tests(self):
        """Run all geo intel API tests"""
        print("🚀 Starting Geo Intel API Tests")
        print(f"🌐 Testing backend at: {self.base_url}")
        print("=" * 60)
        
        # Test core required endpoints first
        health_ok = self.test_geo_health()
        
        # If health fails, we might have bigger issues
        if not health_ok:
            print("❌ CRITICAL: Health check failed. Backend may not be running or accessible.")
            return False
            
        # Continue with main endpoints
        self.test_geo_map()
        self.test_geo_radar()  # Required radar endpoint
        self.test_geo_stats()
        self.test_geo_stats_full()  # Required full stats endpoint
        self.test_geo_predict()  # Required predictions endpoint
        
        # Seed data for testing
        self.test_geo_seed_data()
        
        # Test additional endpoints
        self.test_additional_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"🚨 Critical Failures: {', '.join(self.critical_failures)}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        elif success_rate >= 80:
            print("✅ Most tests passed - Backend is functional")
            return True
        else:
            print("⚠️  Many tests failed. Check backend server.")
            return False

    def get_test_summary(self):
        """Get test summary for reporting"""
        failed_tests = [r for r in self.test_results if not r['passed']]
        passed_tests = [r for r in self.test_results if r['passed']]
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "critical_failures": self.critical_failures,
            "failed_test_names": [t['test_name'] for t in failed_tests],
            "passed_test_names": [t['test_name'] for t in passed_tests]
        }

def main():
    """Main test runner"""
    print("🎯 Geo Intel Backend API Testing")
    print("Testing backend endpoints via public URL")
    
    tester = GeoIntelAPITester("https://tg-full-stack.preview.emergentagent.com")
    success = tester.run_all_tests()
    
    return tester, success

if __name__ == "__main__":
    tester, success = main()
    sys.exit(0 if success else 1)