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

    def test_playback_endpoints(self):
        """Test Playback Control endpoints - REQUIRED by review request"""
        print("\n📹 Testing Playback Control Endpoints...")
        
        # Test basic playback with specified parameters
        success, data = self.run_test("Playback Frames (24h, 30min)", "GET", "/api/geo/playback?hours=24&step=30", 200)
        if success and data:
            expected_fields = ["ok", "frames", "totalEvents", "hours", "stepMinutes"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Playback Response Structure", True, "All required fields present")
                
                # Check frames structure
                frames = data.get("frames", [])
                if isinstance(frames, list):
                    self.log_result("Playback Frames", True, f"Frames list with {len(frames)} items")
                    
                    if len(frames) > 0:
                        frame = frames[0]
                        frame_fields = ["timestamp", "timestampLocal", "events"]
                        missing_frame_fields = [field for field in frame_fields if field not in frame]
                        
                        if not missing_frame_fields:
                            self.log_result("Frame Structure", True, "Frame has required fields")
                        else:
                            self.log_result("Frame Structure", False, f"Missing fields in frame: {missing_frame_fields}")
                else:
                    self.log_result("Playback Frames", False, "Frames should be a list")
            else:
                self.log_result("Playback Response Structure", False, f"Missing fields: {missing_fields}")
        
        # Test playback summary
        self.run_test("Playback Summary", "GET", "/api/geo/playback/summary?hours=24", 200)

    def test_risk_map_endpoints(self):
        """Test Risk Map endpoints - REQUIRED by review request"""
        print("\n🗺️ Testing Risk Map Endpoints...")
        
        # Test risk zones with 7 days
        success, data = self.run_test("Risk Map Zones (7 days)", "GET", "/api/geo/risk?days=7", 200)
        if success and data:
            expected_fields = ["ok", "zones", "totalZones"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Risk Map Response Structure", True, "All required fields present")
                
                # Check zones structure
                zones = data.get("zones", [])
                if isinstance(zones, list):
                    self.log_result("Risk Zones", True, f"Zones list with {len(zones)} items")
                    
                    if len(zones) > 0:
                        zone = zones[0]
                        zone_fields = ["lat", "lng", "riskScore", "riskLevel"]
                        missing_zone_fields = [field for field in zone_fields if field not in zone]
                        
                        if not missing_zone_fields:
                            self.log_result("Risk Zone Structure", True, "Zone has required fields")
                            
                            # Check risk levels
                            risk_level = zone.get("riskLevel")
                            valid_levels = ["critical", "high", "medium", "low", "minimal"]
                            if risk_level in valid_levels:
                                self.log_result("Risk Level Values", True, f"Valid risk level: {risk_level}")
                            else:
                                self.log_result("Risk Level Values", False, f"Invalid risk level: {risk_level}")
                        else:
                            self.log_result("Risk Zone Structure", False, f"Missing fields in zone: {missing_zone_fields}")
                else:
                    self.log_result("Risk Zones", False, "Zones should be a list")
            else:
                self.log_result("Risk Map Response Structure", False, f"Missing fields: {missing_fields}")
        
        # Test location-specific risk as mentioned in review request
        success, data = self.run_test("Location Risk Check", "GET", "/api/geo/risk/location?lat=50.45&lng=30.52&radius=500", 200)
        if success and data:
            location_fields = ["ok", "lat", "lng", "riskScore", "riskLevel", "eventCount"]
            missing_location_fields = [field for field in location_fields if field not in data]
            
            if not missing_location_fields:
                self.log_result("Location Risk Structure", True, "Location risk has required fields")
                
                # Verify coordinates match
                if abs(data.get("lat", 0) - 50.45) < 0.01 and abs(data.get("lng", 0) - 30.52) < 0.01:
                    self.log_result("Location Coordinates", True, "Coordinates match request")
                else:
                    self.log_result("Location Coordinates", False, "Coordinates don't match request")
            else:
                self.log_result("Location Risk Structure", False, f"Missing fields: {missing_location_fields}")

    def test_route_safety_endpoints(self):
        """Test Route Safety endpoints - REQUIRED by review request"""
        print("\n🛣️ Testing Route Safety Endpoints...")
        
        # Test route safety check with sample route
        route_data = {
            "points": [
                {"lat": 50.4501, "lng": 30.5234},
                {"lat": 50.4521, "lng": 30.5254},
                {"lat": 50.4541, "lng": 30.5274},
                {"lat": 50.4561, "lng": 30.5294}
            ],
            "days": 3
        }
        success, data = self.run_test("Route Safety Check", "POST", "/api/geo/route/check", 200, route_data)
        if success and data:
            route_fields = ["ok", "isSafe", "hazards", "riskScore", "message"]
            missing_route_fields = [field for field in route_fields if field not in data]
            
            if not missing_route_fields:
                self.log_result("Route Safety Structure", True, "Route safety has required fields")
                
                # Check Ukrainian message
                message = data.get("message", "")
                if any(char in message for char in "абвгґдеєжзийіїклмнопрстуфхцчшщьюя"):
                    self.log_result("Ukrainian Route Message", True, "Route message contains Ukrainian text")
                else:
                    self.log_result("Ukrainian Route Message", False, "Route message may not be in Ukrainian")
                
                # Check hazards structure
                hazards = data.get("hazards", [])
                if isinstance(hazards, list):
                    self.log_result("Route Hazards", True, f"Hazards list with {len(hazards)} items")
                    
                    if len(hazards) > 0:
                        hazard = hazards[0]
                        hazard_fields = ["eventType", "lat", "lng", "distance", "severity"]
                        missing_hazard_fields = [field for field in hazard_fields if field not in hazard]
                        
                        if not missing_hazard_fields:
                            self.log_result("Hazard Structure", True, "Hazard has required fields")
                        else:
                            self.log_result("Hazard Structure", False, f"Missing fields in hazard: {missing_hazard_fields}")
                else:
                    self.log_result("Route Hazards", False, "Hazards should be a list")
            else:
                self.log_result("Route Safety Structure", False, f"Missing fields: {missing_route_fields}")
        
        # Test safe direction endpoint as mentioned in review request
        success, data = self.run_test("Safe Direction", "GET", "/api/geo/route/direction?lat=50.45&lng=30.52", 200)
        if success and data:
            direction_fields = ["ok", "currentLocation", "sectors", "safestDirection"]
            missing_direction_fields = [field for field in direction_fields if field not in data]
            
            if not missing_direction_fields:
                self.log_result("Safe Direction Structure", True, "Safe direction has required fields")
                
                # Check sectors (N, NE, E, SE, S, SW, W, NW)
                sectors = data.get("sectors", {})
                expected_sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                missing_sectors = [s for s in expected_sectors if s not in sectors]
                
                if not missing_sectors:
                    self.log_result("Direction Sectors", True, "All 8 compass sectors present")
                else:
                    self.log_result("Direction Sectors", False, f"Missing sectors: {missing_sectors}")
                    
                # Check safest direction is valid
                safest = data.get("safestDirection")
                if safest in expected_sectors:
                    self.log_result("Safest Direction Valid", True, f"Safest direction: {safest}")
                else:
                    self.log_result("Safest Direction Valid", False, f"Invalid safest direction: {safest}")
            else:
                self.log_result("Safe Direction Structure", False, f"Missing fields: {missing_direction_fields}")

    def test_intelligence_endpoints(self):
        """Test Intelligence Module specific endpoints from review request"""
        print("\n🧠 Testing Intelligence Module Endpoints...")
        
        # Test event types configuration - REQUIRED
        success, data = self.run_test("Event Types Config", "GET", "/api/geo/config/event-types", 200)
        if success and data:
            types_data = data.get("types", {})
            expected_types = ["virus", "trash", "rain", "heavy_rain"]
            missing_types = [t for t in expected_types if t not in types_data]
            
            if not missing_types:
                self.log_result("Event Types Content", True, f"All expected event types found: {expected_types}")
                
                # Check virus severity = 3
                if types_data.get("virus", {}).get("severity") == 3:
                    self.log_result("Virus Severity", True, "Virus severity is 3")
                else:
                    self.log_result("Virus Severity", False, f"Virus severity is {types_data.get('virus', {}).get('severity')}, expected 3")
                
                # Check heavy_rain severity = 4  
                if types_data.get("heavy_rain", {}).get("severity") == 4:
                    self.log_result("Heavy Rain Severity", True, "Heavy rain severity is 4")
                else:
                    self.log_result("Heavy Rain Severity", False, f"Heavy rain severity is {types_data.get('heavy_rain', {}).get('severity')}, expected 4")
            else:
                self.log_result("Event Types Content", False, f"Missing event types: {missing_types}")
        
        # Test probability predictions - REQUIRED
        success, data = self.run_test("Probability Predictions", "GET", "/api/geo/probability", 200)
        if success and data:
            if "items" in data and isinstance(data["items"], list):
                self.log_result("Probability Response", True, f"Probability data with {len(data['items'])} items")
            else:
                self.log_result("Probability Response", False, "Expected 'items' list in response")
        
        # Test rebuild probabilities - REQUIRED
        self.run_test("Rebuild Probabilities", "POST", "/api/geo/probability/rebuild", 200)
        
        # Test fused events - REQUIRED
        success, data = self.run_test("Fused Events", "GET", "/api/geo/fused", 200)
        if success and data:
            if "items" in data and isinstance(data["items"], list):
                self.log_result("Fused Events Response", True, f"Fused events data with {len(data['items'])} items")
            else:
                self.log_result("Fused Events Response", False, "Expected 'items' list in response")
        
        # Test rebuild fusion - REQUIRED
        self.run_test("Rebuild Fusion", "POST", "/api/geo/fused/rebuild", 200)
        
        # Test decay cycle - REQUIRED
        self.run_test("Run Decay Cycle", "POST", "/api/geo/decay/run", 200)
        
        # Test AI summary in Ukrainian - REQUIRED
        print("⏳ Testing AI Summary endpoint (may take a few seconds)...")
        time.sleep(3)  # Give AI time for summary generation
        success, data = self.run_test("AI Summary Ukrainian", "GET", "/api/geo/summary?days=7", 200)
        if success and data:
            summary_text = data.get("summary", "")
            if summary_text and len(summary_text) > 10:
                self.log_result("AI Summary Content", True, f"Generated summary with {len(summary_text)} characters")
                
                # Check if summary contains Ukrainian text patterns
                ukrainian_patterns = ["подій", "район", "сміття", "дощ", "вірус"]
                found_ukrainian = any(pattern in summary_text.lower() for pattern in ukrainian_patterns)
                if found_ukrainian:
                    self.log_result("Ukrainian Summary", True, "Summary contains Ukrainian text")
                else:
                    self.log_result("Ukrainian Summary", False, "Summary may not be in Ukrainian")
            else:
                self.log_result("AI Summary Content", False, "Empty or very short summary generated")
    
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
        
        # Test REQUIRED endpoints from review request
        self.test_playback_endpoints()       # NEW: Playback Control
        self.test_risk_map_endpoints()       # NEW: Risk Map
        self.test_route_safety_endpoints()   # NEW: Route Safety
            
        # Continue with main endpoints
        self.test_geo_map()
        self.test_geo_radar()  # Required radar endpoint
        self.test_geo_stats()
        self.test_geo_stats_full()  # Required full stats endpoint
        self.test_geo_predict()  # Required predictions endpoint
        
        # Test Intelligence Module specific endpoints - REQUIRED by review request
        self.test_intelligence_endpoints()
        
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