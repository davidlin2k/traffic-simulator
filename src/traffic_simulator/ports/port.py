from traffic_simulator.models import Flow


class Port:
    id: int
    max_capacity: float
    target_utilization: float
    buffer: list[Flow]

    # to keep track of what traffic we processed in the time window for our calculation of link utilization
    current_flows_in_time_window: list[Flow]
    time_window_duration: float = 0.0

    def __init__(
        self,
        id: int,
        max_capacity: float,
        time_window_duration: float,
        target_utilization: float,
    ):
        self.id = id
        self.max_capacity = max_capacity
        self.buffer = []
        self.current_flows_in_time_window = []
        self.time_window_duration = time_window_duration
        self.target_utilization = target_utilization

    def get_current_utilization(self, current_time: float) -> float:
        # tried keeping track of usage in the current_flows_in_time_window and then updating that every time we process_flow
        # so don't have to go through all flows here, but did not work.
        self.update_flows(current_time)

        total_time = 0.0
        for flow in self.current_flows_in_time_window:
            total_time += min(flow.processing_end_time, current_time) - max(
                flow.processing_start_time, current_time - self.time_window_duration
            )

        return total_time / min(self.time_window_duration, current_time)

    def add_flow(self, flow: Flow) -> None:
        self.buffer.append(flow)

    def update_flows(self, current_time: float) -> None:
        # Step 1: Remove expired flows
        self.current_flows_in_time_window = [
            flow
            for flow in self.current_flows_in_time_window
            if flow.processing_end_time > current_time - self.time_window_duration
        ]

        # Step 2: Move flows from buffer to current_flows_in_time_window
        while self.buffer:
            flow = self.buffer[0]

            # next start time is earliest possible time
            next_start_time = flow.arrival_time
            if (
                self.current_flows_in_time_window
                and self.current_flows_in_time_window[-1].processing_end_time
                > flow.arrival_time
            ):
                next_start_time = self.current_flows_in_time_window[
                    -1
                ].processing_end_time

            if next_start_time < current_time:
                flow.processing_start_time = next_start_time
                flow.processing_end_time = flow.processing_start_time + (
                    flow.flow_size / self.max_capacity
                )
                self.current_flows_in_time_window.append(flow)
                self.buffer.pop(0)
            else:
                break
