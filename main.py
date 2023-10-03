import src.solver as solver
import src.utilities.helper.helper as helper

# Test solver
duration = solver.calculate_duration("A", "B")
solution = solver.solve_vrp_problem()

# Test utils
today = helper.get_current_date()

# Print results
print(f'Duration: {duration}')
print(f'Solution: {solution}')
print(f'Today: {today}')