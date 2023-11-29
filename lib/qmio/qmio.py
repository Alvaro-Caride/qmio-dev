"""Qmio helper module"""
import subprocess
import json
from qmio.utils import RunCommandError


PREFIX = "/mnt/Q_SWAP"


def run(circuit, shots=100, backend='simulator_rtcs',
        results='results.json', execution_metrics='execution_metrics.json',
        instructions='instructions.p'):
    """Run the given circuit

    :param circuit: circuit can be given in any of the following formats:
        * qasm filename: filename ends with suffix '.qasm'
        * instructions filename: filename ends with suffix '.p'
        * qasm string: a QASM string
    :param shots: number of shots
    :param backend: backend to use to run the circuit
    :param results: filename where to store the results
    :param execution_metrics: filename where to store the execution metrics

    :return: Python dictionary containing the results of the execution
    """
    if circuit.startswith('OPENQASM 2.0'):
        return run_qasm_str(circuit, shots=shots,
                            backend=backend, results=results,
                            execution_metrics=execution_metrics)
    elif circuit.endswith('.qasm'):
        return run_qasm(circuit, shots=shots,
                        backend=backend, results=results,
                        execution_metrics=execution_metrics)
    elif circuit.endswith('.p'):
        return run_instructions(circuit, shots=shots,
                                backend=backend, results=results,
                                execution_metrics=execution_metrics)
    raise UnknownCircuitTypeError('Unknown circuit type')


def run_qasm_str(qasm_str, results='results.json',
             execution_metrics='execution_metrics.json', shots=100,
             backend='simulator_rtcs'):
    """Run a circuit from a qasm string

    :param qasm_string: qasm string representing the circuit
    :param results: filename where to store the results
    :param execution_metrics: filename where to store the execution metrics
    :param shots: number of shots
    :param backend: backend to use to run the circuit

    :return: Python dictionary containing the results of the execution
    """
    filename = ".circuit.qasm"
    with open(filename, "w") as f:
        f.write(qasm_str)
    return run_qasm(filename, results=results, execution_metrics=execution_metrics,
             shots=shots, backend=backend)


def run_qasm(qasm_filename, results='results.json',
             execution_metrics='execution_metrics.json', shots=100,
             backend='simulator_rtcs'):
    """Run a qasm circuit reading it from the given file

    :param qasm_filename: filename with the qasm circuit
    :param results: filename where to store the results
    :param execution_metrics: filename where to store the execution metrics
    :param shots: number of shots
    :param backend: backend to use to run the circuit

    :return: Python dictionary containing the results of the execution
    """
    tmp_instructions_filename = 'instructions.p'
    compile(qasm_filename, output_filename=tmp_instructions_filename,
            shots=shots, backend=backend)
    return run_instructions(tmp_instructions_filename, results=results,
                            execution_metrics=execution_metrics, shots=shots,
                            backend=backend)


def run_instructions(instructions, results='results.json',
                     execution_metrics='execution_metrics.json', shots=100,
                     backend='simulator_rtcs'):
    """Run a compiled circuit reading it from the given file

    :param instructions: filename with the instructions of the compiled circuit
    :param results: filename where to store the results
    :param execution_metrics: filename where to store the execution metrics
    :param shots: number of shots
    :param backend: backend to use to run the circuit

    :return: Python dictionary containing the results of the execution
    """
    cmd = (
        f"sbatch --wait {PREFIX}/qmio/backends/{backend}/run.sh "
        f"{instructions} {results} {execution_metrics} {shots}"
    )

    print("Submitting run job to slurm")
    #print("DEBUG: ", cmd)
    p = subprocess.run(cmd, shell=True)
    if p.returncode != 0:
        raise RunCommandError('The slurm job failed')
    print(f"Finished running, results in: {results}")
    print(f"Finished running, execution metrics in: {execution_metrics}")
    out = None
    with open(results) as f:
        out = json.load(f)
    return out


def compile(qasm_filename, output_filename='instructions.p', shots=100,
            backend='simulator_rtcs'):
    """Compile a qasm circuit and generate a instructions file

    :param qasm_filename: filename with the circuit in qasm format
    :param output_filename: filename with the circuit in qasm format
    :param shots: number of shots
    :param backend: backend to use to run the circuit

    :return:
    """
    cmd = (
        f"sbatch --wait {PREFIX}/qmio/backends/{backend}/compile.sh "
        f"{qasm_filename} {output_filename} {shots}"
    )

    print("Submitting compile job to slurm")
    #print("DEBUG: ", cmd)
    p = subprocess.run(cmd, shell=True)
    if p.returncode != 0:
        raise RunCommandError('The slurm job failed')
    print(f"Finished generating instructions file: {output_filename}")


class UnknownCircuitTypeError(Exception):
    pass