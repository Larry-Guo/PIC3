import numpy as np
import scipy.fftpack as fft


def PoissonSolver(rho, k, NG, epsilon_0=1):
    """solves the Poisson equation spectrally, via FFT

    the Poisson equation can be written either as
    (in position space)
    $$\nabla \cdot E = \rho/\epsilon_0$$
    $$\nabla^2 V = -\rho/\epsilon_0$$

    Assuming that all functions in fourier space can be represented as
    $$\exp{i(kx - \omega t)}$$
    It is easy to see that upon Fourier transformation $\nabla \to ik$, so

    (in fourier space)
    $$E = \rho /(ik \epsilon_0)$$
    $$V = \rho / (-k^2 \epsilon_0)$$

    Calculate that, fourier transform back to position space
    and both the field and potential pop out easily

    The conceptually problematic part is getting the $k$ wave vector right
    #TODO: finish this description
    """

    rho_F = fft.fft(rho)
    rho_F[0] = 0
    field_F = rho_F / (np.pi * 2j * k * epsilon_0)
    potential_F = field_F / (-2j * np.pi * k * epsilon_0)
    field = fft.ifft(field_F).real
    potential = fft.ifft(potential_F).real
    energy_presum = np.abs(rho_F * potential_F.conjugate())[:NG / 2] / NG * 2 * np.pi
    return field, potential, energy_presum
