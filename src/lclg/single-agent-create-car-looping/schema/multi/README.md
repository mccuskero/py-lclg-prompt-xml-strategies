# JSON Schema Files

This directory contains JSON Schema files generated from XSD.

**Generated on:** 2025-09-28 17:53:12 UTC
**Source XSD:** car.xsd

## File Structure

- `schema.json` - Master schema file with $ref references to individual types
- `types/` - Individual type definition files
- `README.md` - This catalog file

## Type Definitions

| File | Type Name | Schema Type | Description |
|------|-----------|-------------|-------------|
| `types/body-style-enum.json` | bodyStyleEnum | string | No description available |
| `types/body-type.json` | bodyType | object | Body structure and appearance details |
| `types/car-type.json` | carType | object | A complete car structure with all major components.      ... |
| `types/electrical-system-enum.json` | electricalSystemEnum | string | No description available |
| `types/electrical-type.json` | electricalType | object | Electrical system components and specifications |
| `types/engine-type.json` | engineType | object | Engine specifications and components |
| `types/fuel-type-enum.json` | fuelTypeEnum | string | No description available |
| `types/material-enum.json` | materialEnum | string | No description available |
| `types/season-enum.json` | seasonEnum | string | No description available |
| `types/tire-type.json` | tireType | object | Tire specifications and details |

## Usage

To reference these schemas in your application:

```json
{ "$ref": "schema.json" }
```

Or reference individual types:

```json
{ "$ref": "types/person-type.json" }
```
