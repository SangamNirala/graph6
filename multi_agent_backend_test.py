#!/usr/bin/env python3
"""
Multi-Agent Script Generation System Testing Script
Tests the new Phase 1 Multi-Agent Script Generation functionality
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://a9d5007e-720d-4f4a-98a3-76f350619409.preview.emergentagent.com/api"

class MultiAgentTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_multi_agent_status(self):
        """Test GET /api/multi-agent-status endpoint"""
        print("\n🔍 Testing Multi-Agent Status Endpoint...")
        try:
            response = self.session.get(f"{self.backend_url}/multi-agent-status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "system_info", "agents"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Multi-Agent Status Structure", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                # Check if system is operational
                if data.get("status") == "operational":
                    self.log_test("Multi-Agent Status", True, 
                                f"System operational with {len(data.get('agents_available', []))} agents available")
                    
                    # Log system capabilities
                    agents = data.get("agents", {})
                    pipeline_sequence = data.get("pipeline_sequence", [])
                    supported_platforms = data.get("supported_platforms", [])
                    
                    print(f"   Available Agents: {', '.join(agents.keys())}")
                    print(f"   Pipeline Sequence: {' → '.join(pipeline_sequence)}")
                    print(f"   Supported Platforms: {', '.join(supported_platforms)}")
                    
                    return True
                else:
                    self.log_test("Multi-Agent Status", False, 
                                f"System not operational: {data.get('status')}", data)
                    return False
                    
            else:
                self.log_test("Multi-Agent Status", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Multi-Agent Status", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Multi-Agent Status", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_multi_agent_script_generation(self):
        """Test POST /api/generate-script-multi-agent endpoint"""
        print("\n🤖 Testing Multi-Agent Script Generation...")
        
        # Test data as specified in review request
        test_data = {
            "prompt": "Create a video about healthy cooking tips",
            "video_type": "educational",
            "duration": "short",
            "target_platform": "youtube",
            "context": {}
        }
        
        try:
            print(f"   Sending request with data: {json.dumps(test_data, indent=2)}")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.backend_url}/generate-script-multi-agent",
                json=test_data,
                timeout=300  # 5 minutes timeout for complex AI processing
            )
            
            processing_time = time.time() - start_time
            print(f"   Processing time: {processing_time:.1f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify core response structure
                required_fields = [
                    "generated_script", "agent_outputs", "system_metadata", 
                    "performance_summary", "integration_summary"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Multi-Agent Response Structure", False, 
                                f"Missing required fields: {missing_fields}", data.keys())
                    return False
                
                self.log_test("Multi-Agent Response Structure", True, 
                            "All required response fields present")
                
                # Test generated script quality
                generated_script = data.get("generated_script", "")
                if len(generated_script) > 500:  # Expect substantial content
                    self.log_test("Generated Script Quality", True, 
                                f"Generated script has {len(generated_script)} characters")
                else:
                    self.log_test("Generated Script Quality", False, 
                                f"Generated script too short: {len(generated_script)} characters")
                
                # Test agent outputs structure
                agent_outputs = data.get("agent_outputs", {})
                expected_agents = ["narrative", "engagement", "technical", "quality", "coordinator"]
                
                agents_found = list(agent_outputs.keys())
                missing_agents = [agent for agent in expected_agents if agent not in agents_found]
                
                if missing_agents:
                    self.log_test("Agent Pipeline Completeness", False, 
                                f"Missing agents: {missing_agents}. Found: {agents_found}")
                else:
                    self.log_test("Agent Pipeline Completeness", True, 
                                f"All 5 expected agents processed: {', '.join(agents_found)}")
                
                # Test individual agent outputs
                self.test_agent_specialization(agent_outputs)
                
                # Test system metadata
                system_metadata = data.get("system_metadata", {})
                if "processing_time" in system_metadata and "agents_used" in system_metadata:
                    self.log_test("System Metadata", True, 
                                f"Processing time: {system_metadata.get('processing_time')}, "
                                f"Agents used: {system_metadata.get('agents_used')}")
                else:
                    self.log_test("System Metadata", False, 
                                "Missing processing_time or agents_used in metadata")
                
                # Test performance summary
                performance_summary = data.get("performance_summary", {})
                if "quality_scores" in performance_summary:
                    self.log_test("Performance Summary", True, 
                                f"Quality scores available: {list(performance_summary.get('quality_scores', {}).keys())}")
                else:
                    self.log_test("Performance Summary", False, 
                                "Missing quality_scores in performance summary")
                
                # Test integration summary
                integration_summary = data.get("integration_summary", {})
                if len(integration_summary) >= 3:  # Expect contributions from multiple agents
                    self.log_test("Integration Summary", True, 
                                f"Agent contributions documented: {list(integration_summary.keys())}")
                else:
                    self.log_test("Integration Summary", False, 
                                f"Insufficient integration summary: {integration_summary}")
                
                # Overall assessment
                if processing_time <= 240:  # 4 minutes or less
                    self.log_test("Processing Performance", True, 
                                f"Processing completed in {processing_time:.1f}s (within 4min target)")
                else:
                    self.log_test("Processing Performance", False, 
                                f"Processing took {processing_time:.1f}s (exceeds 4min target)")
                
                return True
                
            else:
                self.log_test("Multi-Agent Script Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("Multi-Agent Script Generation", False, 
                        "Request timed out (>5 minutes)")
            return False
        except requests.exceptions.RequestException as e:
            self.log_test("Multi-Agent Script Generation", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Multi-Agent Script Generation", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_agent_specialization(self, agent_outputs):
        """Test that each agent focused on their specialty"""
        print("\n🎯 Testing Agent Specialization...")
        
        specialization_tests = {
            "narrative": ["story", "structure", "pacing", "narrative", "plot"],
            "engagement": ["hook", "retention", "engagement", "audience", "attention"],
            "technical": ["youtube", "platform", "optimization", "technical", "format"],
            "quality": ["quality", "polish", "coherence", "improvement", "refinement"],
            "coordinator": ["integration", "coordination", "final", "synthesis", "combination"]
        }
        
        for agent_name, keywords in specialization_tests.items():
            if agent_name in agent_outputs:
                agent_output = agent_outputs[agent_name]
                
                # Check if agent output contains specialization keywords
                output_text = str(agent_output).lower()
                found_keywords = [kw for kw in keywords if kw in output_text]
                
                if len(found_keywords) >= 2:  # At least 2 specialization keywords
                    self.log_test(f"{agent_name.title()} Agent Specialization", True, 
                                f"Found specialization keywords: {', '.join(found_keywords)}")
                else:
                    self.log_test(f"{agent_name.title()} Agent Specialization", False, 
                                f"Limited specialization evidence. Found: {', '.join(found_keywords)}")
            else:
                self.log_test(f"{agent_name.title()} Agent Specialization", False, 
                            f"Agent {agent_name} not found in outputs")
    
    def test_sequential_pipeline(self, agent_outputs):
        """Test that agents processed in correct order"""
        print("\n🔄 Testing Sequential Pipeline...")
        
        expected_order = ["narrative", "engagement", "technical", "quality", "coordinator"]
        
        # Check if all agents have processing_time or order indicators
        agent_times = {}
        for agent_name in expected_order:
            if agent_name in agent_outputs:
                agent_data = agent_outputs[agent_name]
                if isinstance(agent_data, dict) and "processing_time" in agent_data:
                    agent_times[agent_name] = agent_data["processing_time"]
        
        if len(agent_times) >= 3:  # At least 3 agents with timing data
            self.log_test("Sequential Pipeline", True, 
                        f"Pipeline timing data available for {len(agent_times)} agents")
        else:
            self.log_test("Sequential Pipeline", False, 
                        f"Insufficient pipeline timing data: {list(agent_times.keys())}")
    
    def run_all_tests(self):
        """Run all multi-agent system tests"""
        print("🚀 Starting Multi-Agent Script Generation System Tests")
        print("=" * 60)
        
        # Test 1: Multi-Agent Status
        status_ok = self.test_multi_agent_status()
        
        # Test 2: Multi-Agent Script Generation (main test)
        if status_ok:
            script_ok = self.test_multi_agent_script_generation()
        else:
            print("\n⚠️  Skipping script generation test due to status endpoint failure")
            script_ok = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Multi-Agent System is fully operational!")
        else:
            print(f"\n⚠️  {total - passed} tests failed - Review issues above")
        
        return passed == total

def main():
    """Main test execution"""
    tester = MultiAgentTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()