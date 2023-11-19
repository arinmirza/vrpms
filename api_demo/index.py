import datetime

from src.db.supabase.db_supabase_mapbox import get_mapbox_duration_data, get_mapbox_customers_data
from src.utilities.helper.result_2_output import tsp_result_2_output

from src.vrp.ant_colony.aco_hybrid import run as vrp_aco
from src.vrp.brute_force.brute_force import run as vrp_bf
from src.tsp.ant_colony.aco_hybrid import run_request as tsp_aco
from src.tsp.brute_force.brute_force import run_request as tsp_bf
from src.tsp.simulated_annealing.simulated_annealing import run_request as tsp_sa

SUPABASE_URL = "https://pkeygmzuwfucblldmkjn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s"
SUPABASE_URL_KEY_FILE = "../data/supabase/supabase_url_key.txt"


def run(query_params):
    program_mode = query_params["program_mode"][0] if "program_mode" in query_params else "no_program_mode"
    if program_mode not in ["vrp", "tsp"]:
        program_mode = "no_program_mode"
    algorithm = query_params["algorithm"][0] if "algorithm" in query_params else "no_algorithm"
    if algorithm not in ["aco", "bf", "sa"]:
        algorithm = "no_algorithm"
    input_dict = {"program_mode": program_mode, "algorithm": algorithm}
    result = "no_result"
    time_start = datetime.datetime.now()
    if program_mode != "no_program_mode" and algorithm != "no_algorithm":
        durations_id = int(query_params["durations_id"][0])
        duration = get_mapbox_duration_data(SUPABASE_URL, SUPABASE_KEY, None, durations_id)
        locations_id = int(query_params["locations_id"][0])
        locations = get_mapbox_customers_data(SUPABASE_URL, SUPABASE_KEY, None, locations_id)
        print(locations)
        if program_mode == "vrp":
            if algorithm == "aco":
                result = vrp_aco(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
            elif algorithm == "bf":
                result = vrp_bf(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
        elif program_mode == "tsp":
            start_time = float(query_params["start_time"][0])
            start_node = int(query_params["start_node"][0])
            # customers = query_params["customers"][0]
            customers = [1, 2, 3, 4, 5, 6]
            if algorithm == "aco":
                result = tsp_aco(start_time, start_node, customers, duration)
            elif algorithm == "bf":
                result = tsp_bf(start_time, start_node, customers, duration)
            elif algorithm == "sa":
                result = tsp_sa(start_time, start_node, customers, duration)
            if result != "no_result":
                result = tsp_result_2_output(start_time, start_node, duration, locations, result)
    time_end = datetime.datetime.now()
    time_diff = (time_end - time_start).total_seconds()
    # body = {"input_dict": input_dict, "result": result, "time_diff": time_diff}
    body = result
    print(body)


if __name__ == "__main__":
    query_params = {}
    query_params["program_mode"] = ["tsp"]
    query_params["algorithm"] = ["bf"]
    query_params["durations_id"] = ["1"]
    query_params["locations_id"] = ["1"]
    query_params["start_time"] = ["1"]
    query_params["start_node"] = ["1"]
    query_params["customers"] = ["1"]
    run(query_params)
