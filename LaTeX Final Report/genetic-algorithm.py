import pygad.kerasga

keras_ga = pygad.kerasga.KerasGA(model=lstm_model,num_solutions=10)

from tensorflow.keras.losses import MeanAbsoluteError

def fitness_func(ga_instance, solution, sol_idx):
    global X_train, y_train, keras_ga, lstm_model

    predictions = pygad.kerasga.predict(model=lstm_model,solution=solution,data=X_train)

    mae = tensorflow.keras.losses.MeanAbsoluteError()
    abs_error = mae(data_outputs, predictions).numpy() + 0.00000001
    solution_fitness = 1.0/abs_error

    return solution_fitness

def on_generation(ga_instance):
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution()[1]}")

num_generations = 250
num_parents_mating = 5
initial_population = keras_ga.population_weights

ga_instance = pygad.GA(num_generations=num_generations,num_parents_mating=num_parents_mating,initial_population=initial_population,fitness_func=fitness_func,on_generation=on_generation)

ga_instance.run()