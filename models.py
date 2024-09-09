import json
from pydantic import BaseModel, Field, validator, ValidationError # type: ignore
from dataclasses import dataclass
from enum import Enum
import argparse
import dearpygui.dearpygui as dpg  # type: ignore
from typing import List

# Custom Exception Definitions
class CustomValidationException(Exception):
    """Exception raised for custom validation errors."""
    pass

class InvalidPlanetNameException(CustomValidationException):
    def __init__(self, planet_name: str):
        self.planet_name = planet_name
        super().__init__(f"Invalid planet name: {planet_name}")


# String Enum for planets
class PlanetEnum(str, Enum):
    MERCURY = "Mercury"
    VENUS = "Venus"
    EARTH = "Earth"
    MARS = "Mars"


# Pydantic Model with Predefined Validators
class AstronomicalBody(BaseModel):
    name: str = Field(..., description="Name of the planet")
    radius: float = Field(..., gt=0, description="Radius of the planet in km")
    atmosphere_composition: List[str] = Field(..., description="Gases in the atmosphere")

    @validator('name')
    def validate_name(cls, v):
        if v not in PlanetEnum._value2member_map_:
            raise InvalidPlanetNameException(v)
        return v

    @validator('radius')
    def validate_radius(cls, v):
        if v <= 0:
            raise ValueError("Radius must be a positive number.")
        return v

    def to_json(self) -> str:
        """Serialize the model to JSON."""
        return self.json()

    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize the model from JSON."""
        return cls.parse_raw(json_str)


# Data class definition
@dataclass
class Star:
    name: str
    temperature: float  # Kelvin

    def __str__(self):
        return f"{self.name} (Temperature: {self.temperature}K)"


# Main entry point with CLI using argparse
def main():
    # Setup argparse CLI
    parser = argparse.ArgumentParser(description="Astronomical Body Simulation CLI")
    parser.add_argument('--name', type=str, required=True, help="Name of the planet")
    parser.add_argument('--radius', type=float, required=True, help="Radius of the planet in kilometers")
    parser.add_argument('--atmosphere', type=str, nargs='+', help="List of gases in the atmosphere")
    args = parser.parse_args()

    # Create an AstronomicalBody object using Pydantic
    try:
        body = AstronomicalBody(name=args.name, radius=args.radius, atmosphere_composition=args.atmosphere)
        print("Astronomical Body Created:", body)
        print("Serialized to JSON:", body.to_json())

        # Simulate saving to a file
        json_data = body.to_json()
        print("\nDeserializing from JSON...")
        restored_body = AstronomicalBody.from_json(json_data)
        print("Restored Astronomical Body:", restored_body)

    except ValidationError as e:
        print("Validation Error:", e)
    except InvalidPlanetNameException as e:
        print(e)

    # Create a data class instance
    sun = Star(name="Sun", temperature=5778)
    print(sun)

    # Start a DearPyGui window
    dpg.create_context()

    with dpg.window(label="Astronomical GUI"):
        dpg.add_text(f"Planet Name: {body.name}")
        dpg.add_text(f"Radius: {body.radius} km")
        dpg.add_text(f"Atmosphere: {', '.join(body.atmosphere_composition)}")
        dpg.add_text(f"Star: {sun}")

    dpg.create_viewport(title='Astronomical Simulator', width=600, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


# Use the main entry point
if __name__ == "__main__":
    main()