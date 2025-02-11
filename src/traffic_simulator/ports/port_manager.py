from traffic_simulator.models import Flow
from traffic_simulator.ports.port_assigner import PortAssigner
from traffic_simulator.ports.port import Port


class PortManager:
    def __init__(self, ports: list[Port], port_assigner: PortAssigner):
        self.ports = ports
        self.port_assigner = port_assigner

    def add_port(self, port: Port) -> None:
        self.ports.append(port)

    def get_port_utilization(self, port_id: int, current_time: float) -> float:
        port = self._find_port_by_id(port_id)
        return port.get_current_utilization(current_time)

    def add_flow(self, flow: Flow) -> None:
        port = self.port_assigner.assign_port(flow)
        port.add_flow(flow)

    def process_flows(self, current_time: float) -> None:
        for port in self.ports:
            port.process_flows(current_time)

    def _find_port_by_id(self, port_id: int) -> Port:
        if len(self.ports) > port_id:
            return self.ports[port_id]
        raise ValueError(f"Port with id {port_id} not found")
