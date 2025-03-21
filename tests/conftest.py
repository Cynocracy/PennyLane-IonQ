# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import numpy as np
import pytest

from pennylane_ionq import SimulatorDevice, QPUDevice


np.random.seed(42)


# ==========================================================
# Some useful global variables

# single qubit unitary matrix
U = np.array(
    [
        [0.83645892 - 0.40533293j, -0.20215326 + 0.30850569j],
        [-0.23889780 - 0.28101519j, -0.88031770 - 0.29832709j],
    ]
)

# two qubit unitary matrix
U2 = np.array([[0, 1, 1, 1], [1, 0, 1, -1], [1, -1, 0, 1], [1, 1, -1, 0]]) / np.sqrt(3)

# single qubit Hermitian observable
A = np.array([[1.02789352, 1.61296440 - 0.3498192j], [1.61296440 + 0.3498192j, 1.23920938 + 0j]])


# ==========================================================
# PennyLane devices

# List of all devices that support analytic expectation value
# computation. This generally includes statevector/wavefunction simulators.
analytic_devices = []

# List of all devices that do *not* support analytic expectation
# value computation. This generally includes hardware devices
# and hardware simulators.
hw_devices = [SimulatorDevice]

# List of all device shortnames
shortnames = [d.short_name for d in analytic_devices + hw_devices]


# ==========================================================
# pytest fixtures


@pytest.fixture
def tol(shots):
    """Numerical tolerance to be used in tests."""
    if shots == 0:
        # analytic expectation values can be computed,
        # so we can generally use a smaller tolerance
        return {"atol": 0.01, "rtol": 0}

    # for non-zero shots, there will be additional
    # noise and stochastic effects; will need to increase
    # the tolerance
    return {"atol": 0.05, "rtol": 0.1}


@pytest.fixture
def init_state(scope="session"):
    """Fixture to create an n-qubit initial basis state"""

    def _init_state(n):
        state = np.random.randint(0, 2, [n])
        ket = np.zeros([2 ** n])
        ket[np.ravel_multi_index(state, [2] * n)] = 1
        return state, ket

    return _init_state


@pytest.fixture(params=analytic_devices + hw_devices)
def device(request, shots):
    """Fixture to initialize and return a PennyLane device"""
    device = request.param

    if device not in analytic_devices and shots == 0:
        pytest.skip("Hardware simulators do not support analytic mode")

    def _device(n):
        return device(wires=n, shots=shots)

    return _device


@pytest.fixture
def requires_api():
    """Skips a test if the API key is not available"""
    key = os.environ.get("IONQ_API_KEY", None)
    if key is None or not key:
        pytest.skip("Skipping test as API key is not available")
