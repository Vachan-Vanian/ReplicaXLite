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
from pathlib import Path
from PySide6 import QtGui, QtCore, QtWidgets
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


class JupyterConsole(RichJupyterWidget):
    """
    Production Jupyter Console with full rich media support
    
    Features:
    - Inline matplotlib plots
    - Image display (PNG, JPG, SVG)
    - HTML rendering
    - LaTeX math equations
    - Video and audio playback
    - Pandas DataFrame pretty printing
    - Syntax highlighting
    - Tab completion
    - Magic commands (%timeit, %who, %whos, etc.)
    """
    
    def __init__(self, parent=None, app_reference=None):
        super().__init__(parent)
        
        self.app_reference = app_reference
        
        # Configure appearance
        self.setup_appearance()
        
        # Create and start kernel
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        
        # Setup kernel client
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        
        # Get shell for direct access
        self.shell = self.kernel_manager.kernel.shell
        
        # Setup banner
        self.banner = self.create_banner()
        
        # Initialize environment
        self.setup_environment()
        
        # Push app into namespace
        if self.app_reference:
            self.shell.push({'app': self.app_reference})
    
    def setup_appearance(self):
        """Configure visual appearance"""
        self.kind = 'rich'
        self.set_default_style('linux')
        font = QtGui.QFont("Consolas", 11)
        self.setFont(font)
        self.syntax_style = 'monokai'
        
        # CRITICAL: Enable rich output display
        self.enable_calltips = True
        self.include_other_output = True
        
        # Enable rich MIME types
        self._control.setAcceptRichText(True)
    
    def create_banner(self):
        """Create welcome banner"""
        return """
╔══════════════════════════════════════════════════════════════════════╗
║              ReplicaXLite - Interactive Console                      ║
║                   Powered by Jupyter Kernel                          ║
╚══════════════════════════════════════════════════════════════════════╝

Ready! All features enabled:
   ✓ Rich media (images, plots, HTML, LaTeX)
   ✓ High-DPI inline matplotlib plots (150 DPI)
   ✓ HTML rendering
   ✓ LaTeX math equations
   ✓ Tab completion
   ✓ Syntax highlighting
   ✓ Magic commands

Quick Start:
   app                         # Access main application
   app.interactor              # Access 3D viewer
   app.settings                # View/modify settings
   
Plot Example:
   import matplotlib.pyplot as plt
   import numpy as np
   x = np.linspace(0, 10, 100)
   plt.plot(x, np.sin(x))
   plt.title('High DPI Plot')
   plt.show()

Display HTML:
   from IPython.display import HTML, display
   display(HTML('<h2 style="color:blue;">Hello!</h2>'))

Display LaTeX Math:
   from IPython.display import Latex, display
   display(Latex(r'$E = mc^2$'))
   
Magic Commands:
   %timeit expression          # Measure execution time
   %who                        # List variables
   %whos                       # Detailed variable info
   %pwd                        # Print working directory
   %cd path                    # Change directory
   %history                    # View command history
   %reset                      # Clear namespace
   %quickref                   # Quick reference guide

💡 Tips:
   • Press Tab for autocompletion
   • Use ? for help: app?
   • Use ?? for source code: app??
   • Use Shift+Enter for multiline input
   • Use Ctrl+C to interrupt execution

Type 'help()' for Python help or start coding!
        """
    
    def setup_environment(self):
        """Setup Python environment with common imports and configurations"""
        # Enable rich display formatters FIRST
        self.enable_rich_display_formatters()
        
        # Store console reference in shell for the helper to use
        self.shell.push({'_console_widget': self})
        
        setup_code = """
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Image, HTML, Markdown, Latex
from PySide6.QtCore import QThread, Signal, QObject, QTimer
from PySide6.QtWidgets import QApplication

# Configure matplotlib
%matplotlib inline

# Configure pandas
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)

# ============================================================================
# ASYNC EXECUTION HELPER - Output goes to THIS console!
# ============================================================================

class _ConsoleStream:
    '''Custom stream that writes to console'''
    def __init__(self, console_widget):
        self.console = console_widget
        self.original_stdout = sys.stdout
    
    def write(self, text):
        if text.strip():
            # Print to console using IPython's display system
            print(text, end='', file=self.original_stdout)
            # Also force GUI update
            QApplication.processEvents()
    
    def flush(self):
        QApplication.processEvents()

class _AsyncWorker(QThread):
    '''Worker thread that redirects output to console'''
    finished_signal = Signal(object)
    error_signal = Signal(str)
    
    def __init__(self, func, args, kwargs, console_widget):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.console = console_widget
    
    def run(self):
        try:
            # Redirect stdout to console
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            sys.stdout = _ConsoleStream(self.console)
            sys.stderr = _ConsoleStream(self.console)
            
            try:
                result = self.func(*self.args, **self.kwargs)
                self.finished_signal.emit(result)
                
                if result is not None:
                    print(f"\\n✓ Result: {result}")
            finally:
                # Restore original streams
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            import traceback
            error_msg = f"Error: {e}\\n{traceback.format_exc()}"
            self.error_signal.emit(error_msg)
            print(error_msg)

_active_threads = []
_update_timer = None

def _setup_gui_updates():
    '''Setup timer to process GUI events during async execution'''
    global _update_timer
    if _update_timer is None:
        _update_timer = QTimer()
        _update_timer.timeout.connect(lambda: QApplication.processEvents())
        _update_timer.start(50)  # Update every 50ms

def run_async(func, *args, **kwargs):
    '''
    Run function asynchronously with output to console
    
    Usage:
        def my_task():
            for i in range(100):
                print(f"Step {i}")
                time.sleep(0.01)
        
        run_async(my_task)
    
    ⚠️ Don't call GUI methods inside func!
    '''
    _setup_gui_updates()
    
    worker = _AsyncWorker(func, args, kwargs, _console_widget)
    _active_threads.append(worker)
    
    def on_finished(result):
        _active_threads.remove(worker)
        print("\\n✓ Async task completed")
    
    def on_error(error_msg):
        _active_threads.remove(worker)
        print(f"\\n✗ Async task failed")
    
    worker.finished_signal.connect(on_finished)
    worker.error_signal.connect(on_error)
    worker.start()
    
    print("✓ Started async task (output appears in console)...")

print("✓ Environment initialized")
print("✓ Use run_async() for long operations")
print()
        """
        
        self.execute(setup_code, hidden=False)
    
    def enable_rich_display_formatters(self):
        """Enable proper display formatters for HTML, LaTeX, and other rich content"""
        try:
            # Get the display formatter
            from IPython.core.formatters import DisplayFormatter
            from IPython.display import HTML, Latex, Image, Markdown
            
            # Enable HTML formatter
            html_formatter = self.shell.display_formatter.formatters.get('text/html')
            if html_formatter:
                html_formatter.enabled = True
            
            # Enable LaTeX formatter
            latex_formatter = self.shell.display_formatter.formatters.get('text/latex')
            if latex_formatter:
                latex_formatter.enabled = True
            
            # Enable image formatters
            for fmt in ['image/png', 'image/jpeg', 'image/svg+xml']:
                formatter = self.shell.display_formatter.formatters.get(fmt)
                if formatter:
                    formatter.enabled = True
            
            # Enable markdown formatter
            markdown_formatter = self.shell.display_formatter.formatters.get('text/markdown')
            if markdown_formatter:
                markdown_formatter.enabled = True
                
        except Exception as e:
            print(f"Note: Some display formatters may not be fully enabled: {e}")
    
    def restart_kernel(self):
            """Comprehensive kernel reset: namespace, history, and execution counter"""
            try:
                # Step 1: Clear the namespace (all variables)
                self.execute("%reset -f", hidden=True)
                
                # Step 2: Reset history manager (this resets In[n] to 1!)
                if self.shell and hasattr(self.shell, 'history_manager'):
                    self.shell.history_manager.reset()
                
                # Step 3: Clear the display
                self.clear()

                self.shell.reset()
                
                # Step 4: Reinitialize environment
                self.enable_rich_display_formatters()
                self.setup_environment()
                
                # Step 5: Add app back to namespace
                if self.app_reference:
                    self.shell.push({'app': self.app_reference})
                
                print("✓ Kernel reset successfully")
                print("✓ All variables cleared")
                print("✓ Execution counter reset to In[1]")
                print()
                
            except Exception as e:
                print(f"✗ Error resetting kernel: {e}")
                import traceback
                traceback.print_exc()









class ConsoleManager:
    """
    Production Console Manager for ReplicaXLite
    
    Features:
    - Single console instance
    - Open/Save Python files
    - Clear output
    """
    
    def __init__(self, parent, console_container):
        """
        Initialize console manager
        
        Args:
            parent: Main application window
            console_container: QWidget where console should be embedded
        """
        self.parent = parent
        self.console_container = console_container
        self.console = None
        self.current_file = None
        
        self.setup_console_ui()
    
    def setup_console_ui(self):
        """Setup the complete console UI with toolbar"""
        main_layout = QtWidgets.QVBoxLayout(self.console_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Create single console
        self.console = JupyterConsole(app_reference=self.parent)
        main_layout.addWidget(self.console)
        
        print("═" * 70)
        print("✓ Jupyter Console Ready!")
        print("═" * 70)
    
    def create_toolbar(self):
        """Create toolbar with all action buttons"""
        toolbar = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)
        
        button_style = """
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: white;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """
        
        # Open File
        btn_open = QtWidgets.QPushButton("📂 Open")
        btn_open.setToolTip("Open Python file")
        btn_open.setStyleSheet(button_style)
        btn_open.clicked.connect(self.open_file)
        toolbar_layout.addWidget(btn_open)
        
        # Save File
        btn_save = QtWidgets.QPushButton("💾 Save")
        btn_save.setToolTip("Save current console content to file")
        btn_save.setStyleSheet(button_style)
        btn_save.clicked.connect(self.save_file)
        toolbar_layout.addWidget(btn_save)
        
        # Save As
        btn_save_as = QtWidgets.QPushButton("💾 Save As")
        btn_save_as.setToolTip("Save to a new file")
        btn_save_as.setStyleSheet(button_style)
        btn_save_as.clicked.connect(self.save_file_as)
        toolbar_layout.addWidget(btn_save_as)
        
        toolbar_layout.addWidget(self.create_separator())
        
        # Clear Output
        btn_clear = QtWidgets.QPushButton("🗑️ Clear")
        btn_clear.setToolTip("Clear console output")
        btn_clear.setStyleSheet(button_style)
        btn_clear.clicked.connect(self.clear_console)
        toolbar_layout.addWidget(btn_clear)
        
        toolbar_layout.addStretch()
        
        return toolbar
    
    def create_separator(self):
        """Create a vertical separator line"""
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        return separator
    
    def get_current_console(self):
        """Get the console"""
        return self.console
    
    def open_file(self):
        """Open a Python file and load it into the console (without executing)"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.parent,
            "Open Python File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                if self.console:
                    # Load code into input area without executing
                    self.console.input_buffer = code  # or self.console.setPlainText(code)
                    self.current_file = file_path
                    print(f"✓ Loaded: {Path(file_path).name}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.parent,
                    "Error Opening File",
                    f"Could not open file:\n{str(e)}"
                )

    def save_file(self):
        """Save current console input to file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save console input to a new file"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.parent,
            "Save Python File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
    
    def _save_to_file(self, file_path):
        """Internal method to save content to file"""
        try:
            if self.console:
                history = self.console.shell.history_manager.get_range()
                
                # Get list of available magic commands
                magic_commands = set(self.console.shell.magics_manager.magics['line'].keys())
                
                code_lines = []
                for session, line_num, line_content in history:
                    line = line_content.strip()
                    
                    # Auto-add % to magic commands if missing
                    if line and not line.startswith('%') and not line.startswith('!'):
                        first_word = line.split()[0] if line.split() else ''
                        if first_word in magic_commands:
                            line = '%' + line
                    
                    code_lines.append(line)
                
                code = '\n\n'.join(code_lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                print(f"✓ Saved to: {Path(file_path).name}")
                
                QtWidgets.QMessageBox.information(
                    self.parent,
                    "File Saved",
                    f"Console content saved to:\n{file_path}"
                )
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent,
                "Error Saving File",
                f"Could not save file:\n{str(e)}"
            )
    
    def clear_console(self):
        """Clear the console output"""
        if self.console:
            self.console.clear()
            print("✓ Console cleared")

    def execute_code(self, code):
        """Execute code in the console"""
        if self.console:
            self.console.execute(code)
    
    def get_namespace(self):
        """Get current namespace variables"""
        if self.console:
            return self.console.shell.user_ns
        return {}


class ConsoleOutput:
    """Redirect stdout to Jupyter console"""
    
    def __init__(self, console_widget):
        self.console = console_widget
        self.original_stdout = sys.stdout
    
    def write(self, text):
        """Write to original stdout"""
        if text.strip():
            try:
                print(text, file=self.original_stdout)
            except:
                pass
    
    def flush(self):
        """Flush the output"""
        if hasattr(self.original_stdout, 'flush'):
            self.original_stdout.flush()
