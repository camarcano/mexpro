"""
Matplotlib-based pitch location heatmap generator for hitters.

Produces KDE (Kernel Density Estimation) heatmaps showing where batters
are pitched, make contact, or swing. Supports splits by pitcher handedness.
Returns web-optimized PNG images as BytesIO objects.
"""

import matplotlib
matplotlib.use('Agg')

from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.stats import gaussian_kde

from app.extensions import db
from app.models.pitch import Pitch


class HitterHeatmapGenerator:
    """Generates pitch location heatmaps for a given batter."""

    # Strike zone boundaries (feet)
    ZONE_X_MIN = -0.83
    ZONE_X_MAX = 0.83
    ZONE_Y_MIN = 1.5
    ZONE_Y_MAX = 3.5

    # Plot boundaries (feet)
    PLOT_X_MIN = -2.5
    PLOT_X_MAX = 2.5
    PLOT_Y_MIN = 0.0
    PLOT_Y_MAX = 5.0

    # Rendering settings
    FIGURE_SIZE = (4, 4)
    DPI = 100
    GRID_RESOLUTION = 100
    MIN_DATA_POINTS = 5
    COLORMAP = 'YlOrRd'
    BACKGROUND_COLOR = '#f0f0f0'

    def __init__(self, batter_id=None, filters=None, batter_name=None):
        """
        Initialize the heatmap generator.

        Args:
            batter_id: Trackman ID of the batter (can be None for name-based).
            filters: Optional dict with keys 'game_id', 'start_date',
                     'end_date'.
            batter_name: Batter name (used when batter_id is None).
        """
        self.batter_id = batter_id
        self.batter_name = batter_name
        self.filters = filters or {}

    def generate_heatmap(self, split='overall', heatmap_type='pitched'):
        """
        Generate a pitch location heatmap PNG image.

        Args:
            split: One of 'overall', 'vs_lhp', 'vs_rhp'.
            heatmap_type: 'pitched' (all pitches), 'contact' (contact only),
                          'swing' (all swings), or 'whiff' (swing & miss).

        Returns:
            BytesIO object containing the PNG image data.
        """
        data = self._get_pitch_data(split, heatmap_type)

        n = len(data)
        title = f"{self._build_title(split, heatmap_type)} (n={n})"

        if n < self.MIN_DATA_POINTS:
            return self._render_no_data(title)

        x_data = [d[0] for d in data]
        y_data = [d[1] for d in data]

        return self._render_heatmap(x_data, y_data, title)

    def _get_pitch_data(self, split, heatmap_type):
        """
        Query pitch location data from the database.

        Args:
            split: Split type for filtering (vs_lhp, vs_rhp, overall).
            heatmap_type: Type of pitches to include.

        Returns:
            List of (plate_loc_side, plate_loc_height) tuples.
        """
        if self.batter_id is not None:
            batter_filter = Pitch.batter_id == self.batter_id
        else:
            from sqlalchemy import and_
            batter_filter = and_(
                Pitch.batter == self.batter_name,
                Pitch.batter_id.is_(None),
            )

        q = db.session.query(
            Pitch.plate_loc_side,
            Pitch.plate_loc_height
        ).filter(
            batter_filter,
            Pitch.plate_loc_side.isnot(None),
            Pitch.plate_loc_height.isnot(None)
        )

        # Apply split filter
        if split == 'vs_lhp':
            q = q.filter(Pitch.pitcher_throws == 'Left')
        elif split == 'vs_rhp':
            q = q.filter(Pitch.pitcher_throws == 'Right')

        # Apply heatmap type filter
        if heatmap_type == 'contact':
            q = q.filter(Pitch.pitch_call.in_([
                'InPlay', 'FoulBall', 'FoulBallNotFieldable',
                'FoulBallFieldable', 'FoulTip'
            ]))
        elif heatmap_type == 'swing':
            q = q.filter(Pitch.pitch_call.in_([
                'StrikeSwinging', 'FoulBall', 'FoulBallNotFieldable',
                'FoulBallFieldable', 'InPlay', 'FoulTip'
            ]))
        elif heatmap_type == 'whiff':
            q = q.filter(Pitch.pitch_call == 'StrikeSwinging')

        # Apply additional filters
        if self.filters.get('game_id'):
            q = q.filter(Pitch.game_id == self.filters['game_id'])
        if self.filters.get('start_date'):
            q = q.filter(Pitch.date >= self.filters['start_date'])
        if self.filters.get('end_date'):
            q = q.filter(Pitch.date <= self.filters['end_date'])

        rows = q.all()
        return [(row.plate_loc_side, row.plate_loc_height) for row in rows]

    def _build_title(self, split, heatmap_type):
        """Build descriptive title for the heatmap."""
        type_labels = {
            'pitched': 'Pitches',
            'contact': 'Contact',
            'swing': 'Swings',
            'whiff': 'Whiffs'
        }

        split_labels = {
            'overall': 'Overall',
            'vs_lhp': 'vs LHP',
            'vs_rhp': 'vs RHP'
        }

        type_label = type_labels.get(heatmap_type, heatmap_type)
        split_label = split_labels.get(split, split)

        return f"{type_label} - {split_label}"

    def _render_heatmap(self, x_data, y_data, title):
        """
        Render the heatmap using matplotlib KDE.

        Args:
            x_data: List of x coordinates.
            y_data: List of y coordinates.
            title: Title for the plot.

        Returns:
            BytesIO object containing the PNG image.
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE, dpi=self.DPI)

        # Create 2D KDE
        positions = np.vstack([x_data, y_data])
        kernel = gaussian_kde(positions)

        # Create grid
        x_grid = np.linspace(self.PLOT_X_MIN, self.PLOT_X_MAX,
                             self.GRID_RESOLUTION)
        y_grid = np.linspace(self.PLOT_Y_MIN, self.PLOT_Y_MAX,
                             self.GRID_RESOLUTION)
        xx, yy = np.meshgrid(x_grid, y_grid)
        grid_positions = np.vstack([xx.ravel(), yy.ravel()])
        zz = kernel(grid_positions).reshape(xx.shape)

        # Plot heatmap
        ax.contourf(xx, yy, zz, levels=20, cmap=self.COLORMAP, alpha=0.8)

        # Draw strike zone box
        zone_width = self.ZONE_X_MAX - self.ZONE_X_MIN
        zone_height = self.ZONE_Y_MAX - self.ZONE_Y_MIN
        zone_rect = patches.Rectangle(
            (self.ZONE_X_MIN, self.ZONE_Y_MIN),
            zone_width, zone_height,
            linewidth=2, edgecolor='black', facecolor='none'
        )
        ax.add_patch(zone_rect)

        # Formatting
        ax.set_xlim(self.PLOT_X_MIN, self.PLOT_X_MAX)
        ax.set_ylim(self.PLOT_Y_MIN, self.PLOT_Y_MAX)
        ax.set_xlabel('Horizontal Location (ft)', fontsize=10)
        ax.set_ylabel('Vertical Location (ft)', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_facecolor(self.BACKGROUND_COLOR)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        # Save to BytesIO
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=self.DPI, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _render_no_data(self, title):
        """
        Render a placeholder image when there's insufficient data.

        Args:
            title: Title for the plot.

        Returns:
            BytesIO object containing the PNG image.
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE, dpi=self.DPI)

        # Draw strike zone box
        zone_width = self.ZONE_X_MAX - self.ZONE_X_MIN
        zone_height = self.ZONE_Y_MAX - self.ZONE_Y_MIN
        zone_rect = patches.Rectangle(
            (self.ZONE_X_MIN, self.ZONE_Y_MIN),
            zone_width, zone_height,
            linewidth=2, edgecolor='black', facecolor='none'
        )
        ax.add_patch(zone_rect)

        # Add "No Data" text
        ax.text(
            0, 2.5, 'Insufficient Data',
            ha='center', va='center',
            fontsize=14, color='#999', fontweight='bold'
        )

        # Formatting
        ax.set_xlim(self.PLOT_X_MIN, self.PLOT_X_MAX)
        ax.set_ylim(self.PLOT_Y_MIN, self.PLOT_Y_MAX)
        ax.set_xlabel('Horizontal Location (ft)', fontsize=10)
        ax.set_ylabel('Vertical Location (ft)', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_facecolor(self.BACKGROUND_COLOR)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        # Save to BytesIO
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=self.DPI, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
