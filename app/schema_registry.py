"""
Schema Registry – Single source of truth for all table schemas.

Each entry describes a table, its columns, and the types of questions it can answer.
This registry is consumed by the vector store to enable semantic search.
"""

TABLE_SCHEMAS = [
    {
        "table_name": "fuel_consumption",
        "description": (
            "Stores detailed fuel consumption records for each voyage and vessel. "
            "Each row represents the consumption of a specific fuel type during a voyage, "
            "broken down into main engine, auxiliary, boiler, and fuel loss categories."
        ),
        "columns": [
            {"name": "record_id", "type": "VARCHAR", "description": "Unique record identifier, same as the voyage number."},
            {"name": "fuel_type_id", "type": "VARCHAR", "description": "Type of fuel used (e.g. HSHFO, VLSFO380, VLSFO, LSMGO, LNG, BIO_B100)."},
            {"name": "voyage_no", "type": "VARCHAR", "description": "Voyage number identifier (e.g. VY-2024-1)."},
            {"name": "vessel_coach_id", "type": "VARCHAR", "description": "Ship code identifying the vessel (e.g. SC001)."},
            {"name": "year", "type": "INTEGER", "description": "Reporting year of the consumption record."},
            {"name": "me_consumption_mt", "type": "NUMERIC", "description": "Main engine fuel consumption in metric tonnes."},
            {"name": "aux_consumption_mt", "type": "NUMERIC", "description": "Auxiliary engine fuel consumption in metric tonnes."},
            {"name": "boil_consumption_mt", "type": "NUMERIC", "description": "Boiler fuel consumption in metric tonnes."},
            {"name": "fuel_loss_mt", "type": "NUMERIC", "description": "Fuel loss in metric tonnes."},
            {"name": "l_calorific_value_kj_kg", "type": "NUMERIC", "description": "Lower calorific value in kJ/kg."},
            {"name": "remaining_on_board_mt", "type": "NUMERIC", "description": "Fuel remaining on board in metric tonnes."},
            {"name": "bunkered_mt", "type": "NUMERIC", "description": "Fuel bunkered (loaded) in metric tonnes."},
            {"name": "est_remain_on_arrival_mt", "type": "NUMERIC", "description": "Estimated fuel remaining on arrival in metric tonnes."},
        ],
        "sample_questions": [
            "What is the total fuel consumed by vessel SC001 in 2024?",
            "Compare main engine vs auxiliary fuel consumption across all ships.",
            "Which fuel type has the highest consumption in 2023?",
            "Show me LNG consumption breakdown by voyage.",
            "What is the average fuel loss per voyage?",
            "How much fuel was bunkered across all voyages in 2025?",
        ],
    },
    {
        "table_name": "voyage_summary",
        "description": (
            "Summarizes each individual voyage for a vessel, including route performance, "
            "fuel consumption totals by type, CO2 emissions, AER and CII rating. "
            "Each row represents one voyage."
        ),
        "columns": [
            {"name": "year", "type": "INTEGER", "description": "Reporting year."},
            {"name": "revision_id", "type": "INTEGER", "description": "Revision number for the record."},
            {"name": "vessel_name", "type": "VARCHAR", "description": "Human-readable vessel name."},
            {"name": "ship_code", "type": "VARCHAR", "description": "Unique ship identifier code."},
            {"name": "dwt_mt", "type": "NUMERIC", "description": "Deadweight tonnage of the vessel in metric tonnes."},
            {"name": "v_group_code", "type": "VARCHAR", "description": "Vessel group code (e.g. GRP-A, GRP-B, GRP-C), may be null."},
            {"name": "vessel_class", "type": "VARCHAR", "description": "Class of vessel (Bulk Carrier, Container Ship, Tanker, LNG Carrier)."},
            {"name": "voyage_number", "type": "VARCHAR", "description": "Unique voyage identifier."},
            {"name": "start_date", "type": "TIMESTAMP", "description": "Voyage start date and time."},
            {"name": "end_date", "type": "TIMESTAMP", "description": "Voyage end date and time."},
            {"name": "duration_hours", "type": "NUMERIC", "description": "Total voyage duration in hours."},
            {"name": "avg_speed_kn", "type": "NUMERIC", "description": "Average speed during the voyage in knots."},
            {"name": "distance_observed_nm", "type": "NUMERIC", "description": "Total distance observed in nautical miles."},
            {"name": "co2_emissions_mt", "type": "NUMERIC", "description": "Total CO2 emissions for the voyage in metric tonnes."},
            {"name": "co2_reefer_correction_mt", "type": "NUMERIC", "description": "CO2 reefer correction in metric tonnes."},
            {"name": "aer", "type": "NUMERIC", "description": "Annual Efficiency Ratio for the voyage."},
            {"name": "cii_rating", "type": "VARCHAR", "description": "Carbon Intensity Indicator rating (A, B, C, D, or E)."},
            {"name": "hshfo_consumption_mt", "type": "NUMERIC", "description": "HSHFO fuel consumption in metric tonnes."},
            {"name": "vlsfo380_consumption_mt", "type": "NUMERIC", "description": "VLSFO380 fuel consumption in metric tonnes."},
            {"name": "vlsfo_consumption_mt", "type": "NUMERIC", "description": "VLSFO fuel consumption in metric tonnes."},
            {"name": "lsmgo_consumption_mt", "type": "NUMERIC", "description": "LSMGO fuel consumption in metric tonnes."},
            {"name": "lng_consumption_mt", "type": "NUMERIC", "description": "LNG fuel consumption in metric tonnes."},
            {"name": "bio_b100_consumption_mt", "type": "NUMERIC", "description": "BIO B100 fuel consumption in metric tonnes."},
        ],
        "sample_questions": [
            "Show me all voyages for vessel SC005 in 2024.",
            "What is the average CO2 emission per voyage?",
            "Which voyage had the highest AER?",
            "List all voyages with CII rating D or E.",
            "What is the average speed across all voyages in 2025?",
            "Compare CO2 emissions between Container Ships and Tankers.",
            "Show top 5 ships by total distance traveled.",
        ],
    },
    {
        "table_name": "emission_summary",
        "description": (
            "Annual emission summary per vessel. Aggregates a vessel's yearly performance "
            "including total distance, CO2 emissions, CII rating, AER, and total fuel consumption "
            "by type. Each row represents one vessel-year combination."
        ),
        "columns": [
            {"name": "year", "type": "INTEGER", "description": "Reporting year."},
            {"name": "revision_id", "type": "INTEGER", "description": "Revision number."},
            {"name": "vessel_name", "type": "VARCHAR", "description": "Human-readable vessel name."},
            {"name": "ship_code", "type": "VARCHAR", "description": "Unique ship identifier code."},
            {"name": "dwt_mt", "type": "NUMERIC", "description": "Deadweight tonnage in metric tonnes."},
            {"name": "v_group_code", "type": "VARCHAR", "description": "Vessel group code, may be null."},
            {"name": "vessel_class", "type": "VARCHAR", "description": "Class of vessel."},
            {"name": "is_cii_eligible", "type": "BOOLEAN", "description": "Whether the vessel is eligible for CII rating."},
            {"name": "distance_observed_nm", "type": "NUMERIC", "description": "Total distance observed in nautical miles for the year."},
            {"name": "duration_hours", "type": "NUMERIC", "description": "Total operational hours for the year."},
            {"name": "avg_speed_kn", "type": "NUMERIC", "description": "Average operational speed in knots."},
            {"name": "co2_emissions_mt", "type": "NUMERIC", "description": "Total CO2 emissions for the year in metric tonnes."},
            {"name": "cii_rating", "type": "VARCHAR", "description": "Annual CII rating (A–E)."},
            {"name": "aer", "type": "NUMERIC", "description": "Annual Efficiency Ratio for the year."},
            {"name": "hshfo_consumption_mt", "type": "NUMERIC", "description": "Total HSHFO consumption for the year."},
            {"name": "vlsfo380_consumption_mt", "type": "NUMERIC", "description": "Total VLSFO380 consumption for the year."},
            {"name": "vlsfo_consumption_mt", "type": "NUMERIC", "description": "Total VLSFO consumption for the year."},
            {"name": "lsmgo_consumption_mt", "type": "NUMERIC", "description": "Total LSMGO consumption for the year."},
            {"name": "lng_consumption_mt", "type": "NUMERIC", "description": "Total LNG consumption for the year."},
            {"name": "bio_b100_consumption_mt", "type": "NUMERIC", "description": "Total BIO B100 consumption for the year."},
        ],
        "sample_questions": [
            "What is the total CO2 emission for the fleet in 2024?",
            "Which vessel has the best CII rating in 2025?",
            "Show year-over-year emission trends for all vessels.",
            "Compare AER across vessel classes.",
            "Which vessels are not CII eligible?",
            "What is the fleet-wide average fuel efficiency?",
            "Rank vessels by total CO2 emissions in 2023.",
        ],
    },
]


def get_schema_text(schema: dict) -> str:
    """Build a rich text representation of a table schema for embedding."""
    lines = [
        f"Table: {schema['table_name']}",
        f"Description: {schema['description']}",
        "",
        "Columns:",
    ]
    for col in schema["columns"]:
        lines.append(f"  - {col['name']} ({col['type']}): {col['description']}")

    lines.append("")
    lines.append("Example questions this table can answer:")
    for q in schema["sample_questions"]:
        lines.append(f"  - {q}")

    return "\n".join(lines)


def get_ddl_context(schema: dict) -> str:
    """Build a DDL-style context string for SQL generation prompts."""
    col_defs = ", ".join(
        f"{col['name']} {col['type']}" for col in schema["columns"]
    )
    return f"CREATE TABLE {schema['table_name']} ({col_defs});"
