# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""The RYRZ 2-local circuit."""

from typing import Union, Optional, List, Tuple, Callable, Any
from numpy import pi

from qiskit.circuit import QuantumCircuit, Instruction
from qiskit.circuit.library.standard_gates import RYGate, RZGate, CZGate
from .two_local import TwoLocal


class RYRZ(TwoLocal):
    r"""The RYRZ 2-local circuit.

    The RYRZ circuit consists of layers of :math:`Y` plus :math:`Z` rotations with entanglements.
    It can be used to prepare trial wave functions for variational quantum algorithms.

    .. parsed-literal::

        ┌──────────┐┌──────────┐ ░        ░       ░ ┌───────────┐┌───────────┐
        ┤ RY(θ[0]) ├┤ RZ(θ[3]) ├─░──■─────░─ ... ─░─┤ RY(θ[12]) ├┤ RZ(θ[15]) ├
        ├──────────┤├──────────┤ ░  │     ░       ░ ├───────────┤├───────────┤
        ┤ RY(θ[1]) ├┤ RZ(θ[4]) ├─░──■──■──░─ ... ─░─┤ RY(θ[13]) ├┤ RZ(θ[16]) ├
        ├──────────┤├──────────┤ ░     │  ░       ░ ├───────────┤├───────────┤
        ┤ RY(θ[2]) ├┤ RZ(θ[5]) ├─░─────■──░─ ... ─░─┤ RY(θ[14]) ├┤ RZ(θ[17]) ├
        └──────────┘└──────────┘ ░        ░       ░ └───────────┘└───────────┘

    See :class:`~qiskit.circuit.library.RY` for more detail on the possible arguments and options
    such as skipping unentanglement qubits, which apply here too.

    Examples:

        >>> ryrz = RYRZ(3, reps=1)  # create the variational form on 3 qubits
        >>> print(ryrz)  # show the circuit
             ┌──────────┐┌──────────┐      ┌──────────┐┌──────────┐
        q_0: ┤ RY(θ[0]) ├┤ RZ(θ[3]) ├─■──■─┤ RY(θ[6]) ├┤ RZ(θ[9]) ├─────────────
             ├──────────┤├──────────┤ │  │ └──────────┘├──────────┤┌───────────┐
        q_1: ┤ RY(θ[1]) ├┤ RZ(θ[4]) ├─■──┼──────■──────┤ RY(θ[7]) ├┤ RZ(θ[10]) ├
             ├──────────┤├──────────┤    │      │      ├──────────┤├───────────┤
        q_2: ┤ RY(θ[2]) ├┤ RZ(θ[5]) ├────■──────■──────┤ RY(θ[8]) ├┤ RZ(θ[11]) ├
             └──────────┘└──────────┘                  └──────────┘└───────────┘

        >>> ryrz = RYRZ(4, entanglement='circular', reps=1)
        >>> qc = QuantumCircuit(3)  # create a circuit and append the RY variational form
        >>> qc += ryrz.to_circuit()
        >>> qc.decompose().draw()
             ┌──────────┐┌──────────┐      ┌──────────┐┌───────────┐
        q_0: ┤ RY(θ[0]) ├┤ RZ(θ[4]) ├─■──■─┤ RY(θ[8]) ├┤ RZ(θ[12]) ├──────────────────────────
             ├──────────┤├──────────┤ │  │ └──────────┘└┬──────────┤┌───────────┐
        q_1: ┤ RY(θ[1]) ├┤ RZ(θ[5]) ├─┼──■──────■───────┤ RY(θ[9]) ├┤ RZ(θ[13]) ├─────────────
             ├──────────┤├──────────┤ │         │       └──────────┘├───────────┤┌───────────┐
        q_2: ┤ RY(θ[2]) ├┤ RZ(θ[6]) ├─┼─────────■────────────■──────┤ RY(θ[10]) ├┤ RZ(θ[14]) ├
             ├──────────┤├──────────┤ │                      │      ├───────────┤├───────────┤
        q_3: ┤ RY(θ[3]) ├┤ RZ(θ[7]) ├─■──────────────────────■──────┤ RY(θ[11]) ├┤ RZ(θ[15]) ├
             └──────────┘└──────────┘                               └───────────┘└───────────┘
    """

    def __init__(self,
                 num_qubits: Optional[int] = None,
                 entanglement_blocks: Union[
                     str, type, Instruction, QuantumCircuit,
                     List[Union[str, type, Instruction, QuantumCircuit]]
                 ] = CZGate,
                 entanglement: Union[str, List[List[int]], Callable[[int], List[int]]] = 'full',
                 reps: int = 3,
                 skip_unentangled_qubits: bool = False,
                 skip_final_rotation_layer: bool = False,
                 parameter_prefix: str = 'θ',
                 insert_barriers: bool = False,
                 initial_state: Optional[Any] = None,
                 ) -> None:
        """Create a new RYRZ 2-local circuit.

        Args:
            num_qubits: The number of qubits of the RYRZ circuit.
            reps: Specifies how often the structure of a rotation layer followed by an entanglement
                layer is repeated.
            entanglement_blocks: The gates used in the entanglement layer. Can be specified via the
                name of a gate (e.g. ``'cx'``), the gate type itself (e.g. ``CXGate``) or a
                ``QuantumCircuit`` with two qubits.
                If only one gate is provided, the same gate is applied to each qubit.
                If a list of gates is provided, all gates are applied to each qubit in the provided
                order.
            entanglement: Specifies the entanglement structure. Can be a string ('full', 'linear'
                , 'circular' or 'sca'), a list of integer-pairs specifying the indices of qubits
                entangled with one another, or a callable returning such a list provided with
                the index of the entanglement layer.
                See the Examples section of :class:`~qiskit.circuit.library.TwoLocal` for more
                detail.
            initial_state: An `InitialState` object to prepend to the circuit.
            skip_unentangled_qubits: If True, the single qubit gates are only applied to qubits
                that are entangled with another qubit. If False, the single qubit gates are applied
                to each qubit in the Ansatz. Defaults to False.
            skip_final_rotation_layer: If False, a rotation layer is added at the end of the
                ansatz. If True, no rotation layer is added.
            parameter_prefix: The parameterized gates require a parameter to be defined, for which
                we use :class:`~qiskit.circuit.ParameterVector`.
            insert_barriers: If True, barriers are inserted in between each layer. If False,
                no barriers are inserted.

        """
        super().__init__(num_qubits=num_qubits,
                         rotation_blocks=[RYGate, RZGate],
                         entanglement_blocks=entanglement_blocks,
                         entanglement=entanglement,
                         reps=reps,
                         skip_unentangled_qubits=skip_unentangled_qubits,
                         skip_final_rotation_layer=skip_final_rotation_layer,
                         parameter_prefix=parameter_prefix,
                         insert_barriers=insert_barriers,
                         initial_state=initial_state)

    @property
    def parameter_bounds(self) -> List[Tuple[float, float]]:
        """Return the parameter bounds.

        Returns:
            The parameter bounds.
        """
        return self.num_parameters * [(-pi, pi)]
