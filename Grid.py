import numpy as np
from FourierSolver import PoissonSolver
from scatter import charge_density_deposition
from gather import interpolateField
import scipy.fftpack as fft


class Grid(object):
    def __init__(self, L=2 * np.pi, NG=32, epsilon_0=1):
        self.x, self.dx = np.linspace(0, L, NG, retstep=True, endpoint=False)
        self.charge_density = np.zeros_like(self.x)
        self.electric_field = np.zeros_like(self.x)
        self.potential = np.zeros_like(self.x)
        self.L = L
        self.NG = int(NG)
        self.epsilon_0 = epsilon_0
        self.k = NG * self.dx * fft.fftfreq(NG, self.dx)
        self.k[0] = 0.0001
        self.k_plot = self.k[:int(NG / 2)]
        self.energy_per_mode = np.zeros(int(NG / 2))

    def solve_poisson(self):
        self.electric_field, self.potential, self.energy_per_mode = PoissonSolver(self.charge_density, self.k, self.NG, epsilon_0=self.epsilon_0)
        return self.energy_per_mode.sum()

    def gather_charge(self, list_species):
        self.charge_density[:] = 0.0
        for species in list_species:
            self.charge_density += charge_density_deposition(self.x, self.dx, species.x, species.q)

    def electric_field_function(self, xp):
        return interpolateField(xp, self.electric_field, self.x, self.dx)

    def __eq__(self, other):
        result = True
        result *= np.isclose(self.x, other.x).all()
        result *= np.isclose(self.charge_density, other.charge_density).all()
        result *= np.isclose(self.electric_field, other.electric_field).all()
        result *= np.isclose(self.potential, other.potential).all()
        result *= self.dx == other.dx
        result *= self.L == other.L
        result *= self.NG == other.NG
        result *= self.epsilon_0 == other.epsilon_0
        return result
    # def plot(self, show=True):
    #     plt.plot(self.x, self.charge_density
