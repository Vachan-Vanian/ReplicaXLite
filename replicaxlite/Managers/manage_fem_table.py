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


from ..Managers.fem.material_manager import ReplicaXFemMaterialManager
from ..Managers.fem.node_manager import ReplicaXFemNodeManager
from ..Managers.fem.node_constraint_manager import ReplicaXFemNodeConstraintManager
from ..Managers.fem.node_rigid_diaphragm import ReplicaXFemNodeRigidDiaphragmManager
from ..Managers.fem.node_rigid_link import ReplicaXFemNodeRigidLinkManager
from ..Managers.fem.node_equal_dof_manager import ReplicaXFemNodeEqualDOFManager
from ..Managers.fem.node_mass_manager import ReplicaXFemNodeMassManager
from ..Managers.fem.node_load_manager import ReplicaXFemNodeLoadManager
from ..Managers.fem.time_series_manager import ReplicaXFemTimeSeriesManager
from ..Managers.fem.pattern_manager import ReplicaXFemPatternManager
from ..Managers.fem.element_elastic_section_manager import ReplicaXFemElementElasticSectionManager
from ..Managers.fem.element_fiber_section_manager import ReplicaXFemElementFiberSectionManager
from ..Managers.fem.element_fiber_section_manager_rebars import (ReplicaXFemElementFiberSectionRebarPointManager, 
                                                                ReplicaXFemElementFiberSectionRebarLineManager, 
                                                                ReplicaXFemElementFiberSectionRebarCircleManager)
from ..Managers.fem.element_beam_integration_manager import ReplicaXFemBeamIntegrationManager
from ..Managers.fem.element_beam_manager import ReplicaXFemBeamElementManager
from ..Managers.fem.element_beam_uniform_load_manager import ReplicaXFemBeamElementUniformLoadManager
from ..Managers.fem.analysis_manager import ReplicaXFemAnalysisManager
from ..Managers.manage_fem_table_model_creation import ReplicaXFemTableModelBuilder
from ..Managers.fem.manage_project_sensors import ReplicaXProjectSensors
from pathlib import Path

class ReplicaXFemTableManager:   
    def __init__(self, settings, fem_table_tabs, interactor, console):
        self.settings = settings
        self.fem_table_tabs = fem_table_tabs
        self.interactor = interactor
        self.console=console

        # Initialize fem managers using the new nested structure
        self.materials = ReplicaXFemMaterialManager(
            self.fem_table_tabs['materials'],
            self.settings
        )
               
        self.nodes = ReplicaXFemNodeManager(
            self.fem_table_tabs['nodes']['coordinates'], 
            self.settings
        )
        
        self.constraints = ReplicaXFemNodeConstraintManager(
            constraints_tab_widget=self.fem_table_tabs['nodes']['constraints'],
            settings=self.settings,
            nodes_table=self.nodes.table
        )
        
        self.rigid_diaphragms = ReplicaXFemNodeRigidDiaphragmManager(
            rigid_diaphragms_tab_widget=self.fem_table_tabs['nodes']['restraints']['rigid_diaphragms'],
            settings=self.settings,
            nodes_table=self.nodes.table
        )
        
        self.rigid_links = ReplicaXFemNodeRigidLinkManager(
            rigid_links_tab_widget=self.fem_table_tabs['nodes']['restraints']['rigid_links'],
            settings=self.settings,
            nodes_table=self.nodes.table
        )
        
        self.equal_dofs = ReplicaXFemNodeEqualDOFManager(
            equal_dofs_tab_widget=self.fem_table_tabs['nodes']['restraints']['equal_dofs'],
            settings=self.settings,
            nodes_table=self.nodes.table
        )
        self.masses = ReplicaXFemNodeMassManager(
            masses_tab_widget=self.fem_table_tabs['nodes']['masses'],
            settings=self.settings,
            nodes_table=self.nodes.table
        )
        self.time_series = ReplicaXFemTimeSeriesManager(
            time_series_tab_widget=self.fem_table_tabs['time_series'],
            settings=self.settings,
        )
        self.patterns = ReplicaXFemPatternManager(
            pattern_tab_widget=self.fem_table_tabs['patterns'],
            settings=self.settings,
            time_series_table = self.time_series.table
        )
        self.node_loads = ReplicaXFemNodeLoadManager(
            loads_tab_widget=self.fem_table_tabs['nodes']['loads'],
            settings=self.settings,
            nodes_table=self.nodes.table,
            patterns_table=self.patterns.table
        )
        self.elastic_sections = ReplicaXFemElementElasticSectionManager(
            elastic_sections_tab_widget=self.fem_table_tabs['sections']['elastic'],
            settings=self.settings,
        )
        self.rebar_points = ReplicaXFemElementFiberSectionRebarPointManager(
            rebar_points_tab_widget=self.fem_table_tabs['sections']['fiber']['rebar_points'],
            settings=self.settings,
            materials_table=self.materials.table
        )
        self.rebar_lines = ReplicaXFemElementFiberSectionRebarLineManager(
            rebar_lines_tab_widget=self.fem_table_tabs['sections']['fiber']['rebar_lines'],
            settings=self.settings,
            materials_table=self.materials.table
        )
        self.rebar_circles = ReplicaXFemElementFiberSectionRebarCircleManager(
            rebar_circles_tab_widget=self.fem_table_tabs['sections']['fiber']['rebar_circles'],
            settings=self.settings,
            materials_table=self.materials.table
        )
        self.fiber_sections = ReplicaXFemElementFiberSectionManager(
            fiber_sections_tab_widget=self.fem_table_tabs['sections']['fiber']['section'],
            settings=self.settings,
            materials_table=self.materials.table,
            rebar_points_table=self.rebar_points.table,
            rebar_lines_table=self.rebar_lines.table,
            rebar_circles_table=self.rebar_circles.table
        )
        self.beam_integrations = ReplicaXFemBeamIntegrationManager(
            beam_integrations_tab_widget=self.fem_table_tabs['elements']['beam_integrations'],
            settings=self.settings, 
            elastic_sections_table = self.elastic_sections.table,
            fiber_sections_table= self.fiber_sections.table
        )
        self.beam_elements = ReplicaXFemBeamElementManager(
            beam_elements_tab_widget=self.fem_table_tabs['elements']['connections'],
            settings=self.settings,
            nodes_table = self.nodes.nodes_table, 
            elastic_sections_table = self.elastic_sections.table,
            fiber_sections_table= self.fiber_sections.table,
            beam_integrations_table =self.beam_integrations.table
        )
        self.beam_elements_uniform_loads = ReplicaXFemBeamElementUniformLoadManager(
            beam_elemenets_loads_tab_widget=self.fem_table_tabs['elements']['loads'],
            settings=self.settings,
            load_patterns_table = self.patterns.table,
            beam_elements_table= self.beam_elements.table,
        )
        self.analyses = ReplicaXFemAnalysisManager(
            analysis_tab_widget = self.fem_table_tabs['analyses'],
            settings=self.settings,
            load_patterns_table = self.patterns.table,
            nodes_table=self.nodes.table
        )
        self.sensors = ReplicaXProjectSensors(
            sensors_tab_widget = self.fem_table_tabs['sensors'],
            settings=self.settings,
            interactor=self.interactor
        )

        # Initiialize the reverse tunnel
        self.model = ReplicaXFemTableModelBuilder(self, console)

        self.analyses.btn_build_model.clicked.connect(lambda: self.model.create_model(progress="build"))
        self.analyses.btn_build_and_run_model.clicked.connect(lambda: self.model.create_model(progress="run"))



    def save_all_table(self, folder_path:Path):
        self.nodes.table.save_to_file((folder_path / "nodes_table.json").as_posix())
        self.materials.table.save_to_file((folder_path / "materials_table.json").as_posix())
        self.constraints.table.save_to_file((folder_path / "constraints_table.json").as_posix())
        self.rigid_diaphragms.table.save_to_file((folder_path / "rigid_diaphragms_table.json").as_posix())
        self.rigid_links.table.save_to_file((folder_path / "rigid_links_table.json").as_posix())
        self.equal_dofs.table.save_to_file((folder_path / "equal_dofs_table.json").as_posix())
        self.masses.table.save_to_file((folder_path / "masses_table.json").as_posix())
        self.time_series.table.save_to_file((folder_path / "time_series_table.json").as_posix())
        self.patterns.table.save_to_file((folder_path / "patterns_table.json").as_posix())
        self.node_loads.table.save_to_file((folder_path / "node_loads_table.json").as_posix())
        self.elastic_sections.table.save_to_file((folder_path / "elastic_sections_table.json").as_posix())
        self.rebar_points.table.save_to_file((folder_path / "rebar_points_table.json").as_posix())
        self.rebar_lines.table.save_to_file((folder_path / "rebar_lines_table.json").as_posix())
        self.rebar_circles.table.save_to_file((folder_path / "rebar_circles_table.json").as_posix())
        self.fiber_sections.table.save_to_file((folder_path / "fiber_sections_table.json").as_posix())
        self.beam_integrations.table.save_to_file((folder_path / "beam_integrations_table.json").as_posix())
        self.beam_elements.table.save_to_file((folder_path / "beam_elements_table.json").as_posix())
        self.beam_elements_uniform_loads.table.save_to_file((folder_path / "beam_elements_uniform_loads_table.json").as_posix())
        self.analyses.table.save_to_file((folder_path / "analyses_table.json").as_posix())
        self.sensors.table.save_to_file((folder_path / "sensors_table.json").as_posix())

    def load_all_tables(self, folder_path:Path):
        self.nodes.table.load_from_file((folder_path / "nodes_table.json").as_posix())
        self.materials.table.load_from_file((folder_path / "materials_table.json").as_posix())
        self.materials.refresh_dropdown_nested_table_links_after_load() # special case
        self.constraints.table.load_from_file((folder_path / "constraints_table.json").as_posix())
        self.rigid_diaphragms.table.load_from_file((folder_path / "rigid_diaphragms_table.json").as_posix())
        self.rigid_links.table.load_from_file((folder_path / "rigid_links_table.json").as_posix())
        self.equal_dofs.table.load_from_file((folder_path / "equal_dofs_table.json").as_posix())
        self.masses.table.load_from_file((folder_path / "masses_table.json").as_posix())
        self.time_series.table.load_from_file((folder_path / "time_series_table.json").as_posix())
        self.patterns.table.load_from_file((folder_path / "patterns_table.json").as_posix())
        self.patterns.refresh_dropdown_nested_table_links_after_load() # special case
        self.node_loads.table.load_from_file((folder_path / "node_loads_table.json").as_posix())
        self.elastic_sections.table.load_from_file((folder_path / "elastic_sections_table.json").as_posix())
        self.rebar_points.table.load_from_file((folder_path / "rebar_points_table.json").as_posix())
        self.rebar_lines.table.load_from_file((folder_path / "rebar_lines_table.json").as_posix())
        self.rebar_circles.table.load_from_file((folder_path / "rebar_circles_table.json").as_posix())
        self.fiber_sections.table.load_from_file((folder_path / "fiber_sections_table.json").as_posix())
        self.beam_integrations.table.load_from_file((folder_path / "beam_integrations_table.json").as_posix())
        self.beam_elements.table.load_from_file((folder_path / "beam_elements_table.json").as_posix())
        self.beam_elements_uniform_loads.table.load_from_file((folder_path / "beam_elements_uniform_loads_table.json").as_posix())
        self.analyses.table.load_from_file((folder_path / "analyses_table.json").as_posix())
        self.analyses.refresh_dropdown_nested_table_links_after_load() # special case
        self.sensors.table.load_from_file((folder_path / "sensors_table.json").as_posix())

    def sync_units_from_settings(self):
        self.nodes.table.sync_units_from_settings()
        self.materials.table.sync_units_from_settings()
        self.constraints.table.sync_units_from_settings()
        self.rigid_diaphragms.table.sync_units_from_settings()
        self.rigid_links.table.sync_units_from_settings()
        self.equal_dofs.table.sync_units_from_settings()
        self.masses.table.sync_units_from_settings()
        self.time_series.table.sync_units_from_settings()
        self.patterns.table.sync_units_from_settings()
        self.node_loads.table.sync_units_from_settings()
        self.elastic_sections.table.sync_units_from_settings()
        self.rebar_points.table.sync_units_from_settings()
        self.rebar_lines.table.sync_units_from_settings()
        self.rebar_circles.table.sync_units_from_settings()
        self.fiber_sections.table.sync_units_from_settings()
        self.beam_integrations.table.sync_units_from_settings()
        self.beam_elements.table.sync_units_from_settings()
        self.beam_elements_uniform_loads.table.sync_units_from_settings()
        self.analyses.table.sync_units_from_settings()
        self.sensors.table.sync_units_from_settings()

    def reset_all_tables(self):
        """Reset all tables by clearing their data."""
        self.nodes.table.reset_data()
        self.materials.table.reset_data()
        self.constraints.table.reset_data()
        self.rigid_diaphragms.table.reset_data()
        self.rigid_links.table.reset_data()
        self.equal_dofs.table.reset_data()
        self.masses.table.reset_data()
        self.time_series.table.reset_data()
        self.patterns.table.reset_data()
        self.node_loads.table.reset_data()
        self.elastic_sections.table.reset_data()
        self.rebar_points.table.reset_data()
        self.rebar_lines.table.reset_data()
        self.rebar_circles.table.reset_data()
        self.fiber_sections.table.reset_data()
        self.beam_integrations.table.reset_data()
        self.beam_elements.table.reset_data()
        self.beam_elements_uniform_loads.table.reset_data()
        self.analyses.table.reset_data()
        self.analyses.store_modal_results = [] # SPECIAL CASE
        self.sensors.reset_content() ## SPECIAL CASE interntally it is call the self.sensors.table.reset_data()
