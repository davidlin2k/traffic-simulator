class MetricsCalculator:
    @staticmethod
    def jains_fairness(loads: list[int]) -> float:
        """
        Calculate Jain's fairness index given a list of server loads.
        Jain's fairness index = (sum(loads)^2) / (n * sum(load^2))
        """
        n = len(loads)
        if n == 0:
            return 1.0
        sum_load = sum(loads)
        sum_sq_load = sum(load ** 2 for load in loads)
        if sum_sq_load == 0:
            return 1.0
        return (sum_load ** 2) / (n * sum_sq_load)
    