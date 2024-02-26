import threading
import time
import random

def current_ms():
    """
    Reports the current time in milliseconds
    :return: long int
    """
    return round(time.time() * 1000)

class LoadInjector:
    """
    Abstract class for Injecting Errors in the System probes
    """

    def __init__(self, tag: str = '', duration_ms: float = 1000):
        """
        Constructor
        """
        self.valid = True
        self.tag = tag
        self.duration_ms = duration_ms
        self.inj_thread = None
        self.completed_flag = True
        self.injected_interval = []
        self.init()

    def is_valid(self):
        return self.valid
    
    def init(self):
        """
        Override needed only if the injector needs some pre-setup to be run. Default is an empty method
        :return:
        """
        pass

    def inject_body(self):
        """
        Abstract method to be overridden
        """
        pass

    def inject(self):
        """
        Caller of the body of the injection mechanism, which will be executed in a separate thread
        """
        self.inj_thread = threading.Thread(target=self.inject_body, args=())
        self.inj_thread.start()

    def is_injector_running(self):
        """
        True if the injector has finished working (end of the 'injection_body' function)
        """
        return not self.completed_flag
    
    def force_close(self):
        """
        Try to force-close the injector
        """
        pass

    def get_injections(self) -> list:
        """
        Returns start-end times of injections exercised with this method
        """
        return self.injected_interval

    def get_name(self) -> str:
        """
        Abstract method to be overridden
        """
        return "[" + self.tag + "]Injector" + "(d" + str(self.duration_ms) + ")"

    @classmethod
    def fromJSON(cls, job):
        if job is not None:
            if 'type' in job:
                if job['type'] in {'SSD', 'SSDUsage', 'SolidStateDrive'}:
                    return SSDLoadInjector.fromJSON(job)
                if job['type'] in {'RAM', 'RAMUsage', 'Memory'}:
                    return RAMLoadInjector.fromJSON(job)

        return None

class SSDLoadInjector(LoadInjector):
    """
    Simulates read and write workloads on SSD
    """

    def __init__(self, tag: str = '', duration_ms: float = 1000):
        """
        Constructor
        """
        LoadInjector.__init__(self, tag, duration_ms)

    def inject_body(self):
        """
        Method to simulate read and write workloads on SSD
        """
        self.completed_flag = False
        start_time = current_ms()

        # Simulate read and write workloads on SSD for the specified duration
        while current_ms() - start_time < self.duration_ms:
            # Simulate read workload on SSD
            # You may use external libraries or APIs to simulate read operations on SSD
            time.sleep(random.random() * 0.01)  # Simulate read operation time
            
            # Simulate write workload on SSD
            # You may use external libraries or APIs to simulate write operations on SSD
            time.sleep(random.random() * 0.01)  # Simulate write operation time

        self.injected_interval.append({'start': start_time, 'end': current_ms()})
        self.completed_flag = True

    def get_name(self) -> str:
        """
        Returns the name of the injection
        """
        return "[" + self.tag + "]SSDLoadInjector(d" + str(self.duration_ms) + ")"

    @classmethod
    def fromJSON(cls, job):
        """
        Creates an instance of SSDLoadInjector from a JSON object
        """
        return SSDLoadInjector(tag=(job['tag'] if 'tag' in job else ''),
                                duration_ms=(job['duration_ms'] if 'duration_ms' in job else 1000))

class RAMLoadInjector(LoadInjector):
    """
    Simulates read and write workloads on RAM
    """

    def __init__(self, tag: str = '', duration_ms: float = 1000):
        """
        Constructor
        """
        LoadInjector.__init__(self, tag, duration_ms)

    def inject_body(self):
        """
        Method to simulate read and write workloads on RAM
        """
        self.completed_flag = False
        start_time = current_ms()

        # Simulate read and write workloads on RAM for the specified duration
        while current_ms() - start_time < self.duration_ms:
            # Simulate read workload on RAM
            # You may use external libraries or APIs to simulate read operations on RAM
            time.sleep(random.random() * 0.01)  # Simulate read operation time
            
            # Simulate write workload on RAM
            # You may use external libraries or APIs to simulate write operations on RAM
            time.sleep(random.random() * 0.01)  # Simulate write operation time

        self.injected_interval.append({'start': start_time, 'end': current_ms()})
        self.completed_flag = True

    def get_name(self) -> str:
        """
        Returns the name of the injection
        """
        return "[" + self.tag + "]RAMLoadInjector(d" + str(self.duration_ms) + ")"

    @classmethod
    def fromJSON(cls, job):
        """
        Creates an instance of RAMLoadInjector from a JSON object
        """
        return RAMLoadInjector(tag=(job['tag'] if 'tag' in job else ''),
                                duration_ms=(job['duration_ms'] if 'duration_ms' in job else 1000))
