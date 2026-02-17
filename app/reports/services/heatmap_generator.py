"""
Matplotlib-based pitch location heatmap generator.

Produces KDE (Kernel Density Estimation) heatmaps of pitch locations
for a given pitcher, with support for splits by batter handedness and
pitch type. Returns web-optimized PNG images as BytesIO objects.
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


class HeatmapGenerator:
    """Generates pitch location heatmaps for a given pitcher."""

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

    def __init__(self, pitcher_id=None, filters=None, pitcher_name=None):
        """
        Initialize the heatmap generator.

        Args:
            pitcher_id: Trackman ID of the pitcher (can be None for name-based).
            filters: Optional dict with keys 'game_id', 'start_date', 'end_date'.
            pitcher_name: Pitcher name (used when pitcher_id is None).
        """
        self.pitcher_id = pitcher_id
        self.pitcher_name = pitcher_name
        self.filters = filters or {}

    def generate_heatmap(self, split='overall'):
        """
        Generate a pitch location heatmap PNG image.

        Args:
            split: One of 'overall', 'vs_lhh', 'vs_rhh', or a pitch type
                   string (e.g. 'Four-Seam', 'Slider').

        Returns:
            BytesIO object containing the PNG image data.
        """
        data = self._get_pitch_data(split)

        n = len(data)
        title = f"{self._build_title(split)} (n={n})"

        if n < self.MIN_DATA_POINTS:
            return self._render_no_data(title)

        x_data = [d[0] for d in data]
        y_data = [d[1] for d in data]

        return self._render_heatmap(x_data, y_data, title)

    def _get_pitch_data(self, split):
        """
        Query pitch location data from the database.

        Args:
            split: Split type for filtering.

        Returns:
            List of (plate_loc_side, plate_loc_height) tuples.
        """
        if self.pitcher_id is not None:
            pitcher_filter = Pitch.pitcher_id == self.pitcher_id
        else:
            from sqlalchemy import and_
            pitcher_filter = and_(
                Pitch.pitcher == self.pitcher_name,
                Pitch.pitcher_id.is_(None),
            )

        query = Pitch.query.filter(
            pitcher_filter,
            Pitch.plate_loc_side.isnot(None),
            Pitch.plate_loc_height.isnot(None),
        )

        # Apply split filters
        if split == 'vs_lhh':
            query = query.filter(Pitch.batter_side == 'Left')
        elif split == 'vs_rhh':
            query = query.filter(Pitch.batter_side == 'Right')
        elif split not in ('overall',):
            # Treat as pitch type filter (check both tagged and auto)
            from sqlalchemy import or_
            query = query.filter(or_(
                Pitch.tagged_pitch_type == split,
                Pitch.auto_pitch_type == split,
            ))

        # Apply optional filters
        if 'game_id' in self.filters:
            query = query.filter(Pitch.game_id == self.filters['game_id'])
        if 'start_date' in self.filters:
            query = query.filter(Pitch.date >= self.filters['start_date'])
        if 'end_date' in self.filters:
            query = query.filter(Pitch.date <= self.filters['end_date'])

        rows = query.with_entities(
            Pitch.plate_loc_side,
            Pitch.plate_loc_height,
        ).all()

        return [(row.plate_loc_side, row.plate_loc_height) for row in rows]

    def _render_heatmap(self, x_data, y_data, title):
        """
        Create a KDE heatmap and return it as a PNG in a BytesIO buffer.

        Args:
            x_data: List of horizontal plate locations (feet).
            y_data: List of vertical plate locations (feet).
            title: Title string for the plot.

        Returns:
            BytesIO object containing the PNG image data.
        """
        try:
            fig, ax = plt.subplots(
                figsize=self.FIGURE_SIZE,
                dpi=self.DPI,
            )
            fig.patch.set_facecolor(self.BACKGROUND_COLOR)
            ax.set_facecolor(self.BACKGROUND_COLOR)

            # Build KDE
            xy = np.vstack([x_data, y_data])
            kde = gaussian_kde(xy)

            # Evaluate on grid
            x_grid = np.linspace(self.PLOT_X_MIN, self.PLOT_X_MAX, self.GRID_RESOLUTION)
            y_grid = np.linspace(self.PLOT_Y_MIN, self.PLOT_Y_MAX, self.GRID_RESOLUTION)
            xx, yy = np.meshgrid(x_grid, y_grid)
            positions = np.vstack([xx.ravel(), yy.ravel()])
            zz = np.reshape(kde(positions), xx.shape)

            # Render density
            ax.imshow(
                zz,
                origin='lower',
                aspect='auto',
                extent=[self.PLOT_X_MIN, self.PLOT_X_MAX,
                        self.PLOT_Y_MIN, self.PLOT_Y_MAX],
                cmap=self.COLORMAP,
            )

            # Strike zone overlay
            self._draw_strike_zone(ax)

            # Home plate pentagon
            self._draw_home_plate(ax)

            # Labels and title
            ax.set_xlim(self.PLOT_X_MIN, self.PLOT_X_MAX)
            ax.set_ylim(self.PLOT_Y_MIN, self.PLOT_Y_MAX)
            ax.set_xlabel('Horizontal Location (ft)')
            ax.set_ylabel('Height (ft)')
            ax.set_title(title)

            fig.tight_layout()

            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=self.DPI)
            buf.seek(0)
            return buf
        finally:
            plt.close('all')

    def _render_no_data(self, title):
        """
        Render a placeholder image when there are fewer than MIN_DATA_POINTS.

        Args:
            title: Title string for the plot.

        Returns:
            BytesIO object containing the placeholder PNG image.
        """
        try:
            fig, ax = plt.subplots(
                figsize=self.FIGURE_SIZE,
                dpi=self.DPI,
            )
            fig.patch.set_facecolor(self.BACKGROUND_COLOR)
            ax.set_facecolor(self.BACKGROUND_COLOR)

            ax.set_xlim(self.PLOT_X_MIN, self.PLOT_X_MAX)
            ax.set_ylim(self.PLOT_Y_MIN, self.PLOT_Y_MAX)

            ax.text(
                0, 2.5,
                'No data',
                ha='center', va='center',
                fontsize=16, color='#666666',
            )

            self._draw_strike_zone(ax)
            self._draw_home_plate(ax)

            ax.set_xlabel('Horizontal Location (ft)')
            ax.set_ylabel('Height (ft)')
            ax.set_title(title)

            fig.tight_layout()

            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=self.DPI)
            buf.seek(0)
            return buf
        finally:
            plt.close('all')

    def _draw_strike_zone(self, ax):
        """Draw the strike zone as a white dashed rectangle."""
        zone = patches.Rectangle(
            (self.ZONE_X_MIN, self.ZONE_Y_MIN),
            self.ZONE_X_MAX - self.ZONE_X_MIN,
            self.ZONE_Y_MAX - self.ZONE_Y_MIN,
            linewidth=2,
            edgecolor='white',
            facecolor='none',
            linestyle='--',
        )
        ax.add_patch(zone)

    def _draw_home_plate(self, ax):
        """Draw home plate as a small pentagon at the bottom of the plot."""
        plate_vertices = np.array([
            [-0.25, 0.1],
            [0.25, 0.1],
            [0.25, 0.2],
            [0.0, 0.35],
            [-0.25, 0.2],
        ])
        plate = patches.Polygon(
            plate_vertices,
            closed=True,
            edgecolor='white',
            facecolor='#cccccc',
            linewidth=1,
        )
        ax.add_patch(plate)

    def _build_title(self, split):
        """
        Build a human-readable title for the given split.

        Args:
            split: The split identifier.

        Returns:
            Title string.
        """
        if split == 'overall':
            return 'All Pitches'
        elif split == 'vs_lhh':
            return 'vs Left-Handed Hitters'
        elif split == 'vs_rhh':
            return 'vs Right-Handed Hitters'
        else:
            return split
