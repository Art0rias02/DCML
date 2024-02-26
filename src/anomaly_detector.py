import datetime
import pathlib
import pandas as pd
import time
import sys
import traceback
from main_monitor_injector import monitor_system
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from joblib import load

class SystemMonitorInjector:
    """
    Class for monitoring the system and detecting anomalies using a machine learning model.
    """

    def __init__(self, warning_threshold: int = 5):
        """
        Constructor.
        """
        self.warning_threshold = warning_threshold
        self.random_forest = load(str(pathlib.Path(__file__).parent.resolve()) + '/random_forest.bin')
        self.standard_scaler = load(str(pathlib.Path(__file__).parent.resolve()) + '/standard_scaler.bin')
        self.warning_level = 0
        self.last_printed_length = 0
        self.to_remove = 1
        self.warning_log = open(str(pathlib.Path(__file__).parent.resolve()) + '/warnings.log', 'w')
        self.raw_predictions_log = open(str(pathlib.Path(__file__).parent.resolve()) + '/raw_predictions.log', 'w')

    def _detect_anomaly(self, monitored_data):
        """
        Detects anomalies in monitored data using a machine learning model.
        """
        cols_to_drop = ['0irq', '0steal', '0guest', '0guest_nice', '0iowait',
                        '1irq', '1steal', '1guest', '1guest_nice', '1iowait',
                        '2irq', '2steal', '2guest', '2guest_nice', '2iowait',
                        '3irq', '3steal', '3guest', '3guest_nice', '3iowait',
                        '0min', '0max', '1min', '1max', '2min', '2max', '3min', '3max',
                        'time_s', 'virtual_total']
        monitored_data = pd.DataFrame([monitored_data]).drop(columns=cols_to_drop)
        X = self.standard_scaler.transform(monitored_data)
        is_anomaly = (self.random_forest.predict(X)[0] == 1)
        self.raw_predictions_log.write(f"[{datetime.datetime.now()}] Monitored: ({monitored_data.to_string(header=False)})" +
                                       f"- Prediction: {'ANOMALY!' if is_anomaly else 'Normal'}" +
                                       f" with prob. {self.random_forest.predict_proba(X)[0][1 if is_anomaly else 0]:4.2f}\n")
        return is_anomaly

    def _log_warning(self, warning_level):
        """
        Logs warning information.
        """
        to_print = f'[{datetime.datetime.now()}] ' + f'WARNING!!! (Level {warning_level})'
        self.warning_log.write(to_print + '\n')
        self.last_printed_length = len(to_print)

    def _check_and_print_warning(self):
        """
        Checks the warning level and prints the warning if necessary.
        """
        if self.warning_level > self.warning_threshold:
            self._log_warning(self.warning_level)
        else:
            to_print = ' ' * (self.last_printed_length + 1)  # overwrite the previous warning (if any)
            self.last_printed_length = 0
            print(to_print, end='\r', flush=True)

    def monitor_and_detect(self):
        """
        Monitors the system and detects anomalies.
        """
        try:
            while True:
                monitored_data = monitor_system()
                is_anomaly = self._detect_anomaly(monitored_data)

                if is_anomaly:
                    self.warning_level += 1
                    self.to_remove = 1
                else:
                    self.warning_level = max(self.warning_level - self.to_remove, 0)
                    self.to_remove = self.to_remove * 2 if self.warning_level > 0 else 1

                self._check_and_print_warning()
                time.sleep(0.5)
        except Exception as e:
            print(traceback.format_exc())
            self.warning_log.close()
            self.raw_predictions_log.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        SystemMonitorInjector(int(sys.argv[1])).monitor_and_detect()
    else:
        SystemMonitorInjector().monitor_and_detect()
