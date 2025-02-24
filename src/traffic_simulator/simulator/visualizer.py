import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Optional

from traffic_simulator.metrics.metric_manager import LinkMetricsTracker
from traffic_simulator.ports.link import Link


class LinkVisualizer:
    def __init__(self, metrics_tracker: LinkMetricsTracker):
        self.metrics_tracker = metrics_tracker

    def plot_utilization(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot link utilization over time.

        Args:
            links: List of Link objects with utilization samples
            window: Optional time window (start_time, end_time) to plot
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        fig, ax = plt.subplots(figsize=fig_size)
        # Plot each link
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "link_utilization"
            )
            if not samples:
                continue

            times, utils = zip(*samples)
            times = np.array(times)
            utils = np.array(utils)

            # Filter by time window if specified
            if window:
                start_time, end_time = window
                mask = (times >= start_time) & (times <= end_time)
                times = times[mask]
                utils = utils[mask]

            # Plot raw utilization
            ax.plot(times, utils * 100, alpha=0.5, label=f"Link {i + 1} (Raw)")

        # Customize plot
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Utilization (%)")
        ax.set_title("Link Utilization Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.set_ylim(0, 100)

        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save if path provided
        if save_path:
            file_path = save_path + "/utilization.png"
            plt.savefig(file_path, bbox_inches="tight", dpi=300)

        return fig, ax
    
    def plot_max_utilization(
        self,
        links: list[Link],
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot the link utilization's variance over time.

        Args:
            links: List of Link objects with utilization samples
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        fig, ax = plt.subplots(figsize=fig_size)

        # Store the max utilization of each link
        max_utilization = [0 for _ in range(len(links))]

        # Plot each link
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "link_utilization"
            )
            if not samples:
                continue

            _, utils = zip(*samples)
            utils = np.array(utils)

            # Store max utilization for this link
            max_utilization[i] = max(utils) * 100

        # Bar chart for max utilization
        link_labels = [f"Link {i+1}" for i in range(len(links))]
        ax.bar(link_labels, max_utilization, color="steelblue", alpha=0.7)

        # Customize max utilization plot
        ax.set_xlabel("Links")
        ax.set_ylabel("Max Utilization (%)")
        ax.set_title("Max Utilization of Each Link")
        ax.set_ylim(0, 100)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Save if path provided
        if save_path:
            file_path = save_path + "/max_utilization.png"
            plt.savefig(file_path, bbox_inches="tight", dpi=300)

        return fig, ax
    
    def plot_variance(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot the link utilizations variance over time.

        Args:
            links: List of Link objects with utilization samples
            window: Optional time window (start_time, end_time) to plot
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        # Dictionary to store all link's utilization at each time step
        utilization_over_time = {}

        fig, ax = plt.subplots(figsize=fig_size)
        # Plot each link
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "link_utilization"
            )
            if not samples:
                continue

            times, utils = zip(*samples)
            times = np.array(times)
            # Convert to percentage
            utils = np.array(utils) * 100

            # Filter by time window if specified
            if window:
                start_time, end_time = window
                mask = (times >= start_time) & (times <= end_time)
                times = times[mask]
                utils = utils[mask]

            # Store utilization at each timestamp
            for time, util in zip(times, utils):
                if time not in utilization_over_time:
                    utilization_over_time[time] = []
                utilization_over_time[time].append(util)

        # Compute variance at each timestamp
        times_sorted = sorted(utilization_over_time.keys())
        variances = [np.var(utilization_over_time[t]) for t in times_sorted]

        # Find max variance
        max_variance = max(variances) if variances else 0

        # Plot variance over time
        fig, ax = plt.subplots(figsize=fig_size)
        ax.plot(times_sorted, variances, color="red", label="Variance of Link Utilization")
        
        # Highlight max variance with a dashed line
        ax.axhline(y=max_variance, color="black", linestyle="--", alpha=0.8, label=f"Max Variance ({max_variance:.2f}%)")

        # Customize plot
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Variance of Utilization (%)")
        ax.set_title("Variance of Link Utilization Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend()
        plt.tight_layout()

        # Save if path provided
        if save_path:
            plt.savefig(save_path + "/variance_over_time.png", bbox_inches="tight", dpi=300)

        return fig, ax

    def plot_buffer_occupancy(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot buffer occupancy over time.

        Args:
            links: List of Link objects with utilization samples
            window: Optional time window (start_time, end_time) to plot
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        fig, ax = plt.subplots(figsize=fig_size)
        # Plot each link
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "buffer_occupancy"
            )
            if not samples:
                continue

            times, occupancies = zip(*samples)
            times = np.array(times)
            occupancies = np.array(occupancies)

            # Filter by time window if specified
            if window:
                start_time, end_time = window
                mask = (times >= start_time) & (times <= end_time)
                times = times[mask]
                occupancies = occupancies[mask]

            # Plot buffer occupancies
            ax.plot(times, occupancies, alpha=0.5, label=f"Link {i + 1}")

        # Customize plot
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Buffer Occupancy (Bits)")
        ax.set_title("Buffer Occupancy Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)
        # ax.set_ylim(0, 100)

        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save if path provided
        if save_path:
            file_path = save_path + "/buffer_occupancy.png"
            plt.savefig(file_path, bbox_inches="tight", dpi=300)

        return fig, ax

    def plot_utilization_heatmap(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Create a heatmap of link utilization over time.

        Args:
            links: List of Link objects with utilization samples
            window: Optional time window (start_time, end_time) to plot
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        # Prepare data
        all_times = set()
        for link in links:
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "link_utilization"
            )
            all_times.update(t for t, _ in samples)

        times = sorted(all_times)

        # Filter by time window
        if window:
            start_time, end_time = window
            times = [t for t in times if start_time <= t <= end_time]

        # Create utilization matrix
        util_matrix = np.zeros((len(links), len(times)))
        for i, link in enumerate(links):
            time_to_util = dict(link.utilization_samples)
            for j, t in enumerate(times):
                util_matrix[i, j] = time_to_util.get(t, 0) * 100

        # Create heatmap
        fig, ax = plt.subplots(figsize=fig_size)
        im = ax.imshow(
            util_matrix,
            aspect="auto",
            cmap="YlOrRd",
            interpolation="nearest",
            extent=[min(times), max(times), -0.5, len(links) - 0.5],
            vmin=0,
            vmax=100,
        )

        # Customize plot
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Link")
        ax.set_title("Link Utilization Heatmap")

        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label("Utilization (%)")

        # Set y-axis ticks to link numbers
        ax.set_yticks(range(len(links)))
        ax.set_yticklabels([f"Link {i + 1}" for i in range(len(links))])

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, bbox_inches="tight", dpi=300)

        return fig, ax

    def plot_utilization_stats(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot utilization statistics including histogram and box plot.

        Args:
            links: List of Link objects with utilization samples
            window: Optional time window (start_time, end_time) to plot
            fig_size: Figure size in inches (width, height)
            save_path: Optional path to save the figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size)

        # Prepare data
        all_utils = []
        labels = []
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "flow_completion_time"
            )
            if not samples:
                continue

            utils = [u for t, u in link.utilization_samples]
            if window:
                start_time, end_time = window
                utils = [
                    u
                    for t, u in link.utilization_samples
                    if start_time <= t <= end_time
                ]
            all_utils.append(np.array(utils) * 100)
            labels.append(f"Link {i + 1}")

        # Histogram
        for utils, label in zip(all_utils, labels):
            ax1.hist(utils, bins=30, alpha=0.5, label=label)
        ax1.set_xlabel("Utilization (%)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Utilization Distribution")
        ax1.legend()
        ax1.grid(True, linestyle="--", alpha=0.7)

        # Box plot
        ax2.boxplot(all_utils, labels=labels)
        ax2.set_ylabel("Utilization (%)")
        ax2.set_title("Utilization Statistics")
        ax2.grid(True, linestyle="--", alpha=0.7)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, bbox_inches="tight", dpi=300)

        return fig, (ax1, ax2)

    def plot_fct(
        self,
        links: list[Link],
        window: Optional[Tuple[float, float]] = None,
        fig_size: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=fig_size)
        # Plot each link
        for i, link in enumerate(links):
            samples = self.metrics_tracker.get_link_metric_samples(
                link, "flow_completion_time"
            )
            if not samples:
                continue

            times, occupancies = zip(*samples)
            times = np.array(times)
            occupancies = np.array(occupancies)

            # Filter by time window if specified
            if window:
                start_time, end_time = window
                mask = (times >= start_time) & (times <= end_time)
                times = times[mask]
                occupancies = occupancies[mask]

            # Plot buffer occupancies
            ax.plot(times, occupancies, alpha=0.5, label=f"Link {i + 1}")

        # Customize plot
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Average Flow Completion Time (seconds)")
        ax.set_title("Average Flow Completion Time Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)
        # ax.set_ylim(0, 100)

        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save if path provided
        if save_path:
            file_path = save_path + "/fct.png"
            plt.savefig(file_path, bbox_inches="tight", dpi=300)

        return fig, ax
