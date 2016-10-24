import h5py
import numpy as np
import time
from helper_functions import date_version_string
from Grid import Grid
from Species import Species

class Simulation(object):
    """Contains data from one run of the simulation:
    NT: number of iterations
    NGrid: Number of points on the grid
    NParticle: Number of particles (one species right now)
    L: Length of the simulation domain
    epsilon_0: the physical constant
    particle_positions, velocities: shape (NT, NParticle) numpy arrays of historical particle data
    charge_density, electric_field: shape (NT, NGrid) numpy arrays of historical grid data
    """
    def __init__(self, NT, dt, epsilon_0, grid, list_species, date_ver_str):
        self.grid = grid
        self.charge_density_history = np.empty((NT, grid.NG))
        self.electric_field_history = np.empty((NT, grid.NG))
        self.potential_history = np.empty((NT, grid.NG))
        self.mode_energy_history = np.empty((NT, grid.NG))

        self.all_species = []
        self.position_history = {}
        self.velocity_history = {}
        for species in list_species:
            self.all_species.append(species)
            self.position_history[species] = np.empty((NT, species.N))
            self.velocity_history[species] = np.empty((NT, species.N))

        self.kinetic_energy = np.empty(NT)
        self.field_energy = np.empty(NT)
        self.total_energy = np.empty(NT)
        self.epsilon_0, self.NT, self.dt = epsilon_0, NT, dt

        self.date_ver_str = date_ver_str

    def update_grid(self, i, grid):
        """Update the i-th set of field values"""
        self.charge_density_history[i] = grid.charge_density
        self.electric_field_history[i] = grid.electric_field
        self.potential_history[i] = grid.electric_field

    def update_particles(self, i, list_species):
        """Update the i-th set of particle values"""
        for species in list_species:
            self.position_history[species][i] = species.x
            self.velocity_history[species][i] = species.v

    def update_diagnostics(self, i, kinetic_energy, field_energy, total_energy):
        self.kinetic_energy[i] = kinetic_energy
        self.field_energy[i] = field_energy
        self.total_energy[i] = total_energy
    #
    # def fill_grid(self, charge_density, electric_field):
    #     self.charge_density, self.electric_field = charge_density, electric_field
    #
    # def fill_particles(self, particle_positions, particle_velocities):
    #     self.particle_positions = particle_positions
    #     self.particle_velocities = particle_velocities
    #
    # def fill_diagnostics(self, diagnostics):
    #     kinetic_energy, field_energy, total_energy = diagnostics
    #     self.kinetic_energy = kinetic_energy
    #     self.field_energy = field_energy
    #     self.total_energy = total_energy

    ######
    # data access
    ######

    def save_data(self, filename=time.strftime("%Y-%m-%d_%H-%M-%S.hdf5")):
        """Save simulation data to hdf5.
        filename by default is the timestamp for the simulation."""

        S = self
        with h5py.File(filename, "w") as f:
            grid_data = f.create_group('grid')
            grid_data.attrs['NGrid'] = S.grid.NG
            grid_data.attrs['L'] = S.grid.L
            grid_data.attrs['epsilon_0'] = S.epsilon_0
            grid_data.create_dataset(name="x", dtype=float, data=S.grid.x)

            grid_data.create_dataset(name="rho", dtype=float, data=S.charge_density_history)
            grid_data.create_dataset(name="Efield", dtype=float, data=S.electric_field_history)
            grid_data.create_dataset(name="potential", dtype=float, data=S.potential_history)

            all_species = f.create_group('species')
            for species in S.all_species:
                species_data = all_species.create_group(species.name)
                species_data.attrs['name'] = species.name
                species_data.attrs['N'] = species.N
                species_data.attrs['q'] = species.q
                species_data.attrs['m'] = species.m

                species_data.create_dataset(name="x", dtype=float, data=S.position_history[species])
                species_data.create_dataset(name="v", dtype=float, data=S.velocity_history[species])

            f.create_dataset(name="Kinetic energy", dtype=float, data=S.kinetic_energy) #TODO: move to species
            f.create_dataset(name="Field energy", dtype=float, data=S.field_energy)
            f.create_dataset(name="Total energy", dtype=float, data=S.total_energy)

            f.attrs['dt'] = S.dt
            f.attrs['NT'] = S.NT
            f.attrs['date_ver_str'] = date_version_string()
        print("Saved file to {}".format(filename))
        return filename

    def __eq__(self, other):
        # return "boo"
        result = True
        result *= self.date_ver_str == other.date_ver_str
        result *= self.epsilon_0 == other.epsilon_0
        result *= self.NT == other.NT
        result *= self.dt == other.dt
        return result


def read_hdf5_group(group):
    print("Group:", group)
    for i in group:
        print(i, group[i])
    for attr in group.attrs:
        print(attr, group.attrs[attr])


def load_data(filename):
    """Create a Simulation object from a hdf5 file"""
    with h5py.File(filename, "r") as f:
        grid_data = f['grid']

        L = grid_data.attrs['L']
        NGrid = grid_data.attrs['NGrid']
        charge_density = grid_data['rho'][...]
        field = grid_data['Efield'][...]
        potential = grid_data['potential'][...]
        epsilon_0 = grid_data.attrs['epsilon_0']

        grid = Grid(L, NGrid, epsilon_0)

        all_species = []
        particle_histories = {}
        for species_group_name in f['species']:
            species_group = f['species'][species_group_name]

            position_history = species_group['x'][...]
            velocity_history = species_group['v'][...]
            name = species_group.name
            particle_histories[name] = ((position_history, velocity_history))
            N = species_group.attrs['N']
            q = species_group.attrs['q']
            m = species_group.attrs['m']
            species = Species(q, m, N, name)
            all_species.append(species)

        kinetic_energy = f['Kinetic energy'][...]
        field_energy = f['Field energy'][...]
        total_energy = f['Total energy'][...]

        NT = f.attrs['NT']
        dt = f.attrs['dt']

        date_ver_str = f.attrs['date_ver_str']

    S = Simulation(NT, dt, epsilon_0, grid, all_species, date_ver_str)
    S.charge_density_history = charge_density
    S.electric_field_history = field
    S.potential_history = potential
    S.kinetic_energy = kinetic_energy
    S.field_energy = field_energy
    S.total_energy = total_energy
    for species in all_species:
        S.position_history, S.velocity_history = particle_histories[species.name]
    return S

def test_simulation_equality():
    g = Grid(L=2 * np.pi, NG=32)
    N = 128
    electrons = Species(-1.0, 1.0, N, "electrons")
    positrons = Species(1.0, 1.0, N, "positrons")
    NT = 100
    dt = 0.1
    epsilon_0 = 1
    date_ver_str = date_version_string()

    filename = "simulation_data_format.hdf5"
    S = Simulation(NT, dt, epsilon_0, g, [electrons, positrons], date_ver_str)
    S.save_data(filename)

    S_loaded = load_data(filename)
    assert S == S_loaded, "Simulations not equal!"

if __name__=="__main__":
    test_simulation_equality()
