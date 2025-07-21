import os
from datetime import datetime
import pandas as pd

class TransactionLogger:
    def __init__(self, log_directory="logs"):
        self.log_directory = os.path.abspath(log_directory)
        print(f"DEBUG: Inicjalizuję logger w folderze: {self.log_directory}")
        
        try:
            self.ensure_log_directory()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.transaction_file = os.path.join(self.log_directory, f"transactions_{timestamp}.txt")
            self.performance_file = os.path.join(self.log_directory, f"model_performance_{timestamp}.txt")
            self.daily_portfolio_file = os.path.join(self.log_directory, f"daily_portfolio_{timestamp}.txt")
            
            print(f"DEBUG: Pliki logów:")
            print(f"  - Transakcje: {self.transaction_file}")
            print(f"  - Wydajność: {self.performance_file}")
            print(f"  - Portfolio: {self.daily_portfolio_file}")
            
            self.initialize_files()
            
            self.model_predictions = {}
            self.actual_outcomes = {}
            self.daily_accuracy = {}
            
            print("DEBUG: Logger zainicjalizowany pomyślnie")
            
        except Exception as e:
            print(f"BŁĄD inicjalizacji loggera: {e}")
            raise
        
    def ensure_log_directory(self):
        try:
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)
                print(f"DEBUG: Utworzony folder: {self.log_directory}")
            else:
                print(f"DEBUG: Folder już istnieje: {self.log_directory}")
        except Exception as e:
            print(f"BŁĄD tworzenia folderu {self.log_directory}: {e}")
            raise
    
    def initialize_files(self):
        try:
            print(f"DEBUG: Tworzę plik transakcji: {self.transaction_file}")
            with open(self.transaction_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("TRADING SIMULATOR - LOG TRANSAKCJI\n")
                f.write(f"Utworzony: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.flush()  
                
            print(f"DEBUG: Tworzę plik wydajności: {self.performance_file}")
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("TRADING SIMULATOR - SKUTECZNOŚĆ MODELU\n")
                f.write(f"Utworzony: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.flush()
                
            print(f"DEBUG: Tworzę plik portfolio: {self.daily_portfolio_file}")
            with open(self.daily_portfolio_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("TRADING SIMULATOR - DZIENNY STAN PORTFOLIO\n")
                f.write(f"Utworzony: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.flush()
                
            print("DEBUG: Wszystkie pliki utworzone pomyślnie")
            
        except Exception as e:
            print(f"BŁĄD tworzenia plików: {e}")
            raise
    
    def log_transaction(self, date, ticker, action, shares, price, commission, total_amount, success=True):
        try:
            print(f"DEBUG: Loguję transakcję: {action} {ticker} {shares} akcji po ${price}")
            with open(self.transaction_file, 'a', encoding='utf-8') as f:
                status = "SUKCES" if success else "BŁĄD"
                f.write(f"[{date}] {status} - {action}\n")
                f.write(f"  Ticker: {ticker}\n")
                f.write(f"  Akcje: {shares}\n")
                f.write(f"  Cena: ${price:.2f}\n")
                f.write(f"  prowizja: ${commission:.2f}\n")
                f.write(f"  Łączna kwota: ${total_amount:.2f}\n")
                f.write("-" * 50 + "\n\n")
                f.flush()
            print("DEBUG: Transakcja zalogowana pomyślnie")
        except Exception as e:
            print(f"BŁĄD logowania transakcji: {e}")
    
    def log_prediction(self, date, ticker, prediction, actual_price_change=None):
        try:
            print(f"DEBUG: Loguję przewidywanie: {ticker} prediction={prediction}")
            
            if ticker not in self.model_predictions:
                self.model_predictions[ticker] = []
                self.actual_outcomes[ticker] = []
            
            self.model_predictions[ticker].append({
                'date': date,
                'prediction': prediction
            })
            
            if actual_price_change is not None:
                actual_outcome = 1 if actual_price_change > 0 else 0
                self.actual_outcomes[ticker].append({
                    'date': date,
                    'actual': actual_outcome,
                    'price_change': actual_price_change
                })
                
            print("DEBUG: Przewidywanie zalogowane pomyślnie")
        except Exception as e:
            print(f"BŁĄD logowania przewidywania: {e}")
    
    def log_daily_portfolio(self, date, portfolio_summary, predictions):
        try:
            print(f"DEBUG: Loguję dzienny stan portfolio na {date}")
            with open(self.daily_portfolio_file, 'a', encoding='utf-8') as f:
                f.write(f"[{date}]\n")
                f.write(f"Gotówka: ${portfolio_summary['cash']:,.2f}\n")
                f.write(f"Wartość całkowita: ${portfolio_summary['total_value']:,.2f}\n")
                f.write(f"Zwrot całkowity: ${portfolio_summary['total_return']:,.2f} ({portfolio_summary['return_percentage']:.2f}%)\n")
                f.write("\nPozycje:\n")
                
                if portfolio_summary['positions']:
                    for pos in portfolio_summary['positions']:
                        f.write(f"  {pos['ticker']}: {pos['shares']} akcji @ ${pos['avg_price']:.2f} "
                               f"(Obecna: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pnl']:,.2f})\n")
                else:
                    f.write("  Brak pozycji\n")
                    
                f.write("\nPrzewidywania:\n")
                for ticker, prediction in predictions.items():
                    signal = "BUY" if prediction == 1 else "HOLD/SELL"
                    f.write(f"  {ticker}: {signal} (wartość: {prediction})\n")
                
                f.write("-" * 60 + "\n\n")
                f.flush()
            print("DEBUG: Dzienny stan portfolio zalogowany pomyślnie")
        except Exception as e:
            print(f"BŁĄD logowania dziennego portfolio: {e}")
    
    def calculate_model_accuracy(self, ticker):
        if (ticker not in self.model_predictions or 
            ticker not in self.actual_outcomes or
            len(self.actual_outcomes[ticker]) == 0):
            return None
        
        predictions = self.model_predictions[ticker]
        actuals = self.actual_outcomes[ticker]
        
        if len(predictions) != len(actuals):
            min_len = min(len(predictions), len(actuals))
            predictions = predictions[:min_len]
            actuals = actuals[:min_len]
        
        correct_predictions = 0
        total_predictions = len(predictions)
        
        for i in range(total_predictions):
            if predictions[i]['prediction'] == actuals[i]['actual']:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct_predictions,
            'total': total_predictions,
            'wrong': total_predictions - correct_predictions
        }
    
    def log_model_performance_summary(self):
        with open(self.performance_file, 'a', encoding='utf-8') as f:
            f.write(f"\nPODSUMOWANIE SKUTECZNOŚCI MODELU - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            
            overall_correct = 0
            overall_total = 0
            
            for ticker in self.model_predictions.keys():
                accuracy_data = self.calculate_model_accuracy(ticker)
                
                if accuracy_data:
                    f.write(f"\n{ticker}:\n")
                    f.write(f"  Dokładność: {accuracy_data['accuracy']:.2f}%\n")
                    f.write(f"  Poprawne przewidywania: {accuracy_data['correct']}\n")
                    f.write(f"  Błędne przewidywania: {accuracy_data['wrong']}\n")
                    f.write(f"  Łączne przewidywania: {accuracy_data['total']}\n")
                    
                    overall_correct += accuracy_data['correct']
                    overall_total += accuracy_data['total']
                else:
                    f.write(f"\n{ticker}: Brak danych do oceny\n")
            
            if overall_total > 0:
                overall_accuracy = (overall_correct / overall_total) * 100
                f.write(f"\nOGÓŁEM:\n")
                f.write(f"  Dokładność ogólna: {overall_accuracy:.2f}%\n")
                f.write(f"  Poprawne przewidywania: {overall_correct}\n")
                f.write(f"  Błędne przewidywania: {overall_total - overall_correct}\n")
                f.write(f"  Łączne przewidywania: {overall_total}\n")
            
            f.write("\n" + "=" * 60 + "\n")
    
    def update_actual_outcome(self, ticker, date, price_change):
        if ticker in self.actual_outcomes:
            for i, pred in enumerate(self.model_predictions[ticker]):
                if pred['date'] == date and i < len(self.actual_outcomes[ticker]):
                    actual_outcome = 1 if price_change > 0 else 0
                    self.actual_outcomes[ticker][i] = {
                        'date': date,
                        'actual': actual_outcome,
                        'price_change': price_change
                    }
                    break
    
    def finalize_logs(self, final_portfolio_summary):
        self.log_model_performance_summary()
        
        with open(self.daily_portfolio_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("KOŃCOWE PODSUMOWANIE PORTFOLIO\n")
            f.write("=" * 80 + "\n")
            f.write(f"Końcowa wartość portfolio: ${final_portfolio_summary['total_value']:,.2f}\n")
            f.write(f"Całkowity zwrot: ${final_portfolio_summary['total_return']:,.2f}\n")
            f.write(f"Procentowy zwrot: {final_portfolio_summary['return_percentage']:.2f}%\n")
            f.write("=" * 80 + "\n")
        
        with open(self.transaction_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("SYMULACJA ZAKOŃCZONA\n")
            f.write(f"Data zakończenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")