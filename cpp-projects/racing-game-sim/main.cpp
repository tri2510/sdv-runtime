#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <random>
#include <iomanip>
#include <cmath>

// Racing Game State Variables (Global for memory monitoring)
std::atomic<float> player_speed{0.0f};          // km/h - Current speed
std::atomic<float> player_x{0.0f};              // meters - Track position X
std::atomic<float> player_y{0.0f};              // meters - Track position Y
std::atomic<int> player_score{0};               // Points scored
std::atomic<int> current_lap{1};                // Current lap number
std::atomic<float> lap_time{0.0f};              // Current lap time in seconds
std::atomic<float> best_lap_time{999.9f};       // Best lap time
std::atomic<bool> nitro_active{false};          // Nitro boost status

// Game mechanics variables
std::atomic<float> fuel_level{100.0f};          // % - Fuel remaining  
std::atomic<float> tire_wear{0.0f};             // % - Tire degradation
std::atomic<float> engine_temperature{85.0f};   // °C - Engine temp
std::atomic<int> position_rank{1};              // Current race position
std::atomic<int> opponents_passed{0};           // Number of cars overtaken
std::atomic<bool> collision_detected{false};    // Collision flag
std::atomic<float> track_completion{0.0f};      // % of track completed

// Performance metrics
std::atomic<int> total_races{0};
std::atomic<float> average_speed{0.0f};
std::atomic<int> powerups_collected{0};

void printBanner() {
    std::cout << R"(
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                    FORMULA DRIFT RACING SIM                      ║
    ║                     Real-time Game Monitoring                     ║
    ║                                                                   ║
    ║  🏎️ Speed Tracking  🏁 Lap Times  🔥 Nitro  ⛽ Fuel Management    ║
    ╚═══════════════════════════════════════════════════════════════════╝
    )" << std::endl;
}

class RacingGameEngine {
private:
    std::random_device rd;
    std::mt19937 gen;
    float track_length = 2000.0f; // meters
    float start_time;
    
public:
    RacingGameEngine() : gen(rd()) {
        start_time = std::chrono::duration<float>(std::chrono::steady_clock::now().time_since_epoch()).count();
    }
    
    void updateGameState(int frame) {
        // Simulate racing dynamics
        float time_delta = 0.1f; // 100ms per frame
        
        // Speed calculation with realistic physics
        std::normal_distribution<float> speed_variation(0.0f, 2.0f);
        float base_speed = 80.0f + std::sin(frame * 0.1f) * 30.0f; // Vary between 50-110 km/h
        
        // Nitro boost logic
        if (frame % 50 == 0 && fuel_level > 10.0f) { // Activate nitro every 5 seconds
            nitro_active = true;
            std::cout << "💨 NITRO BOOST ACTIVATED!" << std::endl;
        }
        
        if (nitro_active.load()) {
            base_speed *= 1.5f; // 50% speed boost
            fuel_level = std::max(0.0f, fuel_level.load() - 2.0f); // Consume fuel faster
            if (fuel_level <= 5.0f || frame % 30 == 20) {
                nitro_active = false;
                std::cout << "💨 Nitro boost ended" << std::endl;
            }
        } else {
            fuel_level = std::max(0.0f, fuel_level.load() - 0.3f); // Normal fuel consumption
        }
        
        player_speed = std::max(0.0f, base_speed + speed_variation(gen));
        
        // Position tracking on circular track
        float speed_ms = player_speed.load() / 3.6f; // Convert km/h to m/s
        player_x = player_x.load() + speed_ms * time_delta * std::cos(frame * 0.05f);
        player_y = player_y.load() + speed_ms * time_delta * std::sin(frame * 0.05f);
        
        // Track progress and lap management
        float distance_traveled = std::sqrt(player_x.load() * player_x.load() + player_y.load() * player_y.load());
        track_completion = std::fmod(distance_traveled / track_length * 100.0f, 100.0f);
        
        // Lap completion logic
        if (track_completion > 95.0f && track_completion < 5.0f) { // Completed lap
            current_lap = current_lap.load() + 1;
            
            // Calculate lap time
            float current_time = std::chrono::duration<float>(std::chrono::steady_clock::now().time_since_epoch()).count();
            lap_time = current_time - start_time;
            
            if (lap_time < best_lap_time.load()) {
                best_lap_time = lap_time.load();
                std::cout << "🏆 NEW BEST LAP TIME: " << std::fixed << std::setprecision(2) 
                         << best_lap_time.load() << "s!" << std::endl;
            }
            
            // Reset for next lap
            start_time = current_time;
            player_x = 0.0f;
            player_y = 0.0f;
        }
        
        // Tire wear simulation
        float wear_rate = (player_speed.load() / 100.0f) * 0.1f;
        if (nitro_active.load()) wear_rate *= 2.0f;
        tire_wear = std::min(100.0f, tire_wear.load() + wear_rate);
        
        // Engine temperature (affected by speed and nitro)
        float target_temp = 85.0f + (player_speed.load() / 10.0f);
        if (nitro_active.load()) target_temp += 15.0f;
        engine_temperature = engine_temperature.load() + (target_temp - engine_temperature.load()) * 0.1f;
        
        // Scoring system
        player_score = player_score.load() + static_cast<int>(player_speed.load() / 10.0f);
        if (nitro_active.load()) player_score = player_score.load() + 10; // Bonus points for nitro
        
        // Random events
        std::uniform_real_distribution<float> event_chance(0.0f, 1.0f);
        
        // Collision detection (rare event)
        if (event_chance(gen) < 0.02f) { // 2% chance per frame
            collision_detected = true;
            player_speed = player_speed.load() * 0.5f; // Reduce speed
            std::cout << "💥 COLLISION! Speed reduced!" << std::endl;
        } else {
            collision_detected = false;
        }
        
        // Powerup collection
        if (event_chance(gen) < 0.05f) { // 5% chance
            powerups_collected = powerups_collected.load() + 1;
            player_score = player_score.load() + 50;
            std::cout << "⭐ POWERUP COLLECTED! (+50 points)" << std::endl;
        }
        
        // Position simulation (relative to AI opponents)
        if (player_speed > 90.0f && event_chance(gen) < 0.1f) {
            opponents_passed = opponents_passed.load() + 1;
            position_rank = std::max(1, position_rank.load() - 1);
            std::cout << "🏎️ OVERTAKE! Now in position " << position_rank.load() << std::endl;
        }
        
        // Calculate running averages
        average_speed = (average_speed.load() * frame + player_speed.load()) / (frame + 1);
        
        // Update lap timer
        float current_time = std::chrono::duration<float>(std::chrono::steady_clock::now().time_since_epoch()).count();
        lap_time = current_time - start_time;
    }
};

void printGameState(int frame) {
    std::cout << "\n=== Race Frame #" << std::setw(3) << frame + 1 << " ===" << std::endl;
    std::cout << std::fixed << std::setprecision(1);
    
    std::cout << "🏎️  Speed: " << player_speed.load() << " km/h";
    if (nitro_active.load()) std::cout << " 💨NITRO";
    std::cout << " | Position: (" << player_x.load() << ", " << player_y.load() << ")" << std::endl;
    
    std::cout << "🏁 Lap: " << current_lap.load() 
              << " | Progress: " << track_completion.load() << "%"
              << " | Time: " << std::setprecision(2) << lap_time.load() << "s" << std::endl;
              
    std::cout << "🏆 Score: " << player_score.load() 
              << " | Rank: #" << position_rank.load()
              << " | Overtakes: " << opponents_passed.load() << std::endl;
              
    std::cout << "⛽ Fuel: " << fuel_level.load() << "%"
              << " | 🛞 Tire Wear: " << tire_wear.load() << "%"
              << " | 🌡️ Engine: " << std::setprecision(1) << engine_temperature.load() << "°C" << std::endl;
              
    std::cout << "⭐ Powerups: " << powerups_collected.load()
              << " | 🔥 Best Lap: " << std::setprecision(2) << best_lap_time.load() << "s"
              << " | Avg Speed: " << std::setprecision(1) << average_speed.load() << " km/h" << std::endl;
              
    if (collision_detected.load()) {
        std::cout << "💥 COLLISION WARNING!" << std::endl;
    }
}

int main() {
    printBanner();
    
    std::cout << "🚀 Initializing Racing Game Engine..." << std::endl;
    std::cout << "🏎️ Starting race simulation with real-time monitoring..." << std::endl;
    std::cout << "📊 Monitoring variables: player_speed, player_x, player_y, player_score, current_lap, fuel_level, tire_wear, engine_temperature" << std::endl;
    
    // Game setup
    std::this_thread::sleep_for(std::chrono::seconds(1));
    
    std::cout << "\n🏁 RACE START! 3... 2... 1... GO!" << std::endl;
    
    RacingGameEngine engine;
    total_races = 1;
    
    for (int frame = 0; frame < 100; ++frame) {
        // Update game state
        engine.updateGameState(frame);
        
        // Print state every 5 frames
        if (frame % 5 == 0) {
            printGameState(frame);
        }
        
        // Stop race if no fuel
        if (fuel_level <= 0.0f) {
            std::cout << "\n⛽ OUT OF FUEL! Race ended." << std::endl;
            break;
        }
        
        // Stop if completed 5 laps
        if (current_lap > 5) {
            std::cout << "\n🏁 RACE COMPLETED! 5 laps finished!" << std::endl;
            break;
        }
        
        // Realistic game frame rate (10 FPS for demo)
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    std::cout << "\n🏆 RACE FINISHED!" << std::endl;
    std::cout << "📊 Final Score: " << player_score.load() << " points" << std::endl;
    std::cout << "🏁 Laps Completed: " << current_lap.load() - 1 << std::endl;
    std::cout << "🔥 Best Lap Time: " << std::setprecision(2) << best_lap_time.load() << "s" << std::endl;
    std::cout << "⭐ Total Powerups: " << powerups_collected.load() << std::endl;
    std::cout << "🏎️ Average Speed: " << std::setprecision(1) << average_speed.load() << " km/h" << std::endl;
    
    return 0;
}