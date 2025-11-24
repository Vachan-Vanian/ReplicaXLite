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


import copy

class ReplicaXUnits:
    def __init__(self):
        self.__basic_units = {
            'Length': {'m': 1, 'cm': 0.01,'mm': 0.001, 'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144},
            'Time': {'s': 1,'min': 60, 'hr': 3600, 'day': 86400},
            'Mass': {'kg': 1, 'g': 0.001, 'tonne': 1000, 'ktonne': 1000*1000, 'lb': 0.45359237, 'oz': 0.028349523125,
                    "lbf*s^2/in":175.1268352464760, "lbf*s^2/ft":14.59390293720640, "lbf*s^2/yd":4.864634312402140, 
                    "kip*s^2/in":175126.8352464760, "kip*s^2/ft":14593.90293720640, "kip*s^2/yd":4864.634312402140},
            'Temperature': {'K':1, 'C':1, 'F':1}, # special case
            'Angle': {'rad': 1, 'deg': 0.01745329251994330},
            'Area': {'m^2': 1, 'cm^2': 0.0001,'mm^2': 0.000001, 'in^2': 0.00064516, 'ft^2': 0.09290304, 'yd^2': 0.83612736},
            'Volume': {'m^3': 1, 'cm^3': 0.000001,'mm^3': 0.000000001, 'in^3': 0.000016387064, 'ft^3': 0.028316846592, 'yd^3': 0.764554857984},
            'Specific_Weight': {'N/m^3': 1, 'kN/m^3': 1000, 'MN/m^3': 1000000,
                    'N/cm^3': 1000000, 'kN/cm^3': 1000000000, 'MN/cm^3': 1000000000000,
                    'N/mm^3': 1000000000, 'kN/mm^3': 1000000000000, 'MN/mm^3': 1000000000000000,
                    'lbf/in^3': 271447.1375263140, 'lbf/ft^3': 157.0874638462460, 'lbf/yd^3': 5.818054216527630,
                    'kip/in^3': 271447.1375263140*1000, 'kip/ft^3': 157.0874638462460*1000, 'kip/yd^3': 5.818054216527630*1000},
            'Pressure': {'N/m^2': 1, 'kN/m^2': 1000, 'MN/m^2': 1000000,
                    'N/cm^2': 10000, 'kN/cm^2': 10000000, 'MN/cm^2': 10000000000,
                    'N/mm^2': 1000000, 'kN/mm^2': 1000000000, 'MN/mm^2': 1000000000000,
                    'Pa': 1, 'kPa': 1000, 'MPa': 1000000, 'GPa': 1000000000,
                    'psi': 6894.757293168360, 'ksi': 6894.757293168360*1000,
                    'lbf/in^2':6894.757293168370, 'lbf/ft^2':47.88025898033600, 'lbf/yd^2':5.320028775592890,
                    'kip/in^2':6894.757293168370*1000, 'kip/ft^2':47.88025898033600*1000, 'kip/yd^2':5.320028775592890*1000},
            'Coefficient_of_Thermal_Expansion': {'1/K': 1, '1/C': 1, '1/F': 1.8},
            'Acceleration': {'m/s^2': 1, 'cm/s^2': 0.01,'mm/s^2': 0.001, 'in/s^2': 0.0254, 'ft/s^2': 0.3048, 'yd/s^2': 0.9144, 'g': 9.80665},
            'Thermal_Conductivity': {'W/mK': 1, 'W/mC': 1, 'W/mF': 1.8, 'BTU/(hr*ft*F)': 1.730734666371390},
            'Concentrated_Force': {'N': 1, 'kN': 1000, 'MN': 1000000, 'lbf': 4.448221615260500, 'kip': 4.448221615260500*1000},
            'Distributed_Force': {'N/m': 1, 'kN/m': 1000, 'MN/m': 1000000,
                    'N/cm': 100, 'kN/cm': 100000, 'MN/cm': 100000000,
                    'N/mm': 1000, 'kN/mm': 1000000, 'MN/mm': 1000000000,
                    'lbf/in': 175.1268352464760, 'lbf/ft': 14.59390293720640, 'lbf/yd': 4.864634312402140,
                    'kip/in': 175.1268352464760*1000, 'kip/ft': 14.59390293720640*1000, 'kip/yd': 4.864634312402140*1000},
            'Work': {'N*m': 1, 'kN*m': 1000, 'MN*m': 1000000,
                    'N*cm': 0.01, 'kN*cm': 10, 'MN*cm': 1000,
                    'N*mm': 0.001, 'kN*mm': 1, 'MN*mm': 1000,
                    'lbf*in': 0.1129848290276170, 'lbf*ft': 1.355817948331400, 'lbf*yd': 4.067453844994200,
                    'kip*in': 0.1129848290276170*1000, 'kip*ft': 1.355817948331400*1000, 'kip*yd': 4.067453844994200*1000},
            'Volume_Force': {'N/m^3': 1, 'kN/m^3': 1000, 'MN/m^3': 1000000,
                                'N/cm^3': 1000000, 'kN/cm^3': 1000000000, 'MN/cm^3': 1000000000000,
                                'N/mm^3': 1000000000, 'kN/mm^3': 1000000000000, 'MN/mm^3': 1000000000000000,
                                'lbf/in^3': 271447.1375263140, 'lbf/ft^3': 157.0874638462460, 'lbf/yd^3': 5.818054216527630,
                                'kip/in^3': 271447.1375263140*1000, 'kip/ft^3': 157.0874638462460*1000, 'kip/yd^3': 5.818054216527630*1000},
            'Velocity': {'m/s': 1, 'cm/s': 0.01,'mm/s': 0.001, 'in/s': 0.0254, 'ft/s': 0.3048, 'yd/s': 0.9144},
            'Angular_Velocity': {'rad/s': 1, 'deg/s': 0.0174532925199433, 'rpm': 0.10471975511965977},
            'Angular_Acceleration': {'rad/s^2': 1, 'deg/s^2': 0.01745329251994330, 'rpm^2': 0.01096622711232150},
            'Second_Moment_of_Area': {'m^4': 1, 'cm^4': 0.00000001,'mm^4': 0.000000000001, 'in^4': 4.162314255999999e-07, 'ft^4': 0.008630974841241602, 'yd^4': 0.6991089621405696},
            'Flexural_Rigidity': {'N*m^2': 1, 'kN*m^2': 1000, 'MN*m^2': 1000000,
                                    'N*cm^2': 0.0001, 'kN*cm^2': 0.1, 'MN*cm^2': 100,
                                    'N*mm^2': 0.000001, 'kN*mm^2': 0.001, 'MN*mm^2': 1,
                                    'lbf*in^2': 0.002869814657301460, 'lbf*ft^2': 0.4132533106514120,'lbf*yd^2': 3.719279795862690,
                                    'kip*in^2': 0.002869814657301460*1000, 'kip*ft^2': 0.4132533106514120*1000,'kip*yd^2': 3.719279795862690*1000},
            'Mass_per_Unit_Length': {'kg/m':1, 'kg/cm':100, 'kg/mm':1000, 'g/m':0.001, 'g/cm':0.1, 'g/mm':1, 'tonne/m':1000, 'tonne/cm':100000, 'tonne/mm':1000000,'ktonne/mm':1000000000,
                                     'lb/in': 17.85796732283460, 'lb/ft':1.488163943569550, 'lb/yd':0.4960546478565180,
                                     'oz/in': 1.116122957677170, 'oz/ft':0.09301024647309709, 'oz/yd':0.03100341549103240,
                                     "(kip*s^2/in)/in":6894757.293168360,"(kip*s^2/in)/ft":574563.1077640300,"(kip*s^2/in)/yd":191521.0359213430,
                                     "(kip*s^2/ft)/in":574563.1077640260,"(kip*s^2/ft)/ft":47880.25898033540, "(kip*s^2/ft)/yd":15960.08632677850,
                                     "(kip*s^2/yd)/in":191521.0359213420,"(kip*s^2/yd)/ft":15960.08632677850, "(kip*s^2/yd)/yd":5320.028775592820,
                                     "(lbf*s^2/in)/in":6894.757293168370,"(lbf*s^2/in)/ft":574.5631077640300,"(lbf*s^2/in)/yd":191.5210359213430,
                                     "(lbf*s^2/ft)/in":574.5631077640330,"(lbf*s^2/ft)/ft":47.88025898033600, "(lbf*s^2/ft)/yd":15.96008632677870,
                                     "(lbf*s^2/yd)/in":191.5210359213440,"(lbf*s^2/yd)/ft":15.96008632677870, "(lbf*s^2/yd)/yd":5.320028775592890 
                                    },
            'Mass_Moments_of_Inertia': {'kg*m^2':1, 'kg*cm^2':0.0001, 'kg*mm^2':0.000001, 'g*m^2':0.001, 'g*cm^2':0.0000001, 'g*mm^2':0.000000001, 'tonne*m^2':1000, 'tonne*cm^2':0.1, 'tonne*mm^2':0.001, 'ktonne*mm^2':1,
                                        'lb*in^2': 0.0002926396534292, 'lb*ft^2': 0.04214011009380480, 'lb*yd^2': 0.3792609908442430,
                                        'oz*in^2': 0.000018289978339325, 'oz*ft^2': 0.0026337568808628, 'oz*yd^2': 0.0237038119277652,
                                        '(kip*s^2/in)*in^2': 112.984829027617, '(kip*s^2/in)*ft^2': 16269.8153799767, '(kip*s^2/in)*yd^2': 146428.338419792,
                                        '(kip*s^2/ft)*in^2': 9.41540241896803, '(kip*s^2/ft)*ft^2': 1355.8179483314, '(kip*s^2/ft)*yd^2': 12202.3615349826,
                                        '(kip*s^2/yd)*in^2': 3.13846747298934, '(kip*s^2/yd)*ft^2': 451.939316110465, '(kip*s^2/yd)*yd^2': 4067.453844994170,
                                        '(lbf*s^2/in)*in^2': 0.112984829027617, '(lbf*s^2/in)*ft^2': 16.2698153799767, '(lbf*s^2/in)*yd^2': 146.428338419792,
                                        '(lbf*s^2/ft)*in^2': 0.00941540241896806, '(lbf*s^2/ft)*ft^2': 1.3558179483314, '(lbf*s^2/ft)*yd^2': 12.2023615349827,
                                        '(lbf*s^2/yd)*in^2': 0.00313846747298936, '(lbf*s^2/yd)*ft^2': 0.451939316110469, '(lbf*s^2/yd)*yd^2': 4.06745384499421
                                        },
            'Frequency': {'Hz': 1, '1/s':1, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9},
            'Strain': {
                # Base unit is dimensionless strain (m/m, in/in, etc.)
                'strain': 1,                   # Dimensionless strain
                'uStrain': 1e-6,               # Microstrain (µε)
                'microStrain': 1e-6,           # Alternative name for microstrain
                'mStrain': 1e-3,               # Millistrain
                'milliStrain': 1e-3,           # Alternative name for millistrain
                'percent': 0.01,               # Percent strain (%)
                '%': 0.01,                     # Percent symbol
                "permille": 1e-3,              # Per mille (‰) - parts per thousand
                'o/oo': 1e-3,                  # Per mille symbol
                'ppm': 1e-6,                   # Parts per million
                'ppb': 1e-9,                   # Parts per billion
                'in/in': 1,                    # Inch per inch
                'mm/mm': 1,                    # Millimeter per millimeter
                'cm/cm': 1,                    # Centimeter per centimeter
                'm/m': 1,                      # Meter per meter
                'ft/ft': 1,                    # Foot per foot
                'yd/yd': 1                     # Yard per yard
            }
        }
        
        self.units = {
                        'Length': self.__basic_units['Length'],
                        'Time': self.__basic_units['Time'],
                        'Mass': self.__basic_units['Mass'],
                        'Temperature': self.__basic_units['Temperature'],
                        'Angle': self.__basic_units['Angle'],
                        'Area': self.__basic_units['Area'],
                        'Volume': self.__basic_units['Volume'],
                        'Specific_Weight': self.__basic_units['Specific_Weight'],
                        'E_G_K_Modulus': self.__basic_units['Pressure'],
                        'Coefficient_of_Thermal_Expansion': self.__basic_units['Coefficient_of_Thermal_Expansion'],
                        'Standard_Gravity': self.__basic_units['Acceleration'],
                        'Thermal_Conductivity': self.__basic_units['Thermal_Conductivity'],
                        'Concentrated_Force': self.__basic_units['Concentrated_Force'],
                        'Distributed_Force': self.__basic_units['Distributed_Force'],
                        'Moment': self.__basic_units['Work'],
                        'Area_Force': self.__basic_units['Pressure'],
                        'Pressure': self.__basic_units['Pressure'],
                        'Stress': self.__basic_units['Pressure'],
                        'Volume_Force': self.__basic_units['Volume_Force'],
                        'Velocity': self.__basic_units['Velocity'],
                        'Acceleration': self.__basic_units['Acceleration'],
                        'Angular_Velocity': self.__basic_units['Angular_Velocity'],
                        'Angular_Acceleration': self.__basic_units['Angular_Acceleration'],
                        'Displacement': self.__basic_units['Length'],
                        'Rotation': self.__basic_units['Angle'],
                        'First_Moment_of_Area': self.__basic_units['Volume'],
                        'Second_Moment_of_Area': self.__basic_units['Second_Moment_of_Area'],
                        'Flexural_Rigidity': self.__basic_units['Flexural_Rigidity'],
                        'Axial_Rigidity': self.__basic_units['Concentrated_Force'],
                        'Torsional_Rigidity': self.__basic_units['Flexural_Rigidity'],
                        'Mass_per_Unit_Length': self.__basic_units['Mass_per_Unit_Length'],
                        'Mass_Moments_of_Inertia': self.__basic_units['Mass_Moments_of_Inertia'],
                        'Frequency': self.__basic_units['Frequency'],
                        'Strain': self.__basic_units['Strain'],
                        'Unitless': {'':1}
                    }

        self.unit_vars = copy.deepcopy(list(self.units.keys()))
        self.unit_names = [unit_var.replace('_', ' ') for unit_var in self.unit_vars]

    def convert_temperature(self, from_value, from_unit, to_unit):
        if from_unit == to_unit:
            return from_value
        
        if from_unit == 'C':
            kelvin = from_value + 273.15
        elif from_unit == 'F':
            kelvin = (from_value - 32) * 5/9 + 273.15
        else:
            kelvin = from_value
        
        if to_unit == 'C':
            return kelvin - 273.15
        elif to_unit == 'F':
            return (kelvin - 273.15) * 9/5 + 32
        else:
            return kelvin
      
    def convert(self, from_value, unit_type, from_unit, to_unit, precision=14):
        if unit_type not in self.units:
            raise KeyError(f"Converter: Unit type '{unit_type}' not recognized")
        if from_unit not in self.units[unit_type]:
            raise KeyError(f"Converter: From unit '{from_unit}' not recognized for unit type '{unit_type}'")
        if to_unit not in self.units[unit_type]:
            raise KeyError(f"Converter: To unit '{to_unit}' not recognized for unit type '{unit_type}'")

        if unit_type == 'Temperature':
            result = self.convert_temperature(from_value, from_unit, to_unit)
        elif unit_type== 'Unitless':
            return from_value
        else:
            to_base_factor = self.units[unit_type][from_unit]
            base_value = from_value * to_base_factor

            from_base_factor = self.units[unit_type][to_unit]
            result = base_value / from_base_factor
            
            final_result = "{:#.{}g}".format(result, precision - 1)
            return float(final_result)

