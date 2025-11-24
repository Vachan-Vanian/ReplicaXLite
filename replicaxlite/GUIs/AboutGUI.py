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


from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QGridLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ..config import INFO

class ReplicaXAbout(QDialog):
    def __init__(self, package_root, parent=None):
        super().__init__(parent)

        self.package_root = package_root
        self.setWindowTitle("About")
        self.setFixedSize(800, 700)  # Increased height to accommodate funding section
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Logo - with resize to fit properly
        logo_label = QLabel()
        logo_pixmap = QPixmap(self.package_root / "GUIs" / "icons" / "about" / "about.png")
        # Scale the image to fit within the dialog width while maintaining aspect ratio
        scaled_pixmap = logo_pixmap.scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Separator line
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: #444444;")
        layout.addWidget(separator1)
        
        # Description
        description = QLabel("ReplicaXLite - A finite element toolkit for creating, analyzing and monitoring 3D structural models")
        description.setAlignment(Qt.AlignLeft)
        description.setStyleSheet("font-size: 14px; margin: 10px 0;")
        layout.addWidget(description)
        
        # Version
        version = QLabel(f"Version: {INFO['version']}")
        version.setAlignment(Qt.AlignLeft)
        layout.addWidget(version)
        
        # Copyright
        copyright = QLabel("Copyright © 2024-2025")
        copyright.setAlignment(Qt.AlignLeft)
        layout.addWidget(copyright)
        
        # Developer info - using grid layout for proper alignment
        dev_layout = QGridLayout()
        dev_layout.setColumnStretch(0, 1)
        dev_layout.setColumnStretch(1, 2)
        
        dev_name = QLabel("Developed by: Vachan Vanian")
        dev_email = QLabel('<a href="mailto:vachanvanian@outlook.com" style="color: #4A9EFF; text-decoration: none;">email: vachanvanian@outlook.com</a>')
        dev_email.setTextFormat(Qt.RichText)
        dev_email.setOpenExternalLinks(True)
        dev_email.setAlignment(Qt.AlignRight)
        
        dev_layout.addWidget(dev_name, 0, 0)
        dev_layout.addWidget(dev_email, 0, 1)
        
        dev_container = QFrame()
        dev_container.setLayout(dev_layout)
        layout.addWidget(dev_container)
        
        # Project info
        project = QLabel("Under Project: GREENERGY")
        project.setAlignment(Qt.AlignLeft)
        layout.addWidget(project)
        
        # PI info - using grid layout for proper alignment
        pi_layout = QGridLayout()
        pi_layout.setColumnStretch(0, 1)
        pi_layout.setColumnStretch(1, 2)
        
        pi_name = QLabel("Project (PI): Theodoros Rousakis")
        pi_email = QLabel('<a href="mailto:trousak@civil.duth.gr" style="color: #4A9EFF; text-decoration: none;">email: trousak@civil.duth.gr</a>')
        pi_email.setTextFormat(Qt.RichText)
        pi_email.setOpenExternalLinks(True)
        pi_email.setAlignment(Qt.AlignRight)
        
        pi_layout.addWidget(pi_name, 0, 0)
        pi_layout.addWidget(pi_email, 0, 1)
        
        pi_container = QFrame()
        pi_container.setLayout(pi_layout)
        layout.addWidget(pi_container)
        
        # Department info
        department = QLabel("Department of Civil Engineering, Democritus University of Thrace, Greece")
        department.setAlignment(Qt.AlignLeft)
        layout.addWidget(department)
        
        # Separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #444444;")
        layout.addWidget(separator2)
        
        # ==================== FUNDING ACKNOWLEDGMENT SECTION ====================

        # Funding header
        funding_header = QLabel("Acknowledgment")
        funding_header.setAlignment(Qt.AlignCenter)
        funding_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(funding_header)

        # Funding text
        funding_text = QLabel(
            "This project is implemented in the framework of H.F.R.I call \"Basic research Financing "
            "(Horizontal support of all Sciences)\" under the National Recovery and Resilience Plan "
            "\"Greece 2.0\" funded by the European Union—NextGenerationEU\n"
            "(H.F.R.I. Project Number: 015376)."
        )
        funding_text.setWordWrap(True)
        funding_text.setAlignment(Qt.AlignCenter)
        funding_text.setStyleSheet("font-size: 11px; margin: 10px 20px;")
        layout.addWidget(funding_text)

        # First row: ELIDEK and GREENERGY side by side - closer together
        top_logos_layout = QHBoxLayout()
        top_logos_layout.addStretch(1)  # Push logos towards center from left

        # ELIDEK Logo - height 80px
        elidek_logo = QLabel()
        elidek_pixmap = QPixmap(self.package_root / "GUIs" / "icons" / "about" / "ELIDEK_logo.jpg")
        elidek_scaled = elidek_pixmap.scaledToHeight(80, Qt.SmoothTransformation)
        elidek_logo.setPixmap(elidek_scaled)
        elidek_logo.setAlignment(Qt.AlignCenter)
        top_logos_layout.addWidget(elidek_logo)

        # Small spacing between logos (adjust this number to control gap)
        top_logos_layout.addSpacing(18)  # Change this to make them closer/farther

        # GREENERGY Logo - height 80px
        greenergy_logo = QLabel()
        greenergy_pixmap = QPixmap(self.package_root / "GUIs" / "icons" / "about" / "GREENERGY_logo.jpg")
        greenergy_scaled = greenergy_pixmap.scaledToHeight(80, Qt.SmoothTransformation)
        greenergy_logo.setPixmap(greenergy_scaled)
        greenergy_logo.setAlignment(Qt.AlignCenter)
        top_logos_layout.addWidget(greenergy_logo)

        top_logos_layout.addStretch(1)  # Push logos towards center from right

        # Add top logos to main layout
        top_logos_container = QFrame()
        top_logos_container.setLayout(top_logos_layout)
        layout.addWidget(top_logos_container)

        # Second row: Greece 2.0 logo (centered)
        bottom_logo_layout = QHBoxLayout()
        bottom_logo_layout.setContentsMargins(20, 5, 20, 10)

        greece_logo = QLabel()
        greece_pixmap = QPixmap(self.package_root / "GUIs" / "icons" / "about" / "Greece_2_0_NextGeneration_logo.jpg")
        greece_scaled = greece_pixmap.scaledToHeight(106, Qt.SmoothTransformation)
        greece_logo.setPixmap(greece_scaled)
        greece_logo.setAlignment(Qt.AlignCenter)
        bottom_logo_layout.addWidget(greece_logo)

        # Add bottom logo to main layout
        bottom_logo_container = QFrame()
        bottom_logo_container.setLayout(bottom_logo_layout)
        layout.addWidget(bottom_logo_container)

        # ==================== END FUNDING SECTION ====================
        
        # Add some spacing at the bottom
        layout.addStretch()
