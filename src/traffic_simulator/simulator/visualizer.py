import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Optional

from traffic_simulator.ports.link import Link


class LinkVisualizer:
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
            show_average: Whether to show moving average
        """
        fig, ax = plt.subplots(figsize=fig_size)
        # Plot each link
        for i, link in enumerate(links):
            times, utils = zip(*link.utilization_samples)
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
            all_times.update(t for t, _ in link.utilization_samples)
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
