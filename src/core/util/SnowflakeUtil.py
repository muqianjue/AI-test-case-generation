import time
import threading


class SnowflakeUtil:
    def __init__(self, datacenter_id, worker_id, sequence=0):
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence
        self.twepoch = 1288834974657
        self.datacenter_id_bits = 5
        self.worker_id_bits = 5
        self.sequence_bits = 12
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _gen_timestamp(self):
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def get_id(self):
        with self.lock:
            timestamp = self._gen_timestamp()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id for %d milliseconds" % (
                            self.last_timestamp - timestamp))

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | (
                        self.datacenter_id << self.datacenter_id_shift) | (
                             self.worker_id << self.worker_id_shift) | self.sequence
            return id


# 初始化雪花算法实例
snowflakeUtil = SnowflakeUtil(datacenter_id=1, worker_id=1)
