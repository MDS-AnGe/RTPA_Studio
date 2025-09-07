#!/usr/bin/env python3
"""
Tests de performance et benchmarks pour RTPA Studio
Mesure les temps de réponse et l'utilisation des ressources
"""

import time
import psutil
import threading
from src.core.app_manager import RTAPStudioManager
from src.algorithms.cfr_engine import CFREngine
from src.database.memory_db import MemoryDatabase
from src.core.app_manager import GameState

class PerformanceBenchmark:
    """Benchmark de performance du système RTPA"""
    
    def __init__(self):
        self.results = {}
        self.app_manager = RTAPStudioManager()
        
    def benchmark_cfr_speed(self, iterations=1000):
        """Benchmark vitesse calculs CFR"""
        print("🧠 Test vitesse CFR...")
        
        game_state = GameState(
            hero_cards=("As", "Kh"),
            board_cards=("Ah", "Kd", "7c"),
            pot_size=100.0,
            hero_stack=500.0
        )
        
        start_time = time.time()
        for i in range(iterations):
            recommendation = self.app_manager.cfr_engine.get_recommendation(game_state)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        self.results['cfr_speed'] = {
            'total_time': total_time,
            'avg_time_ms': avg_time * 1000,
            'iterations': iterations,
            'req_per_sec': iterations / total_time
        }
        
        print(f"  ✅ {iterations} recommandations en {total_time:.2f}s")
        print(f"  ✅ Temps moyen: {avg_time*1000:.1f}ms")
        print(f"  ✅ Débit: {iterations/total_time:.1f} req/sec")
        
    def benchmark_database_speed(self, operations=5000):
        """Benchmark vitesse base de données"""
        print("💾 Test vitesse base de données...")
        
        db = MemoryDatabase()
        
        # Test écriture
        start_time = time.time()
        for i in range(operations):
            game_state = GameState(
                hero_cards=("As", "Kh"),
                pot_size=float(100 + i),
                hero_stack=float(500 + i)
            )
            recommendation = {
                'action_type': 'bet',
                'bet_size': 50.0,
                'timestamp': time.time()
            }
            db.store_recommendation(recommendation)
        
        write_time = time.time() - start_time
        
        # Test lecture
        start_time = time.time()
        for i in range(operations):
            recent = db.get_recent_recommendations(10)
        read_time = time.time() - start_time
        
        self.results['database_speed'] = {
            'write_ops': operations,
            'write_time': write_time,
            'write_ops_per_sec': operations / write_time,
            'read_ops': operations,
            'read_time': read_time,
            'read_ops_per_sec': operations / read_time
        }
        
        print(f"  ✅ Écriture: {operations/write_time:.0f} ops/sec")
        print(f"  ✅ Lecture: {operations/read_time:.0f} ops/sec")
        
    def benchmark_memory_usage(self, duration=10):
        """Benchmark utilisation mémoire"""
        print("🧠 Test utilisation mémoire...")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        max_memory = initial_memory
        
        # Simulation charge de travail
        start_time = time.time()
        while time.time() - start_time < duration:
            # Simulation calculs CFR
            for i in range(10):
                game_state = GameState(
                    hero_cards=("As", "Kh"),
                    board_cards=("Ah", "Kd", "7c"),
                    pot_size=float(100 + i),
                    hero_stack=float(500 + i)
                )
                recommendation = self.app_manager.cfr_engine.get_recommendation(game_state)
            
            # Mesure mémoire
            current_memory = process.memory_info().rss
            max_memory = max(max_memory, current_memory)
            
            time.sleep(0.1)
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        peak_usage = max_memory - initial_memory
        
        self.results['memory_usage'] = {
            'initial_mb': initial_memory / 1024 / 1024,
            'final_mb': final_memory / 1024 / 1024,
            'growth_mb': memory_growth / 1024 / 1024,
            'peak_mb': peak_usage / 1024 / 1024
        }
        
        print(f"  ✅ Mémoire initiale: {initial_memory/1024/1024:.1f} MB")
        print(f"  ✅ Croissance mémoire: {memory_growth/1024/1024:.1f} MB")
        print(f"  ✅ Pic d'utilisation: {peak_usage/1024/1024:.1f} MB")
        
    def benchmark_concurrent_load(self, threads=5, duration=5):
        """Benchmark charge concurrente"""
        print(f"⚡ Test charge concurrente ({threads} threads)...")
        
        results = {'completed': 0, 'errors': 0}
        
        def worker():
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    game_state = GameState(
                        hero_cards=("Qd", "Qs"),
                        board_cards=("9h", "3c", "2s"),
                        pot_size=200.0,
                        hero_stack=800.0
                    )
                    recommendation = self.app_manager.cfr_engine.get_recommendation(game_state)
                    results['completed'] += 1
                except Exception as e:
                    results['errors'] += 1
                
                time.sleep(0.01)
        
        # Lancement des threads
        worker_threads = []
        start_time = time.time()
        
        for i in range(threads):
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            worker_threads.append(thread)
        
        # Attendre completion
        for thread in worker_threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        self.results['concurrent_load'] = {
            'threads': threads,
            'duration': total_time,
            'completed_ops': results['completed'],
            'errors': results['errors'],
            'ops_per_sec': results['completed'] / total_time,
            'success_rate': results['completed'] / (results['completed'] + results['errors']) if (results['completed'] + results['errors']) > 0 else 0
        }
        
        print(f"  ✅ Opérations réussies: {results['completed']}")
        print(f"  ✅ Erreurs: {results['errors']}")
        print(f"  ✅ Débit: {results['completed']/total_time:.1f} ops/sec")
        print(f"  ✅ Taux de succès: {results['completed']/(results['completed']+results['errors'])*100:.1f}%")
        
    def run_all_benchmarks(self):
        """Exécute tous les benchmarks"""
        print("🚀 BENCHMARKS PERFORMANCE RTPA STUDIO")
        print("=" * 50)
        
        self.benchmark_cfr_speed(500)
        print()
        
        self.benchmark_database_speed(2000)
        print()
        
        self.benchmark_memory_usage(5)
        print()
        
        self.benchmark_concurrent_load(3, 3)
        print()
        
        self.print_summary()
        
    def print_summary(self):
        """Affiche un résumé des performances"""
        print("📊 RÉSUMÉ PERFORMANCES")
        print("-" * 30)
        
        if 'cfr_speed' in self.results:
            cfr = self.results['cfr_speed']
            status = "✅ EXCELLENT" if cfr['avg_time_ms'] < 100 else "⚠️ ACCEPTABLE" if cfr['avg_time_ms'] < 500 else "❌ LENT"
            print(f"CFR: {cfr['avg_time_ms']:.1f}ms/req - {status}")
        
        if 'database_speed' in self.results:
            db = self.results['database_speed']
            write_status = "✅ RAPIDE" if db['write_ops_per_sec'] > 1000 else "⚠️ MOYEN" if db['write_ops_per_sec'] > 500 else "❌ LENT"
            print(f"Base: {db['write_ops_per_sec']:.0f} écr/sec - {write_status}")
        
        if 'memory_usage' in self.results:
            mem = self.results['memory_usage']
            mem_status = "✅ STABLE" if mem['growth_mb'] < 50 else "⚠️ CROISSANCE" if mem['growth_mb'] < 100 else "❌ FUITE"
            print(f"Mémoire: +{mem['growth_mb']:.1f}MB - {mem_status}")
        
        if 'concurrent_load' in self.results:
            conc = self.results['concurrent_load']
            conc_status = "✅ STABLE" if conc['success_rate'] > 0.95 else "⚠️ INSTABLE" if conc['success_rate'] > 0.9 else "❌ PROBLÈME"
            print(f"Concurrence: {conc['success_rate']*100:.1f}% succès - {conc_status}")

if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()