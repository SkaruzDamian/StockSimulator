"""
Skrypt uruchamiający wszystkie testy dla symulatora giełdowego
Autor: Damian Skaruz
Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego

Uruchomienie: python run_all_tests.py
"""

import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_test_suite():
 
    
    loader = unittest.TestLoader()
    
    suite = unittest.TestSuite()
    
    print("=" * 70)
    print("ŁADOWANIE TESTÓW JEDNOSTKOWYCH")
    print("=" * 70)
    
    from test_portfolio_manager import (
        TestPortfolioManagerInitialization,
        TestPortfolioManagerBuyOperations,
        TestPortfolioManagerSellOperations,
        TestPortfolioManagerPortfolioValue,
        TestPortfolioManagerTransactionHistory,
        TestPortfolioManagerEdgeCases
    )
    
    from test_data_processor import (
        TestDataProcessorInitialization,
        TestDataProcessorTechnicalIndicators,
        TestDataProcessorTargetCreation,
        TestDataProcessorDataSplit,
        TestDataProcessorEdgeCases
    )
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerBuyOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerSellOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerPortfolioValue))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerTransactionHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioManagerEdgeCases))
    
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorTechnicalIndicators))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorTargetCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorDataSplit))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorEdgeCases))
    
    print(f"Załadowano {suite.countTestCases()} testów jednostkowych")
    
    print("\n" + "=" * 70)
    print("ŁADOWANIE TESTÓW INTEGRACYJNYCH")
    print("=" * 70)
    
    from test_integration import (
        TestTradingSimulatorIntegration,
        TestDataProcessorPortfolioIntegration,
        TestModelTrainingPredictionIntegration,
        TestEndToEndSimulation
    )
    
    suite.addTests(loader.loadTestsFromTestCase(TestTradingSimulatorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessorPortfolioIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestModelTrainingPredictionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndSimulation))
    
    integration_count = (
        loader.loadTestsFromTestCase(TestTradingSimulatorIntegration).countTestCases() +
        loader.loadTestsFromTestCase(TestDataProcessorPortfolioIntegration).countTestCases() +
        loader.loadTestsFromTestCase(TestModelTrainingPredictionIntegration).countTestCases() +
        loader.loadTestsFromTestCase(TestEndToEndSimulation).countTestCases()
    )
    print(f"Załadowano {integration_count} testów integracyjnych")
    
    print("\n" + "=" * 70)
    print("ŁADOWANIE TESTÓW FUNKCJONALNYCH")
    print("=" * 70)
    
    from test_functional import (
        TestRequirement_4_1_1_SystemConfiguration,
        TestRequirement_4_1_2_FeatureSelection,
        TestRequirement_4_1_3_TechnicalIndicators,
        TestRequirement_4_1_4_ManualSimulation,
        TestRequirement_4_1_7_PortfolioVisualization,
        TestRequirement_4_1_9_PerformanceMetrics,
        TestRequirement_4_2_1_Responsiveness,
        TestRequirement_4_2_3_Reliability
    )
    
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_1_SystemConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_2_FeatureSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_3_TechnicalIndicators))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_4_ManualSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_7_PortfolioVisualization))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_1_9_PerformanceMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_2_1_Responsiveness))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirement_4_2_3_Reliability))
    
    functional_count = (
        loader.loadTestsFromTestCase(TestRequirement_4_1_1_SystemConfiguration).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_1_2_FeatureSelection).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_1_3_TechnicalIndicators).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_1_4_ManualSimulation).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_1_7_PortfolioVisualization).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_1_9_PerformanceMetrics).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_2_1_Responsiveness).countTestCases() +
        loader.loadTestsFromTestCase(TestRequirement_4_2_3_Reliability).countTestCases()
    )
    print(f"Załadowano {functional_count} testów funkcjonalnych")

    # Podsumowanie
    print("\n" + "=" * 70)
    print(f"ŁĄCZNIE ZAŁADOWANO {suite.countTestCases()} TESTÓW")
    print("=" * 70)
    print()
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("PODSUMOWANIE WYNIKÓW TESTÓW")
    print("=" * 70)
    print(f"Wykonano testów: {result.testsRun}")
    print(f"Sukcesy: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Błędy: {len(result.errors)}")
    print(f"Niepowodzenia: {len(result.failures)}")
    print(f"Pominięte: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ WSZYSTKIE TESTY ZAKOŃCZONE SUKCESEM")
    else:
        print("\n✗ NIEKTÓRE TESTY NIE POWIODŁY SIĘ")
    
    print("=" * 70)
    
    return result


def generate_test_report(result, output_file='test_report.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RAPORT Z TESTÓW SYMULATORA GIEŁDOWEGO\n")
        f.write(f"Data wykonania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Wykonano testów: {result.testsRun}\n")
        f.write(f"Sukcesy: {result.testsRun - len(result.failures) - len(result.errors)}\n")
        f.write(f"Błędy: {len(result.errors)}\n")
        f.write(f"Niepowodzenia: {len(result.failures)}\n")
        f.write(f"Pominięte: {len(result.skipped)}\n\n")
        
        if result.failures:
            f.write("NIEPOWODZENIA:\n")
            f.write("-" * 70 + "\n")
            for test, traceback in result.failures:
                f.write(f"\n{test}:\n")
                f.write(traceback)
                f.write("\n")
        
        if result.errors:
            f.write("BŁĘDY:\n")
            f.write("-" * 70 + "\n")
            for test, traceback in result.errors:
                f.write(f"\n{test}:\n")
                f.write(traceback)
                f.write("\n")
        
        if result.wasSuccessful():
            f.write("\n✓ WSZYSTKIE TESTY ZAKOŃCZONE SUKCESEM\n")
        else:
            f.write("\n✗ NIEKTÓRE TESTY NIE POWIODŁY SIĘ\n")
    
    print(f"\nRaport zapisany do pliku: {output_file}")


if __name__ == '__main__':
    print("\n")
    print("*" * 70)
    print("URUCHAMIANIE TESTÓW SYMULATORA GIEŁDOWEGO")
    print("Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego")
    print("Autor: Damian Skaruz")
    print("*" * 70)
    print("\n")
   
    result = run_test_suite()
    
    generate_test_report(result)
    

    sys.exit(0 if result.wasSuccessful() else 1)