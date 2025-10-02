"""Parallel execution example for GSB-Selenium."""

import sys
import concurrent.futures
import threading
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot


def run_bot_instance(instance_id: str, searches_per_instance: int) -> dict:
    """Run a single bot instance."""
    result = {
        "instance_id": instance_id,
        "success": False,
        "searches_completed": 0,
        "error": None
    }
    
    try:
        # Create configuration for this instance
        config = GSBConfig(
            search_term="digital marketing solutions",
            target_website="example.com",  # Replace with your target
            headless=True,  # Always use headless for parallel execution
            
            # Randomize some settings per instance
            search_range_min=searches_per_instance,
            search_range_max=searches_per_instance,
            click_probability=0.2,
            
            # Optimize for parallel execution
            take_screenshots=False,  # Disable screenshots for performance
            human_like_behavior=True,
            min_search_interval=30.0,  # Shorter intervals for demo
            max_search_interval=60.0,
        )
        
        # Create and run bot
        bot = GoogleSearchBot(config, instance_id)
        print(f"[{instance_id}] Starting {searches_per_instance} searches...")
        
        bot.run_search_session(searches_per_instance)
        
        result["success"] = True
        result["searches_completed"] = searches_per_instance
        print(f"[{instance_id}] ✅ Completed successfully!")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"[{instance_id}] ❌ Failed: {e}")
    
    return result


def main():
    """Run multiple GSB-Selenium instances in parallel."""
    print("🚀 GSB-Selenium Parallel Execution Example")
    print("=" * 50)
    
    # Configuration
    num_instances = 3
    searches_per_instance = 2
    
    print(f"Running {num_instances} instances in parallel")
    print(f"Each instance will perform {searches_per_instance} searches")
    print(f"Total searches: {num_instances * searches_per_instance}")
    print()
    
    # Create thread pool and run instances
    results = []
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_instances) as executor:
            # Submit all instances
            futures = []
            for i in range(num_instances):
                instance_id = f"parallel_{i+1:03d}"
                future = executor.submit(run_bot_instance, instance_id, searches_per_instance)
                futures.append(future)
            
            print("All instances submitted, waiting for completion...")
            print()
            
            # Wait for completion and collect results
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 EXECUTION SUMMARY")
        print("=" * 50)
        
        successful_instances = [r for r in results if r["success"]]
        failed_instances = [r for r in results if not r["success"]]
        total_searches = sum(r["searches_completed"] for r in results)
        
        print(f"Total instances: {len(results)}")
        print(f"Successful: {len(successful_instances)}")
        print(f"Failed: {len(failed_instances)}")
        print(f"Total searches completed: {total_searches}")
        print()
        
        if successful_instances:
            print("✅ Successful instances:")
            for result in successful_instances:
                print(f"   {result['instance_id']}: {result['searches_completed']} searches")
        
        if failed_instances:
            print("\n❌ Failed instances:")
            for result in failed_instances:
                print(f"   {result['instance_id']}: {result['error']}")
        
        print(f"\n🎉 Parallel execution completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Parallel execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Error in parallel execution: {e}")


if __name__ == "__main__":
    main()