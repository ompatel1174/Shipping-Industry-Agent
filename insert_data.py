import random
from datetime import datetime, timedelta
from collections import defaultdict
from app.database import get_connection

# --------------------------
# Configuration
# --------------------------

YEARS = [2023, 2024, 2025]
SHIP_COUNT = 15
VOYAGES_PER_YEAR = 4

FUEL_TYPES = {
    "HSHFO": 3.114,
    "VLSFO380": 3.114,
    "VLSFO": 3.114,
    "LSMGO": 3.206,
    "LNG": 2.750,
    "BIO_B100": 0.500
}

vessel_classes = ["Bulk Carrier", "Container Ship", "Tanker", "LNG Carrier"]
v_group_codes = ["GRP-A", "GRP-B", "GRP-C", None]


def calculate_cii(aer):
    if aer < 5:
        return "A"
    elif aer < 8:
        return "B"
    elif aer < 11:
        return "C"
    elif aer < 15:
        return "D"
    else:
        return "E"


def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for ship_index in range(1, SHIP_COUNT + 1):
            ship_code = f"SC{str(ship_index).zfill(3)}"
            vessel_name = f"Vessel-{ship_code}"
            dwt = round(random.uniform(30000, 100000), 2)
            vessel_class = random.choice(vessel_classes)

            for year in YEARS:
                yearly_distance = 0
                yearly_co2 = 0
                yearly_fuel_totals = defaultdict(float)

                for voyage_index in range(1, VOYAGES_PER_YEAR + 1):
                    voyage_number = f"VY-{year}-{voyage_index}"

                    start_date = datetime(year, random.randint(1, 10), random.randint(1, 20))
                    duration_hours = round(random.uniform(200, 800), 2)
                    end_date = start_date + timedelta(hours=duration_hours)
                    distance = round(random.uniform(2000, 10000), 2)

                    total_co2 = 0

                    for fuel_name, factor in FUEL_TYPES.items():
                        consumption = round(random.uniform(50, 500), 3)
                        co2_generated = consumption * factor

                        cursor.execute("""
                            INSERT INTO fuel_consumption (
                                record_id, fuel_type_id, voyage_no, vessel_coach_id, year,
                                me_consumption_mt, aux_consumption_mt, boil_consumption_mt,
                                fuel_loss_mt, l_calorific_value_kj_kg, remaining_on_board_mt,
                                bunkered_mt, est_remain_on_arrival_mt
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            voyage_number,
                            fuel_name,
                            voyage_number,
                            ship_code,
                            year,
                            consumption * 0.7,
                            consumption * 0.2,
                            consumption * 0.05,
                            consumption * 0.05,
                            42000,
                            round(random.uniform(300, 700), 2),
                            round(random.uniform(100, 500), 2),
                            round(random.uniform(200, 600), 2)
                        ))

                        total_co2 += co2_generated
                        yearly_fuel_totals[fuel_name] += consumption

                    avg_speed = round(distance / duration_hours, 2)
                    aer = round(total_co2 / (dwt * distance) * 1e6, 3)

                    cursor.execute("""
                        INSERT INTO voyage_summary (
                            year, revision_id, vessel_name, ship_code, dwt_mt,
                            v_group_code, vessel_class, voyage_number,
                            start_date, end_date, duration_hours, avg_speed_kn,
                            distance_observed_nm, co2_emissions_mt,
                            co2_reefer_correction_mt, aer, cii_rating,
                            hshfo_consumption_mt, vlsfo380_consumption_mt,
                            vlsfo_consumption_mt, lsmgo_consumption_mt,
                            lng_consumption_mt, bio_b100_consumption_mt
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        year, 1, vessel_name, ship_code, dwt,
                        random.choice(v_group_codes), vessel_class, voyage_number,
                        start_date, end_date, duration_hours, avg_speed,
                        distance, round(total_co2, 3),
                        round(random.uniform(10, 200), 3),
                        aer, calculate_cii(aer),
                        yearly_fuel_totals["HSHFO"],
                        yearly_fuel_totals["VLSFO380"],
                        yearly_fuel_totals["VLSFO"],
                        yearly_fuel_totals["LSMGO"],
                        yearly_fuel_totals["LNG"],
                        yearly_fuel_totals["BIO_B100"]
                    ))

                    yearly_distance += distance
                    yearly_co2 += total_co2

                aer_year = round(yearly_co2 / (dwt * yearly_distance) * 1e6, 3)

                cursor.execute("""
                    INSERT INTO emission_summary (
                        year, revision_id, vessel_name, ship_code, dwt_mt,
                        v_group_code, vessel_class, is_cii_eligible,
                        distance_observed_nm, duration_hours, avg_speed_kn,
                        co2_emissions_mt, cii_rating, aer,
                        hshfo_consumption_mt, vlsfo380_consumption_mt,
                        vlsfo_consumption_mt, lsmgo_consumption_mt,
                        lng_consumption_mt, bio_b100_consumption_mt
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    year, 1, vessel_name, ship_code, dwt,
                    random.choice(v_group_codes), vessel_class, True,
                    yearly_distance, 0, 0,
                    round(yearly_co2, 3),
                    calculate_cii(aer_year), aer_year,
                    yearly_fuel_totals["HSHFO"],
                    yearly_fuel_totals["VLSFO380"],
                    yearly_fuel_totals["VLSFO"],
                    yearly_fuel_totals["LSMGO"],
                    yearly_fuel_totals["LNG"],
                    yearly_fuel_totals["BIO_B100"]
                ))

        conn.commit()
        print("Data inserted successfully!")

    except Exception as e:
        conn.rollback()
        print("Error occurred:", e)

    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()