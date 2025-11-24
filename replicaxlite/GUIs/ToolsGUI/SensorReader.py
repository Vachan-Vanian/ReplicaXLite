######################################################################################################
# ReplicaXLite - A finite element toolkit for creating, analyzing and monitoring 3D structural models
# Copyright (C) 2024-2025 Vachan Vanian
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Contact: vachanvanian@outlook.com
######################################################################################################


import sys
import os
import json
import numpy as np
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                              QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
                              QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
                              QSplitter, QTextEdit, QGroupBox, QFormLayout, QDialog,
                              QLineEdit, QScrollArea, QGridLayout, QFrame, QRadioButton,
                              QButtonGroup, QMenu, QToolButton, QSizePolicy, QListWidget,
                              QHeaderView, QListWidgetItem, QDialogButtonBox, QTreeWidget, 
                              QTreeWidgetItem, QProgressBar)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QIcon, QAction, QColor

# Import matplotlib for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Import your data processing classes
from ...UtilityAPI.SensorsAPI import ReplicaXSensorDataReader


from decimal import Decimal, getcontext

class SmartQDoubleSpinBox(QDoubleSpinBox):
    def textFromValue(self, value):
        # Use Decimal for perfect decimal representation
        getcontext().prec = 8  # up to 10 digits precision
        decimal_value = Decimal(str(value))
        text = format(decimal_value.normalize(), 'f')  # 'normalize()' removes unnecessary trailing zeros
        return text if text else "0"

class FilterComparisonWindow(QMainWindow):
    """Main window for filter comparison tool"""
    def __init__(self, sensor_data, parent=None):
        super(FilterComparisonWindow, self).__init__(parent)
        self.sensor_data = sensor_data
        self.filter_configs = []
        self.comparison_results = None
        self.ranked_filters = None
        self.scores = None
        self.figures = {}
        
        # Setup UI
        self.setup_ui()
        self.setWindowTitle("Filter Comparison Tool")
        self.resize(1200, 800)
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create main splitter to divide configuration and results (HORIZONTAL instead of VERTICAL)
        self.main_splitter = QSplitter(Qt.Horizontal)  # Changed to horizontal
        main_layout.addWidget(self.main_splitter)
        
        # Left section - Configuration
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Add configuration group
        config_group = QGroupBox("Filter Comparison Configuration")
        config_form = QFormLayout(config_group)
        
        # Add sensor selection dropdown
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems(sorted(self.sensor_data.processed_data.keys()))
        config_form.addRow("Select Sensor:", self.sensor_combo)
        
        # Add ranking criteria
        ranking_group = QGroupBox("Ranking Criteria")
        ranking_layout = QGridLayout(ranking_group)
        
        # Add checkboxes for different metrics with weights in a more compact layout
        criteria_metrics = [
            ('rmse', 'RMSE (min)', 'min'),
            ('mae', 'MAE (min)', 'min'),
            ('snr_db', 'SNR (dB) (max)', 'max'),
            ('correlation', 'Correlation (max)', 'max'),
            ('energy_ratio', 'Energy Ratio (max)', 'max'),
            ('preservation_score', 'Peak Preservation (max)', 'max')
        ]
        
        self.criteria_checkboxes = {}
        self.criteria_weights = {}
        
        for i, (metric_id, metric_name, goal) in enumerate(criteria_metrics):
            row = i // 2
            col = (i % 2) * 2  # 0 or 2
            
            checkbox = QCheckBox(metric_name)
            weight_spin = QDoubleSpinBox()
            weight_spin.setMinimum(0.1)
            weight_spin.setMaximum(10.0)
            weight_spin.setValue(1.0)
            weight_spin.setSingleStep(0.1)
            
            # Store widgets in dictionaries for easy access
            self.criteria_checkboxes[metric_id] = checkbox
            self.criteria_weights[metric_id] = weight_spin
            
            # Default selections
            if metric_id in ['rmse', 'snr_db', 'correlation']:
                checkbox.setChecked(True)
            
            # Add to layout
            ranking_layout.addWidget(checkbox, row, col)
            ranking_layout.addWidget(weight_spin, row, col + 1)
        
        config_form.addRow(ranking_group)
        
        # Add filter configuration section
        filter_config_group = QGroupBox("Filter Configurations")
        filter_config_layout = QVBoxLayout(filter_config_group)
        
        # List of configured filters
        self.filter_list = QTreeWidget()
        self.filter_list.setHeaderLabels(["Filter Name", "Type", "Parameters"])
        self.filter_list.setMinimumHeight(200)
        self.filter_list.setColumnWidth(0, 200)
        self.filter_list.setColumnWidth(1, 150)
        filter_config_layout.addWidget(self.filter_list)
        
        # Buttons for managing filters
        filter_buttons_layout = QHBoxLayout()
        
        self.add_filter_btn = QPushButton("Add Filter")
        self.add_filter_btn.clicked.connect(self.add_filter)
        filter_buttons_layout.addWidget(self.add_filter_btn)
        
        self.edit_filter_btn = QPushButton("Edit Selected")
        self.edit_filter_btn.clicked.connect(self.edit_selected_filter)
        self.edit_filter_btn.setEnabled(False)
        filter_buttons_layout.addWidget(self.edit_filter_btn)
        
        self.remove_filter_btn = QPushButton("Remove Selected")
        self.remove_filter_btn.clicked.connect(self.remove_selected_filter)
        self.remove_filter_btn.setEnabled(False)
        filter_buttons_layout.addWidget(self.remove_filter_btn)
        
        # Connect selection changed signal
        self.filter_list.itemSelectionChanged.connect(self.update_filter_buttons)
        
        filter_config_layout.addLayout(filter_buttons_layout)
        config_form.addRow(filter_config_group)
        
        # Add preset buttons
        preset_layout = QHBoxLayout()
        
        self.add_common_filters_btn = QPushButton("Add Common Filters")
        self.add_common_filters_btn.clicked.connect(self.add_common_filters)
        preset_layout.addWidget(self.add_common_filters_btn)
        
        self.add_butterworth_variations_btn = QPushButton("Add Butterworth Variations")
        self.add_butterworth_variations_btn.clicked.connect(self.add_butterworth_variations)
        preset_layout.addWidget(self.add_butterworth_variations_btn)
        
        self.clear_filters_btn = QPushButton("Clear All Filters")
        self.clear_filters_btn.clicked.connect(self.clear_all_filters)
        preset_layout.addWidget(self.clear_filters_btn)
        
        config_form.addRow("Presets:", preset_layout)
        
        # Add run button
        run_layout = QHBoxLayout()
        self.run_comparison_btn = QPushButton("Run Comparison")
        self.run_comparison_btn.clicked.connect(self.run_comparison)
        self.run_comparison_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        run_layout.addStretch()
        run_layout.addWidget(self.run_comparison_btn)
        
        config_layout.addWidget(config_group)
        config_layout.addLayout(run_layout)
        
        # Right section - Results
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Tab widget for different result views
        self.results_tabs = QTabWidget()
        
        # Summary tab
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        
        self.summary_label = QLabel("Run comparison to see results.")
        summary_layout.addWidget(self.summary_label)
        
        self.rankings_table = QTableWidget()
        self.rankings_table.setColumnCount(3)
        self.rankings_table.setHorizontalHeaderLabels(["Rank", "Filter", "Score"])
        self.rankings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        summary_layout.addWidget(self.rankings_table)
        
        self.results_tabs.addTab(self.summary_tab, "Summary")
        
        # Metrics tab
        self.metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(self.metrics_tab)
        
        self.metrics_title = QLabel("<h2>Metrics Comparison</h2>")
        metrics_layout.addWidget(self.metrics_title)
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setMinimumHeight(250)
        metrics_layout.addWidget(self.metrics_table)
        
        self.results_tabs.addTab(self.metrics_tab, "Metrics")
        
        # Frequency Band Analysis tab
        self.freq_band_tab = QWidget()
        freq_band_layout = QVBoxLayout(self.freq_band_tab)
        
        self.freq_band_title = QLabel("<h2>Frequency Band Analysis</h2>")
        freq_band_layout.addWidget(self.freq_band_title)
        
        self.freq_band_table = QTableWidget()
        self.freq_band_table.setMinimumHeight(250)
        freq_band_layout.addWidget(self.freq_band_table)
        
        self.results_tabs.addTab(self.freq_band_tab, "Frequency Band Analysis")
        
        # Time domain tab
        self.time_tab = QWidget()
        time_layout = QVBoxLayout(self.time_tab)
        
        self.time_plot_container = QWidget()
        self.time_plot_layout = QVBoxLayout(self.time_plot_container)
        time_layout.addWidget(self.time_plot_container)
        
        self.results_tabs.addTab(self.time_tab, "Time Domain")
        
        # Frequency domain tab
        self.freq_tab = QWidget()
        freq_layout = QVBoxLayout(self.freq_tab)
        
        self.freq_plot_container = QWidget()
        self.freq_plot_layout = QVBoxLayout(self.freq_plot_container)
        freq_layout.addWidget(self.freq_plot_container)
        
        self.results_tabs.addTab(self.freq_tab, "Frequency Domain")
        
        # FFT tab
        self.fft_tab = QWidget()
        fft_layout = QVBoxLayout(self.fft_tab)
        
        self.fft_plot_container = QWidget()
        self.fft_plot_layout = QVBoxLayout(self.fft_plot_container)
        fft_layout.addWidget(self.fft_plot_container)
        
        self.results_tabs.addTab(self.fft_tab, "FFT Analysis")
        
        # Peaks tab
        self.peaks_tab = QWidget()
        peaks_layout = QVBoxLayout(self.peaks_tab)
        
        self.peaks_plot_container = QWidget()
        self.peaks_plot_layout = QVBoxLayout(self.peaks_plot_container)
        peaks_layout.addWidget(self.peaks_plot_container)
        
        self.results_tabs.addTab(self.peaks_tab, "Peak Preservation")
        
        # Add export button
        export_layout = QHBoxLayout()
        self.export_report_btn = QPushButton("Export Report")
        self.export_report_btn.clicked.connect(self.export_report)
        self.export_report_btn.setEnabled(False)
        export_layout.addStretch()
        export_layout.addWidget(self.export_report_btn)
        results_layout.addWidget(self.results_tabs)
        results_layout.addLayout(export_layout)
        
        # Add widgets to splitter
        self.main_splitter.addWidget(config_widget)
        self.main_splitter.addWidget(results_widget)
        
        # Set initial sizes (1:2 ratio)
        self.main_splitter.setSizes([400, 800])
    
    def add_filter(self):
        """Open dialog to add a new filter configuration"""
        # Generate a default name based on number of existing filters
        default_name = f"NewFilter_{len(self.filter_configs) + 1}"
        
        dialog = FilterConfigDialog(self, default_name=default_name)
        if dialog.exec() == QDialog.Accepted:
            filter_config = dialog.get_filter_config()
            self.add_filter_config(filter_config)
    
    def add_filter_config(self, filter_config):
        """Add a filter configuration to the list"""
        # Add to internal list
        self.filter_configs.append(filter_config)
        
        # Add to tree widget
        item = QTreeWidgetItem()
        item.setText(0, filter_config.get("name", "Unknown Filter"))
        item.setText(1, filter_config.get("filter", {}).get("type", "unknown"))
        
        # Format parameters for display
        params = filter_config.get("filter", {}).get("params", {})
        param_text = ", ".join([f"{k}: {v}" for k, v in params.items()])
        item.setText(2, param_text)
        
        self.filter_list.addTopLevelItem(item)
        
        # Update buttons
        self.update_run_button()
    
    def edit_selected_filter(self):
        """Edit the selected filter configuration"""
        selected_items = self.filter_list.selectedItems()
        if not selected_items:
            return
        
        # Get selected index
        selected_index = self.filter_list.indexOfTopLevelItem(selected_items[0])
        
        # Open edit dialog with current config
        dialog = FilterConfigDialog(self, initial_config=self.filter_configs[selected_index])
        if dialog.exec() == QDialog.Accepted:
            updated_config = dialog.get_filter_config()
            
            # Update internal list
            self.filter_configs[selected_index] = updated_config
            
            # Update display
            item = self.filter_list.topLevelItem(selected_index)
            item.setText(0, updated_config.get("name", "Unknown Filter"))
            item.setText(1, updated_config.get("filter", {}).get("type", "unknown"))
            
            # Format parameters for display
            params = updated_config.get("filter", {}).get("params", {})
            param_text = ", ".join([f"{k}: {v}" for k, v in params.items()])
            item.setText(2, param_text)
    
    def remove_selected_filter(self):
        """Remove the selected filter configuration"""
        selected_items = self.filter_list.selectedItems()
        if not selected_items:
            return
        
        # Get selected index
        selected_index = self.filter_list.indexOfTopLevelItem(selected_items[0])
        
        # Remove from internal list
        if 0 <= selected_index < len(self.filter_configs):
            del self.filter_configs[selected_index]
            
        # Remove from tree widget
        self.filter_list.takeTopLevelItem(selected_index)
        
        # Update buttons
        self.update_filter_buttons()
        self.update_run_button()
    
    def update_filter_buttons(self):
        """Update filter buttons based on selection"""
        has_selection = len(self.filter_list.selectedItems()) > 0
        self.edit_filter_btn.setEnabled(has_selection)
        self.remove_filter_btn.setEnabled(has_selection)
    
    def update_run_button(self):
        """Update run button based on filter count"""
        self.run_comparison_btn.setEnabled(len(self.filter_configs) >= 2)
    
    def add_common_filters(self):
        """Add a set of common filter configurations"""
        # Clear existing filters
        self.filter_configs.clear()
        self.filter_list.clear()
        
        # Add a set of commonly used filters
        common_filters = [
            # Butterworth lowpass
            {
                "name": "Butterworth LP 10Hz",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff": 10.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            # Moving average
            {
                "name": "Moving Average (11)",
                "filter": {
                    "type": "moving_avg",
                    "params": {
                        "window_size": 11
                    }
                }
            },
            # Savitzky-Golay
            {
                "name": "Savitzky-Golay",
                "filter": {
                    "type": "savgol",
                    "params": {
                        "window_length": 21,
                        "polyorder": 3
                    }
                }
            },
            # Chebyshev Type I
            {
                "name": "Chebyshev-I LP 10Hz",
                "filter": {
                    "type": "chebyshev1",
                    "params": {
                        "order": 4,
                        "cutoff": 10.0,
                        "btype": "low",
                        "rp": 1.0,
                        "zero_phase": True
                    }
                }
            },
            # FIR filter
            {
                "name": "FIR LP 10Hz",
                "filter": {
                    "type": "fir",
                    "params": {
                        "numtaps": 101,
                        "cutoff": 10.0,
                        "btype": "low",
                        "window": "hamming",
                        "zero_phase": True
                    }
                }
            }
        ]
        
        # Add each common filter
        for filter_config in common_filters:
            self.add_filter_config(filter_config)
    
    def add_butterworth_variations(self):
        """Add variations of Butterworth filter configurations"""
        # Clear existing filters
        self.filter_configs.clear()
        self.filter_list.clear()
        
        # Add variations of Butterworth filters
        butterworth_variations = [
            # Different orders
            {
                "name": "Butterworth 2nd Order",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 2,
                        "cutoff": 10.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            {
                "name": "Butterworth 4th Order",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff": 10.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            {
                "name": "Butterworth 8th Order",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 8,
                        "cutoff": 10.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            # Different cutoff frequencies
            {
                "name": "Butterworth LP 5Hz",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff": 5.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            {
                "name": "Butterworth LP 20Hz",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff": 20.0,
                        "btype": "low",
                        "zero_phase": True
                    }
                }
            },
            # Different filter types
            {
                "name": "Butterworth HP 5Hz",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff": 5.0,
                        "btype": "high",
                        "zero_phase": True
                    }
                }
            },
            {
                "name": "Butterworth BP 5-20Hz",
                "filter": {
                    "type": "butterworth",
                    "params": {
                        "order": 4,
                        "cutoff_low": 5.0,
                        "cutoff_high": 20.0,
                        "btype": "band",
                        "zero_phase": True
                    }
                }
            }
        ]
        
        # Add each Butterworth variation
        for filter_config in butterworth_variations:
            self.add_filter_config(filter_config)
    
    def clear_all_filters(self):
        """Clear all filter configurations"""
        self.filter_configs.clear()
        self.filter_list.clear()
        self.update_run_button()
    
    def run_comparison(self):
        """Run the filter comparison with selected configurations"""
        if len(self.filter_configs) < 2:
            QMessageBox.warning(self, "Insufficient Filters", 
                               "Please add at least two filter configurations to compare.")
            return
        
        # Get selected sensor
        sensor_name = self.sensor_combo.currentText()
        
        # Build ranking criteria
        ranking_criteria = {}
        for metric_id, checkbox in self.criteria_checkboxes.items():
            if checkbox.isChecked():
                weight = self.criteria_weights[metric_id].value()
                
                # Determine goal (min or max)
                goal = "max"
                if metric_id in ["rmse", "mae"]:
                    goal = "min"
                
                ranking_criteria[metric_id] = {
                    "weight": weight,
                    "goal": goal
                }
        
        # Show progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Running Comparison")
        progress_layout = QVBoxLayout(progress_dialog)
        
        progress_label = QLabel("Analyzing filters...")
        progress_layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_layout.addWidget(progress_bar)
        
        progress_dialog.setMinimumWidth(300)
        progress_dialog.show()
        
        # Process events to show the dialog
        QApplication.processEvents()
        
        try:
            # Clear existing results
            self.clear_result_plots()
            
            # Run comparison
            progress_bar.setValue(10)
            progress_label.setText("Comparing filters...")
            QApplication.processEvents()
            
            # Run the comparison
            self.comparison_results = self.sensor_data.compare_filters(
                sensor_name, self.filter_configs
            )
            
            progress_bar.setValue(50)
            progress_label.setText("Ranking filters...")
            QApplication.processEvents()
            
            # Rank the filters
            self.ranked_filters, self.scores = self.sensor_data.rank_filters(
                self.comparison_results, ranking_criteria
            )
            
            progress_bar.setValue(70)
            progress_label.setText("Generating visualizations...")
            QApplication.processEvents()
            
            # Generate figures
            self.figures = self.sensor_data.visualize_filter_comparison(
                sensor_name, self.comparison_results, output_dir=None,
                plot_types=['time', 'frequency', 'fft', 'peaks', 'metrics']
            )
            
            progress_bar.setValue(90)
            progress_label.setText("Updating display...")
            QApplication.processEvents()
            
            # Update the UI with results
            self.update_results_ui()
            
            progress_bar.setValue(100)
            progress_dialog.close()
            
            # Enable export button
            self.export_report_btn.setEnabled(True)
            
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Error running comparison: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear_result_plots(self):
        """Clear all result plots"""
        # Clear the plot containers
        for layout in [self.time_plot_layout, self.freq_plot_layout, 
                       self.fft_plot_layout, self.peaks_plot_layout]:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Reset the summary label
        self.summary_label.setText("Running comparison...")
        
        # Clear tables
        self.rankings_table.setRowCount(0)
        self.metrics_table.setRowCount(0)
        self.metrics_table.setColumnCount(0)
        self.freq_band_table.setRowCount(0)
        self.freq_band_table.setColumnCount(0)
    
    def update_results_ui(self):
        """Update UI with comparison results"""
        if not self.comparison_results or not self.ranked_filters:
            return
        
        # Get a non-private result key to access sensor name
        filter_key = None
        for key in self.comparison_results.keys():
            if not key.startswith('__'):
                filter_key = key
                break
        
        if not filter_key:
            return
            
        # Get selected sensor name
        sensor_name = self.sensor_combo.currentText()
        
        # Update summary
        self.summary_label.setText(f"<h3>Filter Comparison Results for {sensor_name}</h3>")
        
        # Update rankings table
        self.rankings_table.setRowCount(len(self.ranked_filters))
        
        for i, filter_name in enumerate(self.ranked_filters):
            # Rank
            rank_item = QTableWidgetItem(str(i+1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            rank_item.setFlags(rank_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.rankings_table.setItem(i, 0, rank_item)
            
            # Filter name
            name_item = QTableWidgetItem(filter_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.rankings_table.setItem(i, 1, name_item)
            
            # Score
            score_item = QTableWidgetItem(f"{self.scores[filter_name]:.4f}")
            score_item.setTextAlignment(Qt.AlignCenter)
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.rankings_table.setItem(i, 2, score_item)
            
            # Set background color for top ranks
            if i == 0:
                for col in range(3):
                    self.rankings_table.item(i, col).setBackground(QColor("#d4edda"))  # Light green
            elif i == 1:
                for col in range(3):
                    self.rankings_table.item(i, col).setBackground(QColor("#fff3cd"))  # Light yellow
        
        # Update metrics and frequency band tables
        self.update_metrics_table()
        self.update_frequency_band_table()
        
        # Update plot tabs
        self.update_plot_tabs()
    
    def update_metrics_table(self):
        """Update the metrics table with detailed comparison results"""
        if not self.comparison_results or not self.ranked_filters:
            return
        
        # Define metrics to display
        time_metrics = ['rmse', 'snr_db', 'correlation', 'energy_ratio']
        
        # Set up the table
        self.metrics_table.setRowCount(len(self.ranked_filters))
        self.metrics_table.setColumnCount(len(time_metrics) + 1)  # +1 for filter names
        
        # Set horizontal header (metric names)
        header_labels = ["Filter"]
        header_labels.extend(['RMSE', 'SNR (dB)', 'Correlation', 'Energy Ratio'])
        self.metrics_table.setHorizontalHeaderLabels(header_labels)
        
        # Configure table appearance
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Fill the table
        for row, filter_name in enumerate(self.ranked_filters):
            # Filter name column
            filter_item = QTableWidgetItem(filter_name)
            filter_item.setFlags(filter_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.metrics_table.setItem(row, 0, filter_item)
            
            # Metrics columns
            results = self.comparison_results[filter_name]
            for col, metric in enumerate(time_metrics, 1):
                value = results['time_metrics'].get(metric, 0)
                cell_item = QTableWidgetItem(f"{value:.6f}" if isinstance(value, float) else str(value))
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                cell_item.setTextAlignment(Qt.AlignCenter)
                
                # Add color coding
                if metric == 'rmse':
                    # Lower is better for RMSE
                    if value < 1.0:
                        cell_item.setForeground(QColor("green"))
                    else:
                        cell_item.setForeground(QColor("red"))
                elif metric in ['snr_db', 'correlation']:
                    # Higher is better
                    if (metric == 'snr_db' and value > 40) or (metric == 'correlation' and value > 0.99):
                        cell_item.setForeground(QColor("green"))
                    else:
                        cell_item.setForeground(QColor("red"))
                elif metric == 'energy_ratio':
                    # Closer to 1.0 is better
                    if 0.95 < value < 1.05:
                        cell_item.setForeground(QColor("green"))
                    else:
                        cell_item.setForeground(QColor("red"))
                
                self.metrics_table.setItem(row, col, cell_item)
            
            # Highlight the best filter
            if row == 0:
                for col in range(self.metrics_table.columnCount()):
                    self.metrics_table.item(row, col).setBackground(QColor("#d4edda"))  # Light green
        
        # Resize columns to content
        self.metrics_table.resizeColumnsToContents()
    
    def update_frequency_band_table(self):
        """Update the frequency band analysis table"""
        if not self.comparison_results or not self.ranked_filters:
            return
        
        # Define frequency band metrics
        freq_metrics = ['low_band_ratio', 'mid_band_ratio', 'high_band_ratio']
        
        # Set up the table
        self.freq_band_table.setRowCount(len(self.ranked_filters))
        self.freq_band_table.setColumnCount(len(freq_metrics) + 1)  # +1 for filter names
        
        # Set horizontal header
        header_labels = ["Filter", "Low Band Ratio", "Mid Band Ratio", "High Band Ratio"]
        self.freq_band_table.setHorizontalHeaderLabels(header_labels)
        
        # Configure table appearance
        self.freq_band_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Fill the table
        for row, filter_name in enumerate(self.ranked_filters):
            # Filter name column
            filter_item = QTableWidgetItem(filter_name)
            filter_item.setFlags(filter_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.freq_band_table.setItem(row, 0, filter_item)
            
            # Frequency metrics columns
            results = self.comparison_results[filter_name]
            for col, metric in enumerate(freq_metrics, 1):
                value = results['frequency_metrics'].get(metric, 0)
                cell_item = QTableWidgetItem(f"{value:.6f}" if isinstance(value, float) else str(value))
                cell_item.setFlags(cell_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                cell_item.setTextAlignment(Qt.AlignCenter)
                
                # Color coding for frequency band ratios
                if metric == 'low_band_ratio':
                    # Low band should be preserved (close to 1.0 is good)
                    if 0.95 < value < 1.05:
                        cell_item.setForeground(QColor("green"))
                    else:
                        cell_item.setForeground(QColor("red"))
                elif metric in ['mid_band_ratio', 'high_band_ratio']:
                    # Mid/High band suppression depends on filter purpose
                    # Just color by value for visualization
                    if value < 0.05:
                        cell_item.setForeground(QColor("red"))
                    elif value < 0.5:
                        cell_item.setForeground(QColor("orange"))
                    else:
                        cell_item.setForeground(QColor("green"))
                
                self.freq_band_table.setItem(row, col, cell_item)
            
            # Highlight the best filter
            if row == 0:
                for col in range(self.freq_band_table.columnCount()):
                    self.freq_band_table.item(row, col).setBackground(QColor("#d4edda"))  # Light green
        
        # Resize columns to content
        self.freq_band_table.resizeColumnsToContents()
    
    def update_plot_tabs(self):
        """Update the plot tabs with matplotlib figures"""
        if not self.figures:
            return
        
        # Helper function to add a figure to a layout
        def add_figure_to_layout(figure, layout):
            # Clear layout first
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Create a canvas to display the figure
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas, self)
            
            # Add to layout
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
        
        # Add figures to respective tabs
        if 'time' in self.figures:
            add_figure_to_layout(self.figures['time'], self.time_plot_layout)
        
        if 'frequency' in self.figures:
            add_figure_to_layout(self.figures['frequency'], self.freq_plot_layout)
        
        if 'fft' in self.figures:
            add_figure_to_layout(self.figures['fft'], self.fft_plot_layout)
        
        if 'peaks' in self.figures:
            add_figure_to_layout(self.figures['peaks'], self.peaks_plot_layout)
    
    def export_report(self):
        """Export a comprehensive HTML report of the comparison"""
        if not self.comparison_results or not self.ranked_filters:
            QMessageBox.warning(self, "No Results", "No comparison results to export.")
            return
        
        # Get the directory to save the report
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory for Report", "", QFileDialog.ShowDirsOnly
        )
        
        if not output_dir:
            return
        
        try:
            # Build ranking criteria
            ranking_criteria = {}
            for metric_id, checkbox in self.criteria_checkboxes.items():
                if checkbox.isChecked():
                    weight = self.criteria_weights[metric_id].value()
                    
                    # Determine goal (min or max)
                    goal = "max"
                    if metric_id in ["rmse", "mae"]:
                        goal = "min"
                    
                    ranking_criteria[metric_id] = {
                        "weight": weight,
                        "goal": goal
                    }
            
            # Get selected sensor
            sensor_name = self.sensor_combo.currentText()
            
            # Generate report
            report_path = self.sensor_data.generate_filter_report(
                sensor_name, self.comparison_results, output_dir, ranking_criteria
            )
            
            # Inform user
            QMessageBox.information(
                self, "Report Generated", 
                f"Report has been saved to:\n{report_path}\n\nDirectory contains all plots and analysis."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating report: {str(e)}")
            import traceback
            traceback.print_exc()


class FilterConfigDialog(QDialog):
    """Dialog for configuring a filter"""
    def __init__(self, parent=None, initial_config=None, default_name=None):
        super(FilterConfigDialog, self).__init__(parent)
        self.setWindowTitle("Filter Configuration")
        self.resize(600, 500)
        
        self.initial_config = initial_config
        self.default_name = default_name
        
        # Set up the UI
        self.setup_ui()
        
        # Load initial data if provided
        if initial_config:
            self.load_config(initial_config)
        elif default_name:
            self.name_edit.setText(default_name)
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Filter name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Filter Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a descriptive name for this filter")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Filter type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Filter Type:"))
        self.filter_type = QComboBox()
        self.filter_type.addItems([
            "none", 
            "butterworth", 
            "chebyshev1", 
            "chebyshev2", 
            "elliptic", 
            "bessel", 
            "fir", 
            "savgol", 
            "moving_avg"
        ])
        self.filter_type.currentIndexChanged.connect(self.update_parameter_ui)
        type_layout.addWidget(self.filter_type)
        layout.addLayout(type_layout)
        
        # Parameters group in a scroll area for better display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.params_group = QWidget()
        self.params_layout = QFormLayout(self.params_group)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.params_group)
        layout.addWidget(scroll_area)
        
        # Create parameter widgets containers
        self.param_widgets = {}
        
        # Initialize with empty parameters
        self.update_parameter_ui()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_parameter_ui(self):
        """
        Rebuild the parameter panel whenever the Filter‑Type changes.
        This version makes sure the old 'none'‑info label is completely
        removed, so it never lingers at the bottom of the dialog.
        """
        # ── 0.  Wipe the form clean  ────────────────────────────────────────────
        for i in reversed(range(self.params_layout.rowCount())):
            self.params_layout.removeRow(i)
        self.param_widgets = {}                         # reset our widget map

        # ── 1.  Which filter are we showing controls for?  ─────────────────────
        filter_type = self.filter_type.currentText()

        # ── 2.  Special case: 'none'  ──────────────────────────────────────────
        if filter_type == "none":
            info_lbl = QLabel("No parameters needed for 'none' filter type.")
            info_lbl.setObjectName("_info_none")        # helpful if you ever want to find it
            self.params_layout.addRow(info_lbl)
            return                                      # <-- done for this type

        # ── 3.  Parameter widgets for every other type  ────────────────────────
        # ▷ Example for Savitzky–Golay  (repeat the same idea for the others)
        if filter_type == "savgol":
            # window_length
            wlen = QSpinBox()
            wlen.setRange(3, 1001)
            wlen.setSingleStep(2)
            wlen.setValue(11)
            self.params_layout.addRow("Window Length:", wlen)
            self.param_widgets["window_length"] = wlen

            # polyorder
            pord = QSpinBox()
            pord.setRange(1, 100)
            pord.setValue(3)
            self.params_layout.addRow("Polynomial Order:", pord)
            self.param_widgets["polyorder"] = pord

        elif filter_type == "moving_avg":
            win = QSpinBox()
            win.setRange(1, 100000)
            win.setValue(11)
            self.params_layout.addRow("Window Size:", win)
            self.param_widgets["window_size"] = win

        elif filter_type == "fir":
            numtaps = QSpinBox()
            numtaps.setRange(1, 100000)
            numtaps.setSingleStep(2)
            numtaps.setValue(101)
            self.params_layout.addRow("Number of Taps:", numtaps)
            self.param_widgets["numtaps"] = numtaps

            window = QComboBox()
            window.addItems(["hamming", "hann", "blackman", "boxcar", "kaiser"])
            self.params_layout.addRow("Window Type:", window)
            self.param_widgets["window"] = window

            # common IIR/FIR options
            self.add_filter_mode_ui()

            zp = QCheckBox("Enable Zero‑Phase Filtering")
            zp.setChecked(True)
            self.params_layout.addRow("", zp)
            self.param_widgets["zero_phase"] = zp

        elif filter_type in ["butterworth", "chebyshev1", "chebyshev2",
                            "elliptic", "bessel"]:
            order = QSpinBox()
            order.setRange(1, 20)
            order.setValue(4)
            self.params_layout.addRow("Order:", order)
            self.param_widgets["order"] = order

            if filter_type in ["chebyshev1", "elliptic"]:
                rp = QDoubleSpinBox()
                rp.setRange(0.1, 20.0)
                rp.setSingleStep(0.1)
                rp.setDecimals(1)
                rp.setValue(1.0)
                self.params_layout.addRow("Passband Ripple (dB):", rp)
                self.param_widgets["rp"] = rp

            if filter_type in ["chebyshev2", "elliptic"]:
                rs = QDoubleSpinBox()
                rs.setRange(10.0, 120.0)
                rs.setSingleStep(1.0)
                rs.setDecimals(1)
                rs.setValue(40.0)
                self.params_layout.addRow("Stopband Attenuation (dB):", rs)
                self.param_widgets["rs"] = rs

            # common options
            self.add_filter_mode_ui()

            zp = QCheckBox("Enable Zero‑Phase Filtering")
            zp.setChecked(True)
            self.params_layout.addRow("", zp)
            self.param_widgets["zero_phase"] = zp

    def add_filter_mode_ui(self):
        """Add filter mode (low, high, band, bandstop) UI elements"""
        # Filter type selection (low, high, band, bandstop)
        btype = QComboBox()
        btype.addItems(["low", "high", "band", "bandstop"])
        self.params_layout.addRow("Filter Mode:", btype)
        self.param_widgets["btype"] = btype
        
        # Single cutoff for low/high pass
        cutoff = QDoubleSpinBox()
        cutoff.setMinimum(0.001)
        cutoff.setMaximum(10000.0)
        cutoff.setSingleStep(0.1)
        cutoff.setDecimals(3)
        cutoff.setValue(10.0)
        cutoff_label = QLabel("Cutoff Frequency (Hz):")
        self.params_layout.addRow(cutoff_label, cutoff)
        self.param_widgets["cutoff"] = cutoff
        self.cutoff_label = cutoff_label
        
        # Dual cutoffs for band/bandstop
        cutoff_low = QDoubleSpinBox()
        cutoff_low.setMinimum(0.001)
        cutoff_low.setMaximum(10000.0)
        cutoff_low.setSingleStep(0.1)
        cutoff_low.setDecimals(3)
        cutoff_low.setValue(5.0)
        cutoff_low_label = QLabel("Low Cutoff Frequency (Hz):")
        self.params_layout.addRow(cutoff_low_label, cutoff_low)
        self.param_widgets["cutoff_low"] = cutoff_low
        self.cutoff_low_label = cutoff_low_label
        
        cutoff_high = QDoubleSpinBox()
        cutoff_high.setMinimum(0.001)
        cutoff_high.setMaximum(10000.0)
        cutoff_high.setSingleStep(0.1)
        cutoff_high.setDecimals(3)
        cutoff_high.setValue(20.0)
        cutoff_high_label = QLabel("High Cutoff Frequency (Hz):")
        self.params_layout.addRow(cutoff_high_label, cutoff_high)
        self.param_widgets["cutoff_high"] = cutoff_high
        self.cutoff_high_label = cutoff_high_label
        
        # Connect signal to update cutoff visibility
        btype.currentTextChanged.connect(self.update_cutoff_visibility)
        
        # Initial visibility
        self.update_cutoff_visibility(btype.currentText())
    
    def update_cutoff_visibility(self, btype):
        """Update cutoff fields visibility based on filter type"""
        is_band = btype in ["band", "bandstop"]
        
        # Show/hide single cutoff
        self.param_widgets["cutoff"].setVisible(not is_band)
        self.cutoff_label.setVisible(not is_band)
        
        # Show/hide dual cutoffs
        self.param_widgets["cutoff_low"].setVisible(is_band)
        self.cutoff_low_label.setVisible(is_band)
        self.param_widgets["cutoff_high"].setVisible(is_band)
        self.cutoff_high_label.setVisible(is_band)
    
    def load_config(self, config: dict):
        """
        Populate the dialog with an existing filter‑configuration dict.

        Parameters
        ----------
        config : dict
            {
                "name":   "Butter LP 10 Hz",
                "filter": {
                    "type":   "butterworth",
                    "params": {
                        "order":       4,
                        "cutoff":      10.0,
                        "btype":       "low",
                        "zero_phase":  True,
                        ...
                    }
                }
            }
        """
        if not config:          # nothing to load
            return

        # ── 1.  Name  ──────────────────────────────────────────────────────────
        self.name_edit.setText(config.get("name", ""))

        # ── 2.  Select the filter‑type in the combo; this immediately rebuilds
        #        the parameter panel via update_parameter_ui()  ────────────────
        f_cfg = config.get("filter", {})
        f_type = f_cfg.get("type", "none")
        self.filter_type.setCurrentText(f_type)     # triggers UI rebuild

        # ── 3.  Fill in parameter values  ─────────────────────────────────────
        params = f_cfg.get("params", {})

        for pname, pvalue in params.items():
            if pname not in self.param_widgets:
                # parameter is not applicable for the current filter‑type
                continue

            w = self.param_widgets[pname]

            if isinstance(w, QComboBox):
                # guard in case value is not in the list
                idx = w.findText(str(pvalue))
                if idx >= 0:
                    w.setCurrentIndex(idx)
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(pvalue))
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                w.setValue(float(pvalue))

        # ── 4.  Make sure cutoff visibility matches the loaded 'btype' setting ─
        if "btype" in params and "btype" in self.param_widgets:
            self.update_cutoff_visibility(params["btype"])

    def get_filter_config(self):
        """Get the filter configuration from the dialog"""
        # Build the filter configuration dictionary
        filter_name = self.name_edit.text()
        if not filter_name:
            filter_name = f"{self.filter_type.currentText().capitalize()} Filter"
        
        filter_type = self.filter_type.currentText()
        
        # Collect parameters
        params = {}
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QComboBox):
                params[param_name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                params[param_name] = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                params[param_name] = widget.value()
        
        # For band/bandstop filters, include only relevant cutoff parameters
        if "btype" in params and params["btype"] in ["band", "bandstop"]:
            if "cutoff" in params:
                del params["cutoff"]
        else:
            # For low/high filters, remove band-specific parameters
            if "cutoff_low" in params:
                del params["cutoff_low"]
            if "cutoff_high" in params:
                del params["cutoff_high"]
        
        return {
            "name": filter_name,
            "filter": {
                "type": filter_type,
                "params": params
            }
        }


# Define a custom class for plotting
class SensorPlotCanvas(FigureCanvas):
    """Canvas for plotting sensor data"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(SensorPlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Initialize plot data
        self.plot_lines = {}
        self.legend_added = False
        
        # Configure the figure with grid
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.fig.tight_layout()
    
    def plot_sensor(self, time_array, data_array, sensor_name, color=None):
        """Plot a single sensor's data"""
        if sensor_name in self.plot_lines:
            # Update existing line
            line = self.plot_lines[sensor_name]
            line.set_xdata(time_array)
            line.set_ydata(data_array)
        else:
            # Create new line
            line, = self.axes.plot(time_array, data_array, label=sensor_name, color=color, 
                                  linewidth=1.5, marker='', markersize=2)
            self.plot_lines[sensor_name] = line
            
        # Add/update legend if needed
        if self.plot_lines and not self.legend_added:
            self.axes.legend()
            self.legend_added = True
        elif self.legend_added:
            self.axes.legend()
            
        # Auto-scale the axes
        self.axes.relim()
        self.axes.autoscale_view()
        self.fig.canvas.draw_idle()
    
    def clear_plot(self):
        """Clear all plots"""
        self.axes.clear()
        self.axes.grid(True, linestyle='--', alpha=0.7)
        self.plot_lines = {}
        self.legend_added = False
        self.fig.canvas.draw_idle()
    
    def remove_sensor(self, sensor_name):
        """Remove a specific sensor from the plot"""
        if sensor_name in self.plot_lines:
            line = self.plot_lines[sensor_name]
            line.remove()
            del self.plot_lines[sensor_name]
            
            # Update legend if needed
            if self.plot_lines:
                self.axes.legend()
            else:
                self.legend_added = False
                
            self.fig.canvas.draw_idle()
    
    def set_labels(self, x_label="Time", y_label="Value", title=None):
        """Set axis labels and title"""
        self.axes.set_xlabel(x_label, fontsize=10, fontweight='bold')
        self.axes.set_ylabel(y_label, fontsize=10, fontweight='bold')
        if title:
            self.axes.set_title(title, fontsize=12, fontweight='bold')
        self.fig.canvas.draw_idle()

class LogTextEdit(QTextEdit):
    """Custom text edit for logging with level-based formatting"""
    def __init__(self, parent=None):
        super(LogTextEdit, self).__init__(parent)
        self.setReadOnly(True)
        
    def append_message(self, message, level="INFO"):
        """Append a message with level-based formatting"""
        color_map = {
            "INFO": "magenta",
            "WARNING": "orange",
            "ERROR": "red",
            "SUCCESS": "green"
        }
        
        color = color_map.get(level, "black")
        formatted_msg = f"<span style='color:{color};'><b>[{level}]</b> {message}</span>"
        self.append(formatted_msg)

class ConfigurationEditorDialog(QDialog):
    """Dialog for editing the full configuration"""
    def __init__(self, config, units_converter, parent=None):
        super(ConfigurationEditorDialog, self).__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.config = config.copy() if config else {}
        self.units_converter = units_converter
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create a tab widget for different sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs for different configuration sections
        self.create_basic_settings_tab()
        self.create_units_tab()
        self.create_data_mapping_tab()
        self.create_corrections_tab()
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Save Configuration")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)
        main_layout.addLayout(buttons_layout)
    
    # ADD NEW METHOD FOR FILTER
    def edit_filter_parameters(self):
        """Open dialog to edit filter parameters"""
        filter_type = self.filter_type.currentText()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{filter_type.title()} Filter Parameters")
        layout = QFormLayout(dialog)
        
        # Initialize filter params if they don't exist
        if not hasattr(self, 'filter_params') or self.filter_params is None:
            self.filter_params = {}
        
        # Create different parameter fields based on filter type
        if filter_type == "savgol":
            # Savitzky-Golay filter parameters
            window_length = QSpinBox()
            window_length.setMinimum(3)
            window_length.setMaximum(100001)
            window_length.setSingleStep(2)  # Must be odd
            window_length.setValue(self.filter_params.get("window_length", 11))
            layout.addRow("Window Length:", window_length)
            
            polyorder = QSpinBox()
            polyorder.setMinimum(1)
            polyorder.setMaximum(10)
            polyorder.setValue(self.filter_params.get("polyorder", 3))
            layout.addRow("Polynomial Order:", polyorder)
            
        elif filter_type == "moving_avg":
            # Moving average filter parameters
            window_size = QSpinBox()
            window_size.setMinimum(2)
            window_size.setMaximum(100001)
            window_size.setValue(self.filter_params.get("window_size", 11))
            layout.addRow("Window Size:", window_size)
            
        elif filter_type in ["butterworth", "chebyshev1", "chebyshev2", "elliptic", "bessel", "fir"]:
            # Common IIR and FIR filter parameters
            
            # For FIR filters, we need numtaps
            if filter_type == "fir":
                numtaps = QSpinBox()
                numtaps.setMinimum(3)
                numtaps.setMaximum(1001)
                numtaps.setSingleStep(2)  # Keep it odd
                numtaps.setValue(self.filter_params.get("numtaps", 101))
                layout.addRow("Number of Taps:", numtaps)
                
                window_type = QComboBox()
                window_type.addItems(["hamming", "hann", "blackman", "boxcar", "kaiser"])
                window_type.setCurrentText(self.filter_params.get("window", "hamming"))
                layout.addRow("Window Type:", window_type)
            
            # For IIR filters, we need order
            if filter_type in ["butterworth", "chebyshev1", "chebyshev2", "elliptic", "bessel"]:
                order = QSpinBox()
                order.setMinimum(1)
                order.setMaximum(20)
                order.setValue(self.filter_params.get("order", 4))
                layout.addRow("Order:", order)
            
            # Ripple parameters for Chebyshev and Elliptic
            if filter_type in ["chebyshev1", "elliptic"]:
                rp = QDoubleSpinBox()
                rp.setMinimum(0.1)
                rp.setMaximum(20.0)
                rp.setSingleStep(0.1)
                rp.setDecimals(1)
                rp.setValue(self.filter_params.get("rp", 1.0))
                layout.addRow("Passband Ripple (dB):", rp)
            
            if filter_type in ["chebyshev2", "elliptic"]:
                rs = QDoubleSpinBox()
                rs.setMinimum(10.0)
                rs.setMaximum(120.0)
                rs.setSingleStep(1.0)
                rs.setDecimals(1)
                rs.setValue(self.filter_params.get("rs", 40.0))
                layout.addRow("Stopband Attenuation (dB):", rs)
            
            # Zero-phase option
            zero_phase = QCheckBox("Enable Zero-Phase Filtering")
            zero_phase.setChecked(self.filter_params.get("zero_phase", True))
            zero_phase.setToolTip("Eliminates phase distortion but doubles filter order")
            layout.addRow("", zero_phase)
            
            # Filter type selection (low, high, band, bandstop)
            btype = QComboBox()
            btype.addItems(["low", "high", "band", "bandstop"])
            btype.setCurrentText(self.filter_params.get("btype", "low"))
            layout.addRow("Filter Mode:", btype)
            
            # Single cutoff for low/high pass
            cutoff = QDoubleSpinBox()
            cutoff.setMinimum(0.001)
            cutoff.setMaximum(99999.0)
            cutoff.setSingleStep(0.01)
            cutoff.setDecimals(3)
            cutoff.setValue(self.filter_params.get("cutoff", 0.1))
            cutoff_row = layout.addRow("Cutoff Frequency (Hz):", cutoff)
            
            # Dual cutoffs for band/bandstop
            cutoff_low = QDoubleSpinBox()
            cutoff_low.setMinimum(0.001)
            cutoff_low.setMaximum(99999.0)
            cutoff_low.setSingleStep(0.01)
            cutoff_low.setDecimals(3)
            cutoff_low.setValue(self.filter_params.get("cutoff_low", 0.1))
            cutoff_low_row = layout.addRow("Low Cutoff Frequency (Hz):", cutoff_low)
            
            cutoff_high = QDoubleSpinBox()
            cutoff_high.setMinimum(0.001)
            cutoff_high.setMaximum(99999.0)
            cutoff_high.setSingleStep(0.01)
            cutoff_high.setDecimals(3)
            cutoff_high.setValue(self.filter_params.get("cutoff_high", 0.2))
            cutoff_high_row = layout.addRow("High Cutoff Frequency (Hz):", cutoff_high)
            
            # Function to update visibility of cutoff fields based on filter type
            def update_cutoff_visibility():
                is_band = btype.currentText() in ["band", "bandstop"]
                # For band filters, show low/high cutoffs, hide single cutoff
                # For low/high filters, hide low/high cutoffs, show single cutoff
                cutoff.setVisible(not is_band)
                layout.labelForField(cutoff).setVisible(not is_band)
                cutoff_low.setVisible(is_band)
                layout.labelForField(cutoff_low).setVisible(is_band)
                cutoff_high.setVisible(is_band)
                layout.labelForField(cutoff_high).setVisible(is_band)
            
            # Connect signal
            btype.currentTextChanged.connect(update_cutoff_visibility)
            
            # Initialize visibility
            update_cutoff_visibility()
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            # Update filter parameters based on the selected filter type
            self.filter_params = {}
            
            if filter_type == "savgol":
                self.filter_params["window_length"] = window_length.value()
                self.filter_params["polyorder"] = polyorder.value()
                
            elif filter_type == "moving_avg":
                self.filter_params["window_size"] = window_size.value()
                
            elif filter_type == "fir":
                self.filter_params["numtaps"] = numtaps.value()
                self.filter_params["window"] = window_type.currentText()
                self.filter_params["zero_phase"] = zero_phase.isChecked()
                self.filter_params["btype"] = btype.currentText()
                
                # Store the appropriate cutoff values based on filter type
                if btype.currentText() in ["band", "bandstop"]:
                    self.filter_params["cutoff_low"] = cutoff_low.value()
                    self.filter_params["cutoff_high"] = cutoff_high.value()
                else:
                    self.filter_params["cutoff"] = cutoff.value()
                    
            elif filter_type in ["butterworth", "chebyshev1", "chebyshev2", "elliptic", "bessel"]:
                self.filter_params["order"] = order.value()
                
                # Add ripple parameters for relevant filter types
                if filter_type in ["chebyshev1", "elliptic"]:
                    self.filter_params["rp"] = rp.value()
                    
                if filter_type in ["chebyshev2", "elliptic"]:
                    self.filter_params["rs"] = rs.value()
                    
                self.filter_params["zero_phase"] = zero_phase.isChecked()
                self.filter_params["btype"] = btype.currentText()
                
                # Store the appropriate cutoff values based on filter type
                if btype.currentText() in ["band", "bandstop"]:
                    self.filter_params["cutoff_low"] = cutoff_low.value()
                    self.filter_params["cutoff_high"] = cutoff_high.value()
                else:
                    self.filter_params["cutoff"] = cutoff.value()

    def create_basic_settings_tab(self):
        """Create the tab for basic settings"""
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        # File path
        self.file_path_edit = QLineEdit(self.config.get("file_path", ""))
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_path_layout.addWidget(browse_btn)
        layout.addRow("File Path:", file_path_layout)
        
        # Separator
        self.separator_combo = QComboBox()
        self.separator_combo.addItems([",", ";", "\\t", " ", "|"])
        self.separator_combo.setCurrentText(self.config.get("seperator", ","))
        layout.addRow("Separator:", self.separator_combo)
        
        # Decimal
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems([".", ","])
        self.decimal_combo.setCurrentText(self.config.get("decimal", "."))
        layout.addRow("Decimal:", self.decimal_combo)
        
        # Start and end rows
        self.start_row_spin = QSpinBox()
        self.start_row_spin.setMinimum(1)
        self.start_row_spin.setMaximum(1000000)
        self.start_row_spin.setValue(self.config.get("start_row", 1))
        layout.addRow("Start Row:", self.start_row_spin)
        
        self.end_row_spin = QSpinBox()
        self.end_row_spin.setMinimum(1)
        self.end_row_spin.setMaximum(1000000)
        self.end_row_spin.setValue(self.config.get("end_row", 1000))
        layout.addRow("End Row:", self.end_row_spin)
        
        # Time step (dt)
        self.dt_spin = QDoubleSpinBox()
        self.dt_spin.setMinimum(0.000001)
        self.dt_spin.setMaximum(1000.0)
        self.dt_spin.setDecimals(6)
        self.dt_spin.setValue(self.config.get("dt", 0.001))
        layout.addRow("Time Step (dt):", self.dt_spin)
        
        # Time column
        self.time_column_edit = QLineEdit(self.config.get("time_column", "A"))
        self.time_column_edit.setMaxLength(2)
        layout.addRow("Time Column:", self.time_column_edit)
        
        self.tab_widget.addTab(tab, "Basic Settings")
    
    def create_units_tab(self):
        """Create the tab for units settings"""
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        # Data type
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(self.units_converter.unit_names)
        
        # Set current data type
        current_data_type = self.config.get("data_type", "Length")
        for i, type_name in enumerate(self.units_converter.unit_vars):
            if type_name == current_data_type:
                self.data_type_combo.setCurrentIndex(i)
                break
        
        layout.addRow("Data Type:", self.data_type_combo)
        
        # Connect data type change to update the unit combos
        self.data_type_combo.currentIndexChanged.connect(self.update_unit_combos)
        
        # Input units
        input_units = self.config.get("input_units", {})
        
        # Time units
        self.input_time_combo = QComboBox()
        time_units = list(self.units_converter.units["Time"].keys())
        self.input_time_combo.addItems(time_units)
        self.input_time_combo.setCurrentText(input_units.get("time", "s"))
        layout.addRow("Input Time Unit:", self.input_time_combo)
        
        # Data units
        self.input_data_combo = QComboBox()
        layout.addRow("Input Data Unit:", self.input_data_combo)
        
        # Output units
        output_units = self.config.get("output_units", {})
        
        # Output time units
        self.output_time_combo = QComboBox()
        self.output_time_combo.addItems(time_units)
        self.output_time_combo.setCurrentText(output_units.get("time", "s"))
        layout.addRow("Output Time Unit:", self.output_time_combo)
        
        # Output data units
        self.output_data_combo = QComboBox()
        layout.addRow("Output Data Unit:", self.output_data_combo)
        
        # Initialize data unit combos
        self.update_unit_combos()
        
        self.tab_widget.addTab(tab, "Units")
    
    def update_unit_combos(self):
        """Update the data unit combos based on the selected data type"""
        selected_type = self.units_converter.unit_vars[self.data_type_combo.currentIndex()]
        data_units = list(self.units_converter.units[selected_type].keys())
        
        # Save current selections if possible
        input_data_current = self.input_data_combo.currentText() if self.input_data_combo.count() > 0 else ""
        output_data_current = self.output_data_combo.currentText() if self.output_data_combo.count() > 0 else ""
        
        # Clear and repopulate
        self.input_data_combo.clear()
        self.output_data_combo.clear()
        
        self.input_data_combo.addItems(data_units)
        self.output_data_combo.addItems(data_units)
        
        # Get current units from config
        input_units = self.config.get("input_units", {})
        output_units = self.config.get("output_units", {})
        
        # Try to restore selections
        if input_data_current in data_units:
            self.input_data_combo.setCurrentText(input_data_current)
        elif "data" in input_units and input_units["data"] in data_units:
            self.input_data_combo.setCurrentText(input_units["data"])
        else:
            self.input_data_combo.setCurrentIndex(0)
        
        if output_data_current in data_units:
            self.output_data_combo.setCurrentText(output_data_current)
        elif "data" in output_units and output_units["data"] in data_units:
            self.output_data_combo.setCurrentText(output_units["data"])
        else:
            self.output_data_combo.setCurrentIndex(0)
    
    def create_data_mapping_tab(self):
        """Create the tab for data mapping settings"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Create a table for data mapping
        self.data_mapping_table = QTableWidget()
        self.data_mapping_table.setColumnCount(3)
        self.data_mapping_table.setHorizontalHeaderLabels(["Original Name", "Column", "Display Name"])
        self.data_mapping_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.data_mapping_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Fill the table with current data
        data_columns = self.config.get("data", {})
        data_names = self.config.get("data_name", {})
        
        self.data_mapping_table.setRowCount(len(data_columns))
        
        for i, (orig_name, column) in enumerate(data_columns.items()):
            self.data_mapping_table.setItem(i, 0, QTableWidgetItem(orig_name))
            self.data_mapping_table.setItem(i, 1, QTableWidgetItem(column))
            display_name = data_names.get(orig_name, orig_name)
            self.data_mapping_table.setItem(i, 2, QTableWidgetItem(display_name))
        
        layout.addWidget(self.data_mapping_table)
        
        # Add buttons for manipulating the table
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Sensor")
        add_btn.clicked.connect(self.add_sensor_mapping)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_sensor_mapping)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(tab, "Data Mapping")
    
    def add_sensor_mapping(self):
        """Add a new row to the data mapping table"""
        row = self.data_mapping_table.rowCount()
        self.data_mapping_table.setRowCount(row + 1)
        
        # Set default values
        self.data_mapping_table.setItem(row, 0, QTableWidgetItem(f"Sensor_{row+1}"))
        self.data_mapping_table.setItem(row, 1, QTableWidgetItem(""))
        self.data_mapping_table.setItem(row, 2, QTableWidgetItem(f"S{row+1}"))
    
    def remove_sensor_mapping(self):
        """Remove the selected row from the data mapping table"""
        selected_rows = self.data_mapping_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        # Sort rows in descending order to avoid index issues when removing
        rows = sorted([row.row() for row in selected_rows], reverse=True)
        
        for row in rows:
            self.data_mapping_table.removeRow(row)
    
    def create_corrections_tab(self):
        """Create the tab for data correction settings with improved layout"""
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        # Add note about processing order at the top
        note_label = QLabel("NOTE: Corrections are applied in numerical order when multiple options are enabled.")
        note_label.setWordWrap(True)
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setMinimumHeight(40)
        tab_layout.addWidget(note_label)
        
        tab_layout.addSpacing(10)
        
        correction_config = self.config.get("data_correction", {})

        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 0)
        grid_layout.setColumnStretch(2, 0)
        grid_layout.setColumnStretch(3, 1)
        grid_layout.setColumnStretch(4, 0)
        grid_layout.setColumnStretch(5, 1)
        grid_layout.setColumnMinimumWidth(1, 60)
        grid_layout.setColumnMinimumWidth(3, 100)
        grid_layout.setColumnMinimumWidth(5, 100)
        grid_layout.setVerticalSpacing(10)

        current_row = 0

        # 1. TRIM Correction
        grid_layout.addWidget(QLabel("1. Trim Time Correction:"), current_row, 0)
        self.trim_check = QCheckBox("Enable")
        self.trim_check.setChecked(correction_config.get("trim_time", {}).get("process", False))
        grid_layout.addWidget(self.trim_check, current_row, 1)

        grid_layout.addWidget(QLabel("Start:"), current_row, 2)
        self.trim_start_time = SmartQDoubleSpinBox()
        self.trim_start_time.setMinimum(-100000.0)
        self.trim_start_time.setMaximum(100000.0)
        self.trim_start_time.setSingleStep(0.1)
        self.trim_start_time.setDecimals(8)  # <-- Allow many decimals
        trim_start = correction_config.get("trim_time", {}).get("start_time")
        self.trim_start_time.setValue(0.0 if trim_start is None else float(trim_start))
        grid_layout.addWidget(self.trim_start_time, current_row, 3)

        grid_layout.addWidget(QLabel("End:"), current_row, 4)
        self.trim_end_time = SmartQDoubleSpinBox()
        self.trim_end_time.setMinimum(-100000.0)
        self.trim_end_time.setMaximum(100000.0)
        self.trim_end_time.setSingleStep(0.1)
        self.trim_end_time.setDecimals(8)  # <-- Allow many decimals
        trim_end = correction_config.get("trim_time", {}).get("end_time")
        self.trim_end_time.setValue(10.0 if trim_end is None else float(trim_end))
        grid_layout.addWidget(self.trim_end_time, current_row, 5)
        current_row += 1

        # 2. RESAMPLE Correction
        grid_layout.addWidget(QLabel("2. Resample Correction:"), current_row, 0)
        self.resample_check = QCheckBox("Enable")
        self.resample_check.setChecked(correction_config.get("resample", {}).get("process", False))
        grid_layout.addWidget(self.resample_check, current_row, 1)

        grid_layout.addWidget(QLabel("Rate (Hz):"), current_row, 2)
        self.resample_value = SmartQDoubleSpinBox()
        self.resample_value.setMinimum(0.001)
        self.resample_value.setMaximum(100000.0)
        self.resample_value.setDecimals(8)  # <-- Allow many decimals
        resample_value = correction_config.get("resample", {}).get("value")
        self.resample_value.setValue(100.0 if resample_value is None else float(resample_value))
        grid_layout.addWidget(self.resample_value, current_row, 3)

        grid_layout.addWidget(QLabel("Method:"), current_row, 4)
        self.resample_method = QComboBox()
        self.resample_method.addItems(["linear", "cubic", "nearest"])
        current_method = correction_config.get("resample", {}).get("method", "linear")
        self.resample_method.setCurrentText(current_method)
        grid_layout.addWidget(self.resample_method, current_row, 5)
        current_row += 1

        # 3. SHIFT_TIME Correction
        grid_layout.addWidget(QLabel("3. Shift Time Correction:"), current_row, 0)
        self.shift_time_check = QCheckBox("Enable")
        self.shift_time_check.setChecked(correction_config.get("shift_time", {}).get("process", False))
        grid_layout.addWidget(self.shift_time_check, current_row, 1)

        grid_layout.addWidget(QLabel("Shift (s):"), current_row, 2)
        self.shift_time_value = SmartQDoubleSpinBox()
        self.shift_time_value.setMinimum(-100000.0)
        self.shift_time_value.setMaximum(100000.0)
        self.shift_time_value.setSingleStep(0.1)
        self.shift_time_value.setDecimals(8)  # <-- Allow many decimals
        shift_time_value = correction_config.get("shift_time", {}).get("value")
        self.shift_time_value.setValue(0.0 if shift_time_value is None else float(shift_time_value))
        grid_layout.addWidget(self.shift_time_value, current_row, 3)
        current_row += 1

        # 4. ZERO_START_Y Correction
        grid_layout.addWidget(QLabel("4. Zero Start Y Correction:"), current_row, 0)
        self.zero_start_y_check = QCheckBox("Enable")
        self.zero_start_y_check.setChecked(correction_config.get("zero_start_y", {}).get("process", False))
        grid_layout.addWidget(self.zero_start_y_check, current_row, 1)

        grid_layout.addWidget(QLabel("Points:"), current_row, 2)
        self.zero_start_y_value = QSpinBox()
        self.zero_start_y_value.setMinimum(1)
        self.zero_start_y_value.setMaximum(10000000)
        zero_start_y_value = correction_config.get("zero_start_y", {}).get("value")
        self.zero_start_y_value.setValue(1 if zero_start_y_value is None else int(zero_start_y_value))
        grid_layout.addWidget(self.zero_start_y_value, current_row, 3)
        current_row += 1

        # 5. REVERSE_Y Correction
        grid_layout.addWidget(QLabel("5. Reverse Y Correction:"), current_row, 0)
        self.reverse_y_check = QCheckBox("Enable")
        self.reverse_y_check.setChecked(correction_config.get("reverse_y", {}).get("process", False))
        grid_layout.addWidget(self.reverse_y_check, current_row, 1)
        current_row += 1
        
        # 6. DETREND
        grid_layout.addWidget(QLabel("6. Detrend Correction:"), current_row, 0)
        self.detrend_check = QCheckBox("Enable")
        self.detrend_check.setChecked(correction_config.get("detrend", {}).get("process", False))
        grid_layout.addWidget(self.detrend_check, current_row, 1)

        # Store the labels as instance variables so we can reference them directly
        self.detrend_type_label = QLabel("Type:")
        grid_layout.addWidget(self.detrend_type_label, current_row, 2)

        self.detrend_type = QComboBox()
        self.detrend_type.addItems(["linear", "poly"])
        current_detrend_type = correction_config.get("detrend", {}).get("type", "linear")
        self.detrend_type.setCurrentText(current_detrend_type)
        grid_layout.addWidget(self.detrend_type, current_row, 3)

        self.detrend_degree_label = QLabel("Degree:")
        grid_layout.addWidget(self.detrend_degree_label, current_row, 4)

        self.detrend_degree = QSpinBox()
        self.detrend_degree.setMinimum(1)
        self.detrend_degree.setMaximum(10)
        self.detrend_degree.setToolTip("Polynomial degree (used only with 'poly' type)")
        detrend_degree = correction_config.get("detrend", {}).get("degree", 2)
        self.detrend_degree.setValue(detrend_degree)
        grid_layout.addWidget(self.detrend_degree, current_row, 5)

        # Create a function to update the degree field state based on the selected type
        def update_detrend_degree_visibility():
            is_poly = self.detrend_type.currentText() == "poly"
            self.detrend_degree.setEnabled(is_poly)
            
            # Update label color
            if is_poly:
                self.detrend_degree_label.setStyleSheet("")  # Reset to default
            else:
                self.detrend_degree_label.setStyleSheet("color: gray;")  # Gray out when disabled

        # Connect the function to the detrend type combobox
        self.detrend_type.currentTextChanged.connect(update_detrend_degree_visibility)

        # Initialize states
        update_detrend_degree_visibility()
        current_row += 1

        # 7. DERIVATIVE Correction
        grid_layout.addWidget(QLabel("7. Derivative Correction:"), current_row, 0)
        self.derivative_check = QCheckBox("Enable")
        self.derivative_check.setChecked(correction_config.get("derivative", {}).get("process", False))
        grid_layout.addWidget(self.derivative_check, current_row, 1)
        current_row += 1

        # 8. FILTER Correction
        grid_layout.addWidget(QLabel("8. Filter Correction:"), current_row, 0)
        self.filter_check = QCheckBox("Enable")
        self.filter_check.setChecked(correction_config.get("filter", {}).get("process", False))
        grid_layout.addWidget(self.filter_check, current_row, 1)

        grid_layout.addWidget(QLabel("Type:"), current_row, 2)
        self.filter_type = QComboBox()
        self.filter_type.addItems([
            "none", 
            "butterworth", 
            "chebyshev1", 
            "chebyshev2", 
            "elliptic", 
            "bessel", 
            "fir", 
            "savgol", 
            "moving_avg"
        ])
        current_filter_type = correction_config.get("filter", {}).get("type", "none")
        self.filter_type.setCurrentText(current_filter_type)
        grid_layout.addWidget(self.filter_type, current_row, 3)

        self.filter_params = correction_config.get("filter", {}).get("params", {})
        self.filter_params_btn = QPushButton("Parameters...")
        self.filter_params_btn.clicked.connect(self.edit_filter_parameters)
        grid_layout.addWidget(self.filter_params_btn, current_row, 5)
        current_row += 1

        # 9. STRETCH_Y Correction
        grid_layout.addWidget(QLabel("9. Stretch Y Correction:"), current_row, 0)
        self.stretch_y_check = QCheckBox("Enable")
        self.stretch_y_check.setChecked(correction_config.get("stretch_y", {}).get("process", False))
        grid_layout.addWidget(self.stretch_y_check, current_row, 1)

        grid_layout.addWidget(QLabel("Factor:"), current_row, 2)
        self.stretch_y_value = SmartQDoubleSpinBox()
        self.stretch_y_value.setMinimum(-100000.0)
        self.stretch_y_value.setMaximum(100000.0)
        self.stretch_y_value.setSingleStep(0.1)
        self.stretch_y_value.setDecimals(8)  # <-- Allow many decimals
        stretch_y_value = correction_config.get("stretch_y", {}).get("value")
        self.stretch_y_value.setValue(0.0 if stretch_y_value is None else float(stretch_y_value))
        grid_layout.addWidget(self.stretch_y_value, current_row, 3)
        current_row += 1

        # 10. NORMALIZE Correction
        grid_layout.addWidget(QLabel("10. Normalize Correction:"), current_row, 0)
        self.normalize_check = QCheckBox("Enable")
        self.normalize_check.setChecked(correction_config.get("normilized", {}).get("process", False))
        grid_layout.addWidget(self.normalize_check, current_row, 1)
        current_row += 1

        # 11. ZERO_START_TIME Correction
        grid_layout.addWidget(QLabel("11. Zero Start Time Correction:"), current_row, 0)
        self.zero_start_time_check = QCheckBox("Enable")
        self.zero_start_time_check.setChecked(correction_config.get("zero_start_time", {}).get("process", False))
        grid_layout.addWidget(self.zero_start_time_check, current_row, 1)

        tab_layout.addLayout(grid_layout)
        tab_layout.addStretch(1)

        self.tab_widget.addTab(tab, "Data Corrections")


    def browse_file(self):
        """Open a file dialog to select a data file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def get_updated_config(self):
        """Get the updated configuration from all tabs"""
        # Basic settings
        self.config["file_path"] = self.file_path_edit.text()
        self.config["seperator"] = self.separator_combo.currentText()
        self.config["decimal"] = self.decimal_combo.currentText()
        self.config["start_row"] = self.start_row_spin.value()
        self.config["end_row"] = self.end_row_spin.value()
        self.config["dt"] = self.dt_spin.value()
        self.config["time_column"] = self.time_column_edit.text()
        
        # Units
        self.config["data_type"] = self.units_converter.unit_vars[self.data_type_combo.currentIndex()]
        
        self.config["input_units"] = {
            "time": self.input_time_combo.currentText(),
            "data": self.input_data_combo.currentText()
        }
        
        self.config["output_units"] = {
            "time": self.output_time_combo.currentText(),
            "data": self.output_data_combo.currentText()
        }
        
        # Data mapping
        data = {}
        data_name = {}
        
        for row in range(self.data_mapping_table.rowCount()):
            orig_name = self.data_mapping_table.item(row, 0).text()
            column = self.data_mapping_table.item(row, 1).text()
            display_name = self.data_mapping_table.item(row, 2).text()
            
            if orig_name and column:
                data[orig_name] = column
                data_name[orig_name] = display_name
        
        self.config["data"] = data
        self.config["data_name"] = data_name
        
        # Update the data_correction section in get_updated_config
        self.config["data_correction"] = {
            # 1. TRIM TIME
            "trim_time": {
                "process": self.trim_check.isChecked(),
                "start_time": self.trim_start_time.value() if self.trim_check.isChecked() else None,
                "end_time": self.trim_end_time.value() if self.trim_check.isChecked() else None
            },
            # 2. RESAMPLE
            "resample": {
                "process": self.resample_check.isChecked(),
                "value": self.resample_value.value() if self.resample_check.isChecked() else None,
                "method": self.resample_method.currentText()
            },
            # 3. SHIFT_TIME
            "shift_time": {
                "process": self.shift_time_check.isChecked(),
                "value": self.shift_time_value.value() if self.shift_time_check.isChecked() else None
            },
            # 4. ZERO_START_Y
            "zero_start_y": {
                "process": self.zero_start_y_check.isChecked(),
                "value": self.zero_start_y_value.value()
            },
            # 5. REVERSE_Y
            "reverse_y": {
                "process": self.reverse_y_check.isChecked()
            },
            # 6. DETREND
            "detrend": {
                "process": self.detrend_check.isChecked(),
                "type": self.detrend_type.currentText(),
                "degree": self.detrend_degree.value()
            },
            # 7. DERIVATIVE
            "derivative": {
                "process": self.derivative_check.isChecked()
            },
            # 8. FILTER
            "filter": {
                "process": self.filter_check.isChecked(),
                "type": self.filter_type.currentText(),
                "params": self.filter_params
            },
            # 9. STRETCH_Y
            "stretch_y": {
                "process": self.stretch_y_check.isChecked(),
                "value": self.stretch_y_value.value() if self.stretch_y_check.isChecked() else None
            },
            # 10. NORMALIZE
            "normilized": {
                "process": self.normalize_check.isChecked()
            },
            # 11. ZERO_START_TIME
            "zero_start_time": {
                "process": self.zero_start_time_check.isChecked()
            }
        }
                
        return self.config

class ExportOptionsDialog(QDialog):
    """Dialog for configuring export options"""
    def __init__(self, sensor_names, parent=None):
        super(ExportOptionsDialog, self).__init__(parent)
        self.setWindowTitle("Export Options")
        self.setMinimumWidth(400)
        
        self.sensor_names = sensor_names
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Export type selection
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItems([
            "Export All Data", 
            "Export Selected Sensors", 
            "Export in Original Format"
        ])
        self.export_type_combo.currentIndexChanged.connect(self.update_ui)
        layout.addWidget(QLabel("Export Type:"))
        layout.addWidget(self.export_type_combo)
        
        # Sensors selection list (for "Export Selected Sensors")
        self.sensors_group = QGroupBox("Select Sensors")
        sensors_layout = QVBoxLayout(self.sensors_group)
        
        self.sensor_checkboxes = {}
        for sensor_name in sensor_names:
            checkbox = QCheckBox(sensor_name)
            checkbox.setChecked(True)
            self.sensor_checkboxes[sensor_name] = checkbox
            sensors_layout.addWidget(checkbox)
        
        # Add select all/none buttons
        buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_sensors)
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_none_sensors)
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_none_btn)
        sensors_layout.addLayout(buttons_layout)
        
        layout.addWidget(self.sensors_group)
        
        # Precision option (for CSV exports)
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("Decimal Precision:"))
        self.precision_spin = QSpinBox()
        self.precision_spin.setMinimum(1)
        self.precision_spin.setMaximum(16)
        self.precision_spin.setValue(6)
        precision_layout.addWidget(self.precision_spin)
        layout.addLayout(precision_layout)
        
        # ADD SECTION - Export config option
        self.export_config_checkbox = QCheckBox("Export configuration file")
        self.export_config_checkbox.setChecked(True)
        layout.addWidget(self.export_config_checkbox)
        # END OF NEW SECTION
        
        # Output path
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        output_layout.addWidget(self.output_path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_btn)
        layout.addWidget(QLabel("Output Path:"))
        layout.addLayout(output_layout)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Export")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)
        layout.addLayout(buttons_layout)
        
        # Initial update
        self.update_ui()
    
    def update_ui(self):
        """Update UI based on selected export type"""
        export_type = self.export_type_combo.currentIndex()
        
        # Show/hide sensors selection
        self.sensors_group.setVisible(export_type == 1)  # Only for "Export Selected Sensors"
    
    def select_all_sensors(self):
        """Select all sensors"""
        for checkbox in self.sensor_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_none_sensors(self):
        """Deselect all sensors"""
        for checkbox in self.sensor_checkboxes.values():
            checkbox.setChecked(False)
    
    def browse_output(self):
        """Open a dialog to select output file path"""
        export_type = self.export_type_combo.currentIndex()
        file_filter = "CSV Files (*.csv)"
        
        if export_type == 2:  # Original Format
            file_filter = "CSV Files (*.csv);;All Files (*)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", file_filter
        )
        
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def get_export_config(self):
        """Get the export configuration"""
        export_type = self.export_type_combo.currentIndex()
        output_path = self.output_path_edit.text()
        precision = self.precision_spin.value()
        
        selected_sensors = []
        if export_type == 1:  # Export Selected Sensors
            for sensor_name, checkbox in self.sensor_checkboxes.items():
                if checkbox.isChecked():
                    selected_sensors.append(sensor_name)
        
        return {
            "export_type": export_type,
            "output_path": output_path,
            "precision": precision,
            "selected_sensors": selected_sensors,
            "export_config": self.export_config_checkbox.isChecked() ## ADD LINE Filter
        }

class ReplicaXSensorDataReaderGUI(QMainWindow):
    """Main GUI application for ReplicaXSensorDataReader"""
    def __init__(self):
        super(ReplicaXSensorDataReaderGUI, self).__init__()
        
        # Initialize ReplicaXSensorDataReader instance
        self.sensor_data = ReplicaXSensorDataReader()
        
        # Set of colors for dynamic sensor coloring
        self.available_colors = [
            "blue", "green", "red", "purple", "orange", 
            "brown", "cyan", "magenta", "darkblue", "darkgreen",
            "darkred", "darkmagenta", "darkorange", "darkgray"
        ]
        self.sensor_colors = {}  # Will be populated dynamically
        
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI components"""
        self.setWindowTitle("ReplicaXSensorDataReader Analyzer")
        self.setMinimumSize(1200, 845)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(self.main_splitter)
        
        # Create tab widget for main content
        self.main_tabs = QTabWidget()
        self.main_splitter.addWidget(self.main_tabs)
        
        # Create data viewer tab
        self.create_data_viewer_tab()
        
        # Create config editor tab
        self.create_config_editor_tab()
        
        # Create lower section for log output
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)
        self.main_splitter.addWidget(lower_widget)
        
        # Log viewer
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        self.log_text = LogTextEdit()
        log_layout.addWidget(self.log_text)
        lower_layout.addWidget(log_group)
        
        # Set the initial splitter sizes
        self.main_splitter.setSizes([600, 200])  # 3/4 for upper, 1/4 for lower
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Initialize log
        self.log_message("Application started")
        
        # Initialize live update timer
        self.real_time_update_timer = QTimer(self)
        self.real_time_update_timer.timeout.connect(self.process_data)
    
    def reset_application_state(self):
        """Reset the application state before loading a new configuration"""
        self.log_message("Resetting application state")
        
        # Stop real time update if running
        if hasattr(self, 'real_time_update_timer') and self.real_time_update_timer.isActive():
            self.real_time_update_timer.stop()
            self.real_time_update_btn.setChecked(False)
            self.real_time_update_btn.setText("Start Real Time Update")
        
        # Reset ReplicaXSensorDataReader object
        self.sensor_data = ReplicaXSensorDataReader()
        
        # Clear all plots
        if hasattr(self, 'combined_canvas'):
            self.combined_canvas.clear_plot()
        
        # Clear individual plots
        if hasattr(self, 'individual_plots_layout'):
            for i in reversed(range(self.individual_plots_layout.count())):
                item = self.individual_plots_layout.itemAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        
        # Clear sensor selection
        if hasattr(self, 'sensor_container_layout'):
            for i in reversed(range(self.sensor_container_layout.count())):
                item = self.sensor_container_layout.itemAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
            # Add a placeholder after clearing
            if hasattr(self, 'sensor_container_layout'):
                label = QLabel("No sensors defined")
                self.sensor_container_layout.addWidget(label)
        
        # Clear sensor colors and checkboxes
        self.sensor_colors = {}
        self.sensor_checkboxes = {}
        
        # Reset config summary
        if hasattr(self, 'config_summary'):
            self.config_summary.setText("No configuration loaded")
        
        # Reset config text editor
        if hasattr(self, 'config_text_editor'):
            self.config_text_editor.setPlainText("")
        
        # Reset status bar
        self.statusBar().showMessage("Ready")
        
        # Disable all buttons except Load Configuration
        if hasattr(self, 'export_btn'):
            self.export_btn.setEnabled(False)
        if hasattr(self, 'process_btn'):
            self.process_btn.setEnabled(False)
        if hasattr(self, 'real_time_update_btn'):
            self.real_time_update_btn.setEnabled(False)
        if hasattr(self, 'select_all_btn'):
            self.select_all_btn.setEnabled(False)
        if hasattr(self, 'select_none_btn'):
            self.select_none_btn.setEnabled(False)
        
        # Clear the log
        if hasattr(self, 'log_text'):
            self.log_text.clear()
            self.log_message("Application reset successfully", "SUCCESS")

    def create_data_viewer_tab(self):
        """Create the data viewer tab"""
        data_viewer = QWidget()
        layout = QVBoxLayout(data_viewer)  # Change to vertical layout to contain the splitter
        
        # Create horizontal splitter
        self.data_viewer_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.data_viewer_splitter)
        
        # Left panel (controls and selection)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File controls
        file_controls = QGroupBox("File Controls")
        file_layout = QVBoxLayout(file_controls)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_config_file)
        file_layout.addWidget(load_btn)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config_file)
        file_layout.addWidget(save_btn)
        
        # Export button with dropdown menu
        self.export_btn = QToolButton()
        self.export_btn.setText("Export Data")
        self.export_btn.setPopupMode(QToolButton.InstantPopup)
        self.export_btn.setEnabled(False)  # Initially disabled
        export_menu = QMenu(self.export_btn)
        
        export_all_action = QAction("Export All Data", self)
        export_all_action.triggered.connect(lambda: self.export_data(0))
        export_menu.addAction(export_all_action)
        
        export_selected_action = QAction("Export Selected Sensors", self)
        export_selected_action.triggered.connect(lambda: self.export_data(1))
        export_menu.addAction(export_selected_action)
        
        export_original_action = QAction("Export in Original Format", self)
        export_original_action.triggered.connect(lambda: self.export_data(2))
        export_menu.addAction(export_original_action)
        
        self.export_btn.setMenu(export_menu)
        self.export_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_layout.addWidget(self.export_btn)
        
        # Add process button to file controls
        self.process_btn = QPushButton("Process Data")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_data)
        file_layout.addWidget(self.process_btn)
        
        # Add real time update controls
        real_time_update_group = QGroupBox("Real Time Update")
        real_time_update_layout = QVBoxLayout(real_time_update_group)
        
        # Create horizontal layout for live update controls
        live_control_layout = QHBoxLayout()
        
        # Add real time update toggle button
        self.real_time_update_btn = QPushButton("Start Real Time Update")
        self.real_time_update_btn.setEnabled(False)
        self.real_time_update_btn.setCheckable(True)
        self.real_time_update_btn.clicked.connect(self.toggle_real_time_update)
        live_control_layout.addWidget(self.real_time_update_btn)
        
        # Add interval spinbox
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval (s):"))
        self.update_interval_spin = QDoubleSpinBox()
        self.update_interval_spin.setMinimum(0.1)
        self.update_interval_spin.setMaximum(60.0)
        self.update_interval_spin.setValue(1.0)
        self.update_interval_spin.setSingleStep(0.1)
        self.update_interval_spin.valueChanged.connect(self.update_timer_interval)
        interval_layout.addWidget(self.update_interval_spin)
        
        # Add layouts to live update group
        real_time_update_layout.addLayout(live_control_layout)
        real_time_update_layout.addLayout(interval_layout)
        
        # Add live update group to file controls
        file_layout.addWidget(real_time_update_group)
        
        left_layout.addWidget(file_controls)
        
        # Configuration summary
        self.config_summary = QTextEdit()
        self.config_summary.setReadOnly(True)
        left_layout.addWidget(QLabel("Configuration Summary"))
        left_layout.addWidget(self.config_summary)
        
        # Sensor selection group with scroll area
        self.sensor_selection_group = QGroupBox("Sensor Selection")
        sensor_selection_layout = QVBoxLayout(self.sensor_selection_group)

        # Add buttons at the top (outside scroll area)
        buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_sensors)
        self.select_all_btn.setEnabled(False)  # Initially disabled

        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none_sensors)
        self.select_none_btn.setEnabled(False)  # Initially disabled

        buttons_layout.addWidget(self.select_all_btn)
        buttons_layout.addWidget(self.select_none_btn)
        sensor_selection_layout.addLayout(buttons_layout)

        # Create a scroll area for the sensor checkboxes
        self.sensor_scroll_area = QScrollArea()
        self.sensor_scroll_area.setWidgetResizable(True)
        self.sensor_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sensor_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sensor_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sensor_scroll_area.setMinimumHeight(150)  # Set minimum height to show several sensors

        # Create widget to hold the checkboxes
        self.sensor_container = QWidget()
        self.sensor_container_layout = QVBoxLayout(self.sensor_container)
        self.sensor_container_layout.setContentsMargins(0, 0, 0, 0)
        self.sensor_container_layout.setSpacing(2)  # Compact spacing
        # Don't add stretch here - we want it to fill naturally

        self.sensor_scroll_area.setWidget(self.sensor_container)
        sensor_selection_layout.addWidget(self.sensor_scroll_area, 1)  # Give it a stretch factor

        # Make sure the group expands with available space
        self.sensor_selection_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left_layout.addWidget(self.sensor_selection_group, 1)  # Give it a stretch factor
        
        # Add stretcher to ensure widgets stay at the top
        left_layout.addStretch()
        
        # Right panel for plots
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tab widget for different plot views
        self.plot_tabs = QTabWidget()
        
        # Combined plot tab
        self.combined_plot_widget = QWidget()
        combined_plot_layout = QVBoxLayout(self.combined_plot_widget)
        self.combined_canvas = SensorPlotCanvas(self.combined_plot_widget, width=5, height=4)
        self.combined_toolbar = NavigationToolbar(self.combined_canvas, self.combined_plot_widget)
        combined_plot_layout.addWidget(self.combined_toolbar)
        combined_plot_layout.addWidget(self.combined_canvas)
        self.combined_canvas.set_labels(x_label="Time (s)", y_label="Value", title="Combined Sensor Data")
        self.plot_tabs.addTab(self.combined_plot_widget, "Combined Plot")
        
        # Individual plots tab - using grid layout
        self.individual_plots_widget = QScrollArea()
        self.individual_plots_widget.setWidgetResizable(True)
        self.individual_plots_container = QWidget()
        self.individual_plots_layout = QGridLayout(self.individual_plots_container)
        self.individual_plots_widget.setWidget(self.individual_plots_container)
        self.plot_tabs.addTab(self.individual_plots_widget, "Individual Plots")
        
        right_layout.addWidget(self.plot_tabs)
        
        # Add panels to the splitter instead of directly to the layout
        self.data_viewer_splitter.addWidget(left_panel)
        self.data_viewer_splitter.addWidget(right_panel)
        
        # Set initial sizes (e.g., 1:3 ratio)
        self.data_viewer_splitter.setSizes([300, 900])
        
        # Add to main tabs
        self.main_tabs.addTab(data_viewer, "Data Viewer")

    def create_config_editor_tab(self):
        """Create the configuration editor tab"""
        config_editor = QWidget()
        layout = QVBoxLayout(config_editor)
        
        # Add message about the advanced editor
        info_label = QLabel("Use this tab to directly edit the configuration JSON. For a more user-friendly interface, use the 'Edit Configuration' button.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add open editor button
        edit_config_btn = QPushButton("Edit Configuration")
        edit_config_btn.clicked.connect(self.open_config_editor)
        layout.addWidget(edit_config_btn)
        
        # Add the config text editor
        self.config_text_editor = QTextEdit()
        self.config_text_editor.setAcceptRichText(False)
        self.config_text_editor.setFont(QFont("Courier New", 10))
        layout.addWidget(self.config_text_editor)
        
        # Add update button
        update_config_btn = QPushButton("Update Configuration")
        update_config_btn.clicked.connect(self.update_config_from_text)
        layout.addWidget(update_config_btn)
        
        # Add to main tabs
        self.main_tabs.addTab(config_editor, "Configuration Editor")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open Configuration...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_config_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Configuration...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_config_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu("Export Data")
        
        export_all_action = QAction("Export &All Data...", self)
        export_all_action.triggered.connect(lambda: self.export_data(0))
        export_menu.addAction(export_all_action)
        
        export_selected_action = QAction("Export &Selected Sensors...", self)
        export_selected_action.triggered.connect(lambda: self.export_data(1))
        export_menu.addAction(export_selected_action)
        
        export_original_action = QAction("Export in &Original Format...", self)
        export_original_action.triggered.connect(lambda: self.export_data(2))
        export_menu.addAction(export_original_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        edit_config_action = QAction("&Edit Configuration...", self)
        edit_config_action.triggered.connect(self.open_config_editor)
        edit_menu.addAction(edit_config_action)
        
        correction_action = QAction("Data &Correction Settings...", self)
        correction_action.triggered.connect(self.edit_correction_settings)
        edit_menu.addAction(correction_action)
        
        units_action = QAction("&Units Settings...", self)
        units_action.triggered.connect(self.edit_units_settings)
        edit_menu.addAction(units_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        process_action = QAction("&Process Data", self)
        process_action.setShortcut("F5")
        process_action.triggered.connect(self.process_data)
        tools_menu.addAction(process_action)
        
        # Add filter comparison action
        filter_comparison_action = QAction("Filter &Comparison...", self)
        filter_comparison_action.triggered.connect(self.open_filter_comparison)
        tools_menu.addAction(filter_comparison_action)

        clear_plots_action = QAction("&Clear Plots", self)
        clear_plots_action.triggered.connect(self.clear_plots)
        tools_menu.addAction(clear_plots_action)

        reset_sensors_action = QAction("&Reset Sensors", self)
        reset_sensors_action.setShortcut("Ctrl+R")
        reset_sensors_action.triggered.connect(self.reset_application_state)
        tools_menu.addAction(reset_sensors_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def open_filter_comparison(self):
        """Open the filter comparison tool window"""
        if not hasattr(self.sensor_data, 'processed_data') or not self.sensor_data.processed_data:
            QMessageBox.warning(self, "No Data", "Please process data first before using the Filter Comparison tool.")
            return
        
        # Create and show the filter comparison window
        self.filter_comparison_window = FilterComparisonWindow(self.sensor_data, self)
        self.filter_comparison_window.show()

    def toggle_real_time_update(self):
        """Toggle the live update functionality"""
        if self.real_time_update_btn.isChecked():
            # Start the timer
            interval_ms = int(self.update_interval_spin.value() * 1000)  # Convert to milliseconds
            self.real_time_update_timer.start(interval_ms)
            self.real_time_update_btn.setText("Stop Real Time Update")
            self.log_message("Real Time update started", "INFO")
            
            # Process data immediately when starting
            self.process_data()
        else:
            # Stop the timer
            self.real_time_update_timer.stop()
            self.real_time_update_btn.setText("Start Real Time Update")
            self.log_message("Real Time update stopped", "INFO")

    def toggle_real_time_update_from_menu(self, checked):
        """Toggle live update from menu action"""
        # Sync the button state with the menu action
        self.real_time_update_btn.setChecked(checked)
        self.toggle_real_time_update()

    def update_timer_interval(self, value):
        """Update the timer interval when the spinbox value changes"""
        if self.real_time_update_timer.isActive():
            interval_ms = int(value * 1000)  # Convert to milliseconds
            self.real_time_update_timer.setInterval(interval_ms)
            self.log_message(f"Update interval changed to {value} seconds", "INFO")
    
    def load_config_file(self):
        """Open a dialog to select and load a configuration file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration File", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.load_config_from_file(file_path)
    
    def load_config_from_file(self, file_path):
        """Load configuration from the specified file"""
        try:
            # Reset the application state first
            self.reset_application_state()
            
            self.log_message(f"Loading configuration from {file_path}")
            
            # Read the JSON file
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Update the ReplicaXSensorDataReader object
            success = self.sensor_data.load_config_from_dict(config)
            
            if success:
                self.log_message(f"Configuration loaded successfully", "SUCCESS")
                self.update_config_summary()
                self.update_config_text_editor()
                self.update_sensor_selection()
                # Enable all buttons
                if hasattr(self, 'export_btn'):
                    self.export_btn.setEnabled(True)
                if hasattr(self, 'process_btn'):
                    self.process_btn.setEnabled(True)
                if hasattr(self, 'real_time_update_btn'):
                    self.real_time_update_btn.setEnabled(True)
                if hasattr(self, 'select_all_btn'):
                    self.select_all_btn.setEnabled(True)
                if hasattr(self, 'select_none_btn'):
                    self.select_none_btn.setEnabled(True)
                self.statusBar().showMessage(f"Loaded: {file_path}")
            else:
                self.log_message("Failed to load configuration", "ERROR")
        except Exception as e:
            self.log_message(f"Error loading configuration: {e}", "ERROR")
    
    def save_config_file(self):
        """Open a dialog to save the current configuration"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            QMessageBox.warning(self, "No Configuration", "No configuration to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.sensor_data.config, f, indent=4)
                self.log_message(f"Configuration saved to {file_path}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Error saving configuration: {e}", "ERROR")
    
    def export_data(self, export_type=0):
        """Export data with the specified export type"""
        if not hasattr(self.sensor_data, 'processed_data') or not self.sensor_data.processed_data:
            QMessageBox.warning(self, "No Data", "No processed data to export.")
            return
        
        sensor_names = list(self.sensor_data.processed_data.keys())
        dialog = ExportOptionsDialog(sensor_names, self)
        
        # Pre-select the export type
        dialog.export_type_combo.setCurrentIndex(export_type)
        
        if dialog.exec() == QDialog.Accepted:
            export_config = dialog.get_export_config()
            output_path = export_config["output_path"]
            
            if not output_path:
                QMessageBox.warning(self, "No Output Path", "Please select an output file path.")
                return
            
            try:
                if export_config["export_type"] == 0:  # Export All Data
                    # UPDATE THIS LINE to pass export_config parameter
                    success = self.sensor_data.export_to_csv(
                        output_path, 
                        export_config["precision"],
                        export_config["export_config"]  # Add this parameter
                    )
                    if success:
                        self.log_message(f"All data exported to {output_path}", "SUCCESS")
                    else:
                        self.log_message("Failed to export all data", "ERROR")
                        
                elif export_config["export_type"] == 1:  # Export Selected Sensors
                    selected_sensors = export_config["selected_sensors"]
                    if not selected_sensors:
                        QMessageBox.warning(self, "No Sensors Selected", "Please select at least one sensor to export.")
                        return
                        
                    # UPDATE THIS LINE to pass export_config parameter
                    success = self.sensor_data.export_selected_sensors_to_csv(
                        output_path, 
                        selected_sensors, 
                        export_config["precision"],
                        export_config["export_config"]  # Add this parameter
                    )
                    if success:
                        self.log_message(f"Selected sensors exported to {output_path}", "SUCCESS")
                    else:
                        self.log_message("Failed to export selected sensors", "ERROR")
                        
                elif export_config["export_type"] == 2:  # Export in Original Format
                    # UPDATE THIS LINE to pass export_config parameter
                    success = self.sensor_data.export_processed_data_in_original_format(
                        output_path, 
                        export_config["precision"],
                        export_config["export_config"]  # Add this parameter
                    )
                    if success:
                        self.log_message(f"Data exported in original format to {output_path}", "SUCCESS")
                    else:
                        self.log_message("Failed to export data in original format", "ERROR")
                    
            except Exception as e:
                self.log_message(f"Error exporting data: {e}", "ERROR")

    def update_config_summary(self):
        """Update the configuration summary"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            self.config_summary.setText("No configuration loaded")
            return
        
        config = self.sensor_data.config
        summary = "<html><body>"
        
        # Add basic properties
        summary += "<h3>Basic Settings</h3>"
        summary += f"<p><b>File:</b> {os.path.basename(config.get('file_path', ''))}</p>"
        summary += f"<p><b>Rows:</b> {config.get('start_row', '')} to {config.get('end_row', '')}</p>"
        summary += f"<p><b>Time Column:</b> {config.get('time_column', '')}</p>"
        summary += f"<p><b>Sample Rate:</b> {1/config.get('dt', 1):.2f} Hz</p>"
        
        # Add units information
        summary += "<h3>Units</h3>"
        input_units = config.get("input_units", {})
        output_units = config.get("output_units", {})
        data_type = config.get("data_type", "")
        
        summary += f"<p><b>Data Type:</b> {data_type.replace('_', ' ')}</p>"
        summary += f"<p><b>Input Units:</b> {input_units.get('data', '')} ({input_units.get('time', '')})</p>"
        summary += f"<p><b>Output Units:</b> {output_units.get('data', '')} ({output_units.get('time', '')})</p>"
        
        # Add data corrections
        summary += "<h3>Corrections</h3>"
        corrections = config.get("data_correction", {})
        
        # Add this in the update_config_summary method where it builds the active_corrections list
        active_corrections = []

        # 1. TRIM TIME
        if corrections.get("trim_time", {}).get("process", False):
            start_time = corrections.get("trim_time", {}).get("start_time", "")
            end_time = corrections.get("trim_time", {}).get("end_time", "")
            active_corrections.append(f"1. Trim Time (Range: {start_time} to {end_time})")

        # 2. RESAMPLE
        if corrections.get("resample", {}).get("process", False):
            value = corrections.get("resample", {}).get("value", "")
            method = corrections.get("resample", {}).get("method", "linear")
            active_corrections.append(f"2. Resample ({value} Hz, Method: {method})")

        # 3. SHIFT_TIME
        if corrections.get("shift_time", {}).get("process", False):
            value = corrections.get("shift_time", {}).get("value", "")
            active_corrections.append(f"3. Shift Time (Value: {value})")

        # 4. ZERO_START_Y
        if corrections.get("zero_start_y", {}).get("process", False):
            value = corrections.get("zero_start_y", {}).get("value", "")
            active_corrections.append(f"4. Zero Start Y (Points: {value})")

        # 5. REVERSE_Y
        if corrections.get("reverse_y", {}).get("process", False):
            active_corrections.append("5. Reverse Y")

        # 6. DETREND 
        if corrections.get("detrend", {}).get("process", False):
            detrend_type = corrections.get("detrend", {}).get("type", "linear")
            detrend_degree = corrections.get("detrend", {}).get("degree", 2)
            detrend_info = f"5. Detrend ({detrend_type}"
            if detrend_type == "poly":
                detrend_info += f", degree: {detrend_degree}"
            detrend_info += ")"
            active_corrections.append(detrend_info)

        # 7. DERIVATIVE
        if corrections.get("derivative", {}).get("process", False):
            active_corrections.append("7. Derivative")

        # 8. FILTER
        if corrections.get("filter", {}).get("process", False):
            filter_type = corrections.get("filter", {}).get("type", "none")
            filter_params = corrections.get("filter", {}).get("params", {})
            params_str = ", ".join([f"{k}: {v}" for k, v in filter_params.items()])
            active_corrections.append(f"8. Filter ({filter_type}{', ' + params_str if params_str else ''})")

        # 9. STRETCH_Y
        if corrections.get("stretch_y", {}).get("process", False):
            value = corrections.get("stretch_y", {}).get("value", "")
            active_corrections.append(f"9. Stretch Y (Factor: {value})")

        # 10. NORMALIZE
        if corrections.get("normilized", {}).get("process", False):
            active_corrections.append("10. Normalize")

        # 11. ZERO_START_TIME
        if corrections.get("zero_start_time", {}).get("process", False):
            active_corrections.append("11. Zero Start Time")

        if active_corrections:
            summary += "<ul>"
            for correction in active_corrections:
                summary += f"<li>{correction}</li>"
            summary += "</ul>"
        else:
            summary += "<p>No active corrections</p>"
        
        # Add sensors
        summary += "<h3>Sensors</h3>"
        data_columns = config.get("data", {})
        data_names = config.get("data_name", {})
        
        if data_columns:
            summary += "<ul>"
            for orig_name, column in data_columns.items():
                display_name = data_names.get(orig_name, orig_name)
                summary += f"<li>{orig_name} → {display_name} (Column {column})</li>"
            summary += "</ul>"
        else:
            summary += "<p>No sensors defined</p>"
        
        summary += "</body></html>"
        self.config_summary.setHtml(summary)
    
    def update_config_text_editor(self):
        """Update the config text editor with the current configuration"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            self.config_text_editor.setPlainText("")
            return
        
        try:
            # Format the JSON for display
            formatted_json = json.dumps(self.sensor_data.config, indent=4)
            self.config_text_editor.setPlainText(formatted_json)
        except Exception as e:
            self.log_message(f"Error updating config editor: {e}", "ERROR")
    
    def update_config_from_text(self):
        """Update the configuration from the text editor"""
        try:
            # Parse the JSON from the text editor
            config_text = self.config_text_editor.toPlainText()
            if not config_text.strip():
                QMessageBox.warning(self, "Empty Configuration", "Configuration cannot be empty.")
                return
            
            config = json.loads(config_text)
            
            # Update the ReplicaXSensorDataReader object
            success = self.sensor_data.load_config_from_dict(config)
            
            if success:
                self.log_message("Configuration updated from text editor", "SUCCESS")
                self.update_config_summary()
                self.update_sensor_selection()
                self.process_btn.setEnabled(True)
            else:
                self.log_message("Failed to update configuration", "ERROR")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Invalid JSON format: {e}")
        except Exception as e:
            self.log_message(f"Error updating configuration: {e}", "ERROR")
    
    def open_config_editor(self):
        """Open the configuration editor dialog"""
        if not hasattr(self.sensor_data, 'config'):
            # Initialize with empty config if none exists
            self.sensor_data.config = {}
        
        # Create and show the dialog
        dialog = ConfigurationEditorDialog(self.sensor_data.config, self.sensor_data.converter, self)
        if dialog.exec() == QDialog.Accepted:
            # Get updated config
            new_config = dialog.get_updated_config()
            
            # Update the ReplicaXSensorDataReader object
            success = self.sensor_data.load_config_from_dict(new_config)
            
            if success:
                self.log_message("Configuration updated from editor", "SUCCESS")
                self.update_config_summary()
                self.update_config_text_editor()
                self.update_sensor_selection()
                self.process_btn.setEnabled(True)
            else:
                self.log_message("Failed to update configuration", "ERROR")
    
    def update_sensor_selection(self):
        """Update the sensor selection checkboxes"""
        # Clear existing checkboxes
        for i in reversed(range(self.sensor_container_layout.count())):
            item = self.sensor_container_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Clear existing checkboxes dictionary
        self.sensor_checkboxes = {}
        
        # Get sensor names from config (we might not have processed data yet)
        config_sensor_names = []
        for orig_name, display_name in self.sensor_data.config.get("data_name", {}).items():
            config_sensor_names.append(display_name)
        
        # Get sensor names from processed data
        processed_sensor_names = []
        if hasattr(self.sensor_data, 'processed_data') and self.sensor_data.processed_data:
            processed_sensor_names = list(self.sensor_data.processed_data.keys())
        
        # Use processed names if available, otherwise use config names
        sensor_names = processed_sensor_names if processed_sensor_names else config_sensor_names
        
        # Initialize sensor colors if needed
        self.assign_colors_to_sensors(sensor_names)
        
        if not sensor_names:
            # Add a placeholder
            label = QLabel("No sensors defined")
            self.sensor_container_layout.addWidget(label)
            return
        
        # Add checkboxes for each sensor
        for sensor_name in sensor_names:
            checkbox = QCheckBox(sensor_name)
            checkbox.setChecked(True)  # Default to checked
            checkbox.stateChanged.connect(self.update_plots)
            
            self.sensor_checkboxes[sensor_name] = checkbox
            self.sensor_container_layout.addWidget(checkbox)
        
        # Add some empty space at the end if needed
        self.sensor_container_layout.addStretch(1)
    
    def assign_colors_to_sensors(self, sensor_names):
        """Assign colors to sensors"""
        # Clear existing color assignments
        self.sensor_colors = {}
        
        # Assign colors to sensors
        for i, sensor_name in enumerate(sensor_names):
            # Use predefined colors in rotation
            color_idx = i % len(self.available_colors)
            self.sensor_colors[sensor_name] = self.available_colors[color_idx]
    
    def select_all_sensors(self):
        """Select all sensors"""
        for checkbox in self.sensor_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_none_sensors(self):
        """Deselect all sensors"""
        for checkbox in self.sensor_checkboxes.values():
            checkbox.setChecked(False)
    
    def process_data(self):
        """Process the sensor data and update plots"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            self.log_message("No configuration loaded", "ERROR")
            return
        
        try:
            # Process the data
            success = self.sensor_data.process_data()
            
            if success:
                # Get the log from ReplicaXSensorDataReader and display it
                self.log_text.clear()
                for line in self.sensor_data.log.split('\n'):
                    if line.startswith("INFO:"):
                        self.log_message(line[6:].strip(), "INFO")
                    elif line.startswith("WARNING:"):
                        self.log_message(line[9:].strip(), "WARNING")
                    elif line.startswith("ERROR:"):
                        self.log_message(line[7:].strip(), "ERROR")
                    else:
                        self.log_message(line.strip())
                
                # Update summary in the status bar
                self.update_status_summary()
                
                # Update sensor selection (in case it changed)
                self.update_sensor_selection()
                
                # Update plots
                self.update_plots()
                
                self.log_message("Data processed successfully", "SUCCESS")
            else:
                self.log_message("Failed to process data", "ERROR")
        except Exception as e:
            self.log_message(f"Error processing data: {e}", "ERROR")
            import traceback
            self.log_message(traceback.format_exc(), "ERROR")
    
    def update_status_summary(self):
        """Update the status bar with summary information"""
        if not hasattr(self.sensor_data, 'processed_data') or not self.sensor_data.processed_data:
            self.statusBar().showMessage("No data processed")
            return
        
        # Get the number of sensors and data points
        num_sensors = len(self.sensor_data.processed_data)
        num_points = 0
        if hasattr(self.sensor_data, 'time_array') and self.sensor_data.time_array is not None:
            num_points = len(self.sensor_data.time_array)
        
        # Display summary
        self.statusBar().showMessage(f"Processed {num_points} data points for {num_sensors} sensors")
    
    def edit_correction_settings(self):
        """Open the configuration editor directly to the corrections tab"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            QMessageBox.warning(self, "No Configuration", "No configuration to edit.")
            return
        
        # Create and show the main configuration dialog
        dialog = ConfigurationEditorDialog(self.sensor_data.config, self.sensor_data.converter, self)
        
        # Select the corrections tab (index 3)
        dialog.tab_widget.setCurrentIndex(3)
        
        if dialog.exec() == QDialog.Accepted:
            # Get updated config
            new_config = dialog.get_updated_config()
            
            # Update the ReplicaXSensorDataReader object
            success = self.sensor_data.load_config_from_dict(new_config)
            
            if success:
                self.log_message("Configuration updated from editor", "SUCCESS")
                self.update_config_summary()
                self.update_config_text_editor()
                self.update_sensor_selection()
                self.process_btn.setEnabled(True)
            else:
                self.log_message("Failed to update configuration", "ERROR")
    
    def edit_units_settings(self):
        """Open the configuration editor directly to the units tab"""
        if not hasattr(self.sensor_data, 'config') or not self.sensor_data.config:
            QMessageBox.warning(self, "No Configuration", "No configuration to edit.")
            return
        
        # Create and show the main configuration dialog
        dialog = ConfigurationEditorDialog(self.sensor_data.config, self.sensor_data.converter, self)
        
        # Select the units tab (index 1)
        dialog.tab_widget.setCurrentIndex(1)
        
        if dialog.exec() == QDialog.Accepted:
            # Get updated config
            new_config = dialog.get_updated_config()
            
            # Update the ReplicaXSensorDataReader object
            success = self.sensor_data.load_config_from_dict(new_config)
            
            if success:
                self.log_message("Configuration updated from editor", "SUCCESS")
                self.update_config_summary()
                self.update_config_text_editor()
                self.update_sensor_selection()
                self.process_btn.setEnabled(True)
            else:
                self.log_message("Failed to update configuration", "ERROR")
    
    def update_plots(self):
        """Update all plots based on selected sensors"""
        if not hasattr(self.sensor_data, 'processed_data') or not self.sensor_data.processed_data:
            return
        
        # Clear all plots
        self.combined_canvas.clear_plot()
        
        # Update the individual plots grid
        self.update_individual_plots()
        
        # Get selected sensors
        selected_sensors = []
        for sensor_name, checkbox in self.sensor_checkboxes.items():
            if checkbox.isChecked():
                selected_sensors.append(sensor_name)
        
        # Update combined plot
        for sensor_name in selected_sensors:
            time_array, data_array = self.sensor_data.get_xy(sensor_name)
            # Use assigned colors for sensors
            color = self.sensor_colors.get(sensor_name)
            self.combined_canvas.plot_sensor(time_array, data_array, sensor_name, color)
        
        # Update units and titles
        output_time_unit = self.sensor_data.config.get("output_units", {}).get("time", "s")
        output_data_unit = self.sensor_data.config.get("output_units", {}).get("data", "m")
        data_type = self.sensor_data.config.get("data_type", "Length").replace("_", " ")
        
        # Update combined plot labels
        self.combined_canvas.set_labels(
            x_label=f"Time ({output_time_unit})",
            y_label=f"{data_type} ({output_data_unit})",
            title="Combined Sensor Data"
        )
    
    def update_individual_plots(self):
        """Create or update individual plots for each sensor with professional appearance"""
        # Clear existing plots widget content
        for i in reversed(range(self.individual_plots_layout.count())):
            item = self.individual_plots_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        if not hasattr(self.sensor_data, 'processed_data') or not self.sensor_data.processed_data:
            # Add a placeholder
            label = QLabel("No data processed")
            self.individual_plots_layout.addWidget(label, 0, 0)
            return
        
        # Get selected sensors
        selected_sensors = []
        for sensor_name, checkbox in self.sensor_checkboxes.items():
            if checkbox.isChecked():
                selected_sensors.append(sensor_name)
        
        if not selected_sensors:
            # Add a placeholder if no sensors are selected
            label = QLabel("No sensors selected")
            self.individual_plots_layout.addWidget(label, 0, 0)
            return
        
        # Calculate grid layout - maximum 4 rows for better visibility
        n_sensors = len(selected_sensors)
        n_rows = min(n_sensors, 4)  # Maximum 4 rows
        n_cols = int(np.ceil(n_sensors / n_rows))
        
        # Create a main widget to hold the figure and toolbar
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to use full space
        
        # Create a single figure for all subplots
        width = 9  # Width for figure
        height = 2.5 * n_rows  # Height per row
        
        fig = Figure(figsize=(width, height), dpi=100, facecolor='white')
        canvas = FigureCanvas(fig)
        
        # Add a toolbar for the entire figure
        toolbar = NavigationToolbar(canvas, plot_widget)
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(canvas)
        
        # Get output units and data type
        output_time_unit = self.sensor_data.config.get("output_units", {}).get("time", "s")
        output_data_unit = self.sensor_data.config.get("output_units", {}).get("data", "m")
        data_type = self.sensor_data.config.get("data_type", "Length").replace("_", " ")
        
        # Set figure title with more detailed information
        config_name = os.path.basename(self.sensor_data.config.get("file_path", ""))
        fig.suptitle(f"Sensor Data Analysis: {config_name}", 
                    fontsize=14, fontweight='bold', y=0.98)
        
        # Create a more professional layout with appropriate spacing
        fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.9, 
                            wspace=0.3, hspace=0.4)
        
        # Create subplots for each sensor with appropriate spacing
        axes = []
        for i in range(n_sensors):
            ax = fig.add_subplot(n_rows, n_cols, i+1)
            axes.append(ax)
        
        # Plot each sensor in its subplot with enhanced appearance
        for i, sensor_name in enumerate(selected_sensors):
            ax = axes[i]
            
            # Get data
            time_array, data_array = self.sensor_data.get_xy(sensor_name)
            
            # Calculate some statistics
            min_val = np.min(data_array)
            max_val = np.max(data_array)
            mean_val = np.mean(data_array)
            
            # Plot with consistent color and improved line properties
            color = self.sensor_colors.get(sensor_name)
            line, = ax.plot(time_array, data_array, color=color, linewidth=1.2, alpha=0.9, label=sensor_name)
            
            # Add horizontal line at zero if within range (but not the mean line)
            if min_val < 0 < max_val:
                ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.5)
            
            # Create custom legend handles and labels
            # Bold sensor name with its respective color
            from matplotlib.font_manager import FontProperties
            from matplotlib.lines import Line2D
            
            # Create a bold font for the sensor name
            bold_font = FontProperties()
            bold_font.set_weight('bold')
            bold_font.set_size(6)  # Set the same size as the legend font
            
            # Create legend elements
            legend_elements = [
                # Sensor name with color and bold font
                Line2D([0], [0], color=color, lw=2, label=sensor_name),
                # Stats in black normal font
                Line2D([0], [0], color='white', marker='', linestyle='', label=f"Min: {min_val:.3g}"),
                Line2D([0], [0], color='white', marker='', linestyle='', label=f"Max: {max_val:.3g}"),
                Line2D([0], [0], color='white', marker='', linestyle='', label=f"Mean: {mean_val:.3g}")
            ]
            
            # Add legend at the top right corner with small font
            legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=6, 
                            framealpha=0.7, ncol=1)
            
            # Set the font properties for the first entry (sensor name) to bold
            legend.get_texts()[0].set_fontproperties(bold_font)
            
            # FIX: Set better y-axis limits with appropriate padding
            data_range = max_val - min_val
            padding = data_range * 0.05  # 5% padding
            
            # Handle cases where min and max are very close or equal
            if data_range < 1e-10:
                padding = max(abs(min_val) * 0.05, 0.1)  # Use 5% of value or default to 0.1
            
            # Set y-axis limits with padding
            ax.set_ylim(min_val - padding, max_val + padding)
            
            # Configure tick appearance
            ax.tick_params(axis='both', which='major', labelsize=8, direction='out', length=4)
            ax.tick_params(axis='both', which='minor', labelsize=6, direction='out', length=2)
            
            # Add grid with both major and minor lines
            ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
            ax.grid(True, which='minor', linestyle=':', linewidth=0.3, alpha=0.3)
            ax.minorticks_on()  # Enable minor ticks
            
            # Only set axis labels (no title since it's in the legend now)
            ax.set_xlabel(f"Time ({output_time_unit})", fontsize=8)
            ax.set_ylabel(f"{data_type} ({output_data_unit})", fontsize=8)
            
            # Use scientific notation for large or small numbers
            ax.ticklabel_format(style='sci', scilimits=(-3, 4), axis='y')
            
            # Move tick labels to the edges of the plot box
            ax.tick_params(axis='both', pad=2)  # Reduce padding for tick labels
            
        # Adjust layout for better spacing
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Leave room for suptitle
        
        # Add the widget to the layout
        self.individual_plots_layout.addWidget(plot_widget, 0, 0)
        
        # Set size policy to expand
        plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Draw the canvas
        canvas.draw()

    def clear_plots(self):
        """Clear all plots"""
        self.combined_canvas.clear_plot()
        self.update_individual_plots()
        self.log_message("Plots cleared")
    
    def log_message(self, message, level="INFO"):
        """Add a message to the log text widget"""
        self.log_text.append_message(message, level)
    
    def show_about_dialog(self):
        """Show an about dialog"""
        QMessageBox.about(
            self,
            "About ReplicaXSensorDataReader Analyzer",
            """<h1>ReplicaXSensorDataReader Analyzer</h1>
            <p>A GUI application for analyzing sensor data.</p>
            <p>This application allows you to:</p>
            <ul>
                <li>Load and save sensor configurations</li>
                <li>Process sensor data with various corrections</li>
                <li>Visualize sensor data in combined and individual plots</li>
                <li>Export processed data in multiple formats</li>
                <li>Automatically update data with the live update feature</li>
            </ul>
            """
        )
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop the real time update timer if it's running
        if self.real_time_update_timer.isActive():
            self.real_time_update_timer.stop()
        
        event.accept()


# # Main entry point
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     # Set application style
#     # app.setStyle("Fusion")
    
#     window = ReplicaXSensorDataReaderGUI()
#     window.show()
    
#     sys.exit(app.exec())