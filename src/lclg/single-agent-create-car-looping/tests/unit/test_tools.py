"""Unit tests for tool classes."""

import pytest
import json
from tools.engine_tools import EngineConfigurationTool, EngineSpecificationTool
from tools.body_tools import BodyConfigurationTool, BodyStyleTool
from tools.electrical_tools import ElectricalConfigurationTool, ElectricalSystemTool
from tools.tire_tools import TireConfigurationTool, TireSizingTool


class TestEngineTools:
    """Test engine configuration tools."""

    def test_engine_configuration_tool_init(self):
        """Test EngineConfigurationTool initialization."""
        tool = EngineConfigurationTool()

        assert tool.name == "configure_engine"
        assert tool.description is not None
        assert hasattr(tool, 'logger')

    def test_engine_configuration_run_sedan(self):
        """Test engine configuration for sedan."""
        tool = EngineConfigurationTool()

        result = tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        data = json.loads(result)
        assert "engineType" in data
        assert data["engineType"]["fuelType"] == "gasoline"
        assert "horsepower" in data["engineType"]

    def test_engine_configuration_run_electric(self):
        """Test engine configuration for electric vehicle."""
        tool = EngineConfigurationTool()

        result = tool._run(
            vehicle_type="sedan",
            fuel_preference="electric",
            electric_capable=True
        )

        data = json.loads(result)
        assert data["engineType"]["fuelType"] == "electric"

    def test_engine_configuration_run_performance(self):
        """Test engine configuration for performance vehicle."""
        tool = EngineConfigurationTool()

        result = tool._run(
            vehicle_type="coupe",
            performance_level="performance",
            fuel_preference="gasoline"
        )

        data = json.loads(result)
        assert "engineType" in data
        # Performance should get more powerful engine
        hp = int(data["engineType"]["horsepower"].split()[0])
        assert hp > 200

    def test_engine_specification_tool_init(self):
        """Test EngineSpecificationTool initialization."""
        tool = EngineSpecificationTool()

        assert tool.name == "get_engine_specs"
        assert tool.description is not None

    def test_engine_specification_run(self):
        """Test getting engine specifications."""
        tool = EngineSpecificationTool()

        result = tool._run(engine_type="v6_gasoline")

        data = json.loads(result)
        assert "specifications" in data
        assert data["specifications"]["displacement"] == "3.5L"


class TestBodyTools:
    """Test body configuration tools."""

    def test_body_configuration_tool_init(self):
        """Test BodyConfigurationTool initialization."""
        tool = BodyConfigurationTool()

        assert tool.name == "configure_body"
        assert tool.description is not None

    def test_body_configuration_run_sedan(self):
        """Test body configuration for sedan."""
        tool = BodyConfigurationTool()

        result = tool._run(
            style="sedan",
            performance_level="standard"
        )

        data = json.loads(result)
        assert "bodyType" in data
        assert data["bodyType"]["style"] == "sedan"
        assert data["bodyType"]["doors"] == 4

    def test_body_configuration_run_suv(self):
        """Test body configuration for SUV."""
        tool = BodyConfigurationTool()

        result = tool._run(
            style="suv",
            customization_level="premium"
        )

        data = json.loads(result)
        assert data["bodyType"]["style"] == "suv"
        assert data["bodyType"]["doors"] == 4
        assert data["bodyType"]["@customized"] == True

    def test_body_configuration_run_with_color(self):
        """Test body configuration with specific color."""
        tool = BodyConfigurationTool()

        result = tool._run(
            style="coupe",
            color_preference="red"
        )

        data = json.loads(result)
        assert data["bodyType"]["color"] == "red"

    def test_body_style_tool_init(self):
        """Test BodyStyleTool initialization."""
        tool = BodyStyleTool()

        assert tool.name == "get_body_style_info"
        assert tool.description is not None

    def test_body_style_tool_run(self):
        """Test getting body style information."""
        tool = BodyStyleTool()

        result = tool._run(style="sedan", detailed=True)

        data = json.loads(result)
        assert "style_info" in data
        assert data["style_info"]["style"] == "sedan"


class TestElectricalTools:
    """Test electrical system tools."""

    def test_electrical_configuration_tool_init(self):
        """Test ElectricalConfigurationTool initialization."""
        tool = ElectricalConfigurationTool()

        assert tool.name == "configure_electrical_system"
        assert tool.description is not None

    def test_electrical_configuration_run_gasoline(self):
        """Test electrical configuration for gasoline engine."""
        tool = ElectricalConfigurationTool()

        result = tool._run(
            engine_type="gasoline",
            vehicle_requirements="standard sedan"
        )

        data = json.loads(result)
        assert "electricalType" in data
        assert "12V" in data["electricalType"]["batteryVoltage"]

    def test_electrical_configuration_run_electric(self):
        """Test electrical configuration for electric vehicle."""
        tool = ElectricalConfigurationTool()

        result = tool._run(
            engine_type="electric",
            hybrid_capable=True
        )

        data = json.loads(result)
        assert "electricalType" in data
        # Electric should have higher voltage
        assert "high-voltage" in data["electricalType"]["@systemType"].lower() or \
               "400V" in data["electricalType"]["batteryVoltage"]

    def test_electrical_system_tool_init(self):
        """Test ElectricalSystemTool initialization."""
        tool = ElectricalSystemTool()

        assert tool.name == "get_electrical_system_info"
        assert tool.description is not None

    def test_electrical_system_tool_run(self):
        """Test getting electrical system information."""
        tool = ElectricalSystemTool()

        result = tool._run(system_type="12V")

        data = json.loads(result)
        assert "system_info" in data


class TestTireTools:
    """Test tire configuration tools."""

    def test_tire_configuration_tool_init(self):
        """Test TireConfigurationTool initialization."""
        tool = TireConfigurationTool()

        assert tool.name == "configure_tires"
        assert tool.description is not None

    def test_tire_configuration_run_sedan(self):
        """Test tire configuration for sedan."""
        tool = TireConfigurationTool()

        result = tool._run(
            body_style="sedan",
            performance_level="standard"
        )

        data = json.loads(result)
        assert "tireType" in data
        assert "size" in data["tireType"]
        assert "brand" in data["tireType"]

    def test_tire_configuration_run_performance(self):
        """Test tire configuration for performance vehicle."""
        tool = TireConfigurationTool()

        result = tool._run(
            body_style="coupe",
            performance_level="performance"
        )

        data = json.loads(result)
        assert "tireType" in data
        # Performance tires
        assert data["tireType"]["@season"] in ["performance", "summer", "all-season"]

    def test_tire_configuration_run_winter(self):
        """Test tire configuration for winter."""
        tool = TireConfigurationTool()

        result = tool._run(
            body_style="suv",
            climate_preference="winter"
        )

        data = json.loads(result)
        assert "tireType" in data
        assert data["tireType"]["@season"] == "winter"

    def test_tire_sizing_tool_init(self):
        """Test TireSizingTool initialization."""
        tool = TireSizingTool()

        assert tool.name == "get_tire_sizing"
        assert tool.description is not None

    def test_tire_sizing_tool_run(self):
        """Test getting tire sizing information."""
        tool = TireSizingTool()

        result = tool._run(tire_size="225/60R16", detailed_analysis=True)

        data = json.loads(result)
        assert "sizing_info" in data or "tire_size" in data
