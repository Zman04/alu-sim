from enum import Enum
import os

import cocotb

from cocotb.clock import Clock
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge

alu_sim_dir = os.path.abspath(os.path.join('.', 'alu_sim_dir'))

class Funct3(Enum):
    ADD = 0
    SLL = 1
    SLT = 2
    SLTU = 3
    XOR = 4
    SRL = 5
    SRA = 5
    OR = 6
    AND = 7


async def perform_not(dut) -> None:
    """
    ~

    :param dut: DUT object from cocotb
    :return: None
    """

    ones = 2 ** 32 - 1
    #input_value = int(dut.s1.value)
    #dut.s1.value = ones
    dut.s2.value = ones
    dut.funct3.value = 4
    await RisingEdge(dut.clk)


async def perform_negate(dut) -> None:
    """
    Perform the two's complement.

    :param dut: DUT object from cocotb
    :return: None
    """
    await perform_not(dut)

    await RisingEdge(dut.clk)

    dut.s1.value = dut.d.value
    dut.s2.value = 1
    dut.funct3.value = 0
    await RisingEdge(dut.clk)


async def perform_sub(dut, val1, val2) -> None:
    """
    sub rd, rs1, rs2

    :param dut: Dut object from cocotb
    :param s1: First value as described in R sub
    :param s2: Second value as described in R sub
    :return: None
    """


    dut.s1.value = val2
    await perform_negate(dut)

    await RisingEdge(dut.clk)

    dut.s1.value = val1
    dut.s2.value = int(dut.d.value)
    dut.funct3.value = 0

    await RisingEdge(dut.clk)



async def set_gt(dut, val1, val2):
    """
    In the same format as slt, rd, rsq, rs2 perform the operation to set the output LSB bit to rs1 > rs2.

    :param dut:
    :return:
    """

    dut.s1.value = val2
    dut.s2.value = val1

    dut.funct3.value = 3

    await RisingEdge(dut.clk)


async def set_gte(dut, val1, val2):
    """
    In the same format as slt rd, rs1, rs2 perform the operation to set the output LSB bit to rs1 >= rs2.

    :param dut: DUT object from cocotb
    :return:
    """

    dut.s1.value = val1
    dut.s2.value = val2
    dut.funct3.value = 3

    await RisingEdge(dut.clk)

    dut.s1.value = int(dut.d.value)
    dut.s2.value = 1

    dut.funct3.value = 4

    await RisingEdge(dut.clk)




async def f_set_e(dut, val1, val2):
    """
    In the same format as feq.s rd, rs1, rs2 perform a floating point equal comparison.

    :param dut:
    :return:
    """

    dut.s1.value = val1
    dut.s2.value = val2
    dut.funct3.value = 4

    await RisingEdge(dut.clk)

    dut.s1.value = int(dut.d.value)
    dut.s2.value = 1
    dut.funct3.value = 3

    await RisingEdge(dut.clk)


async def f_set_lt(dut, val1, val2):
    """
    In the same format as flt.s rd, rs1, rs2 perform a floating point less than comparison.

    :param dut:
    :return:
    """

    dut.s1.value = val1
    dut.s2.value = val2
    dut.funct3.value = 3

    await RisingEdge(dut.clk)


async def f_set_lte(dut, val1, val2):
    """
    In the same format as fle.s rd, rs1, rs2 perform a floating point less than or equal comparison.

    :param dut:
    :return:
    """

    dut.s1.value = val2
    dut.s2.value = val1
    dut.funct3.value = 3

    await RisingEdge(dut.clk)

    dut.s1.value = int(dut.d.value)
    dut.s2.value = 1
    dut.funct3.value = 4

    await RisingEdge(dut.clk)


async def perform_multiplication(dut, val1, val2):
    """
    In the same format as mul rd, rs1, rs2 perform multiplication.

    :param dut:
    :return:
    """

    product = 0

    for i in range(32):
        dut.s1.value = val2
        dut.s2.value = 1

        dut.funct3.value = 7 # Test Multiplier 0

        await RisingEdge(dut.clk)

        if int(dut.d.value):
            dut.s1.value = product
            dut.s2.value = val1

            dut.funct3.value = 0

            await RisingEdge(dut.clk)

            product = int(dut.d.value)

        else:
            pass

        dut.s1.value = val1 # Assign multiplicand to first pin
        dut.s2.value = 1 # Shift 1

        dut.funct3.value = 1 # sll

        await RisingEdge(dut.clk)

        val1 = int(dut.d.value) # Newly shifted result is now on output wire

        dut.s1.value = val2 # Assign multiplier to first pin
        dut.s2.value = 1 # Shift right one

        dut.funct3.value = 5 #srl

        await RisingEdge(dut.clk)

        val2 = int(dut.d.value)

        dut.s1.value = product
        dut.s2.value = 0

        dut.funct3.value = 0

        await RisingEdge(dut.clk)




async def perform_division(dut):
    """
    In the same format as mul rd, rs1, rs2 perform multiplication.

    :param dut:
    :return:
    """

@cocotb.test()
async def run_alu_sim(dut):
    clock = Clock(dut.clk, period=10, units='ns') # This assigns the clock into the ALU
    cocotb.start_soon(clock.start(start_high=False))

    '''print("Hello World!")

    await RisingEdge(dut.clk)
    dut.s1.value = 3
    await perform_not(dut)

    print("clock 0: %s" % dut.d.value)

    await RisingEdge(dut.clk)
    print("clock 1: %s" % dut.d.value)

    await RisingEdge(dut.clk)
    print("clock 2: %s" % dut.d.value)

    await RisingEdge(dut.clk)
    dut.s1.value = 5
    await perform_negate(dut)
    await RisingEdge(dut.clk)
    print("perform negate: %s" % dut.d.value)

    await RisingEdge(dut.clk)
    await perform_sub(dut, 5, 5)
    await RisingEdge(dut.clk)
    print("perform subtraction: %s" %dut.d.value)

    await RisingEdge(dut.clk)
    await set_gt(dut, 10, 2)
    await RisingEdge(dut.clk)
    print("set gt: %s" %dut.d.value)

    await RisingEdge(dut.clk)
    await set_gte(dut, 10, 2)
    await RisingEdge(dut.clk)
    print("set gte: %s" %dut.d.value)

    await RisingEdge(dut.clk)
    await f_set_lt(dut, 10, 2)
    await RisingEdge(dut.clk)
    print("f_set_lt: %s" %dut.d.value)

    await RisingEdge(dut.clk)
    await f_set_e(dut, 5, 5)
    await RisingEdge(dut.clk)
    print("f_set_e %s" %dut.d.value)

    await RisingEdge(dut.clk)
    await f_set_lte(dut, 6, 6)
    await RisingEdge(dut.clk)
    print("f_set_lte %s" %dut.d.value)'''

    await RisingEdge(dut.clk)
    await perform_multiplication(dut, 2, 1)
    await RisingEdge(dut.clk)
    print("Multiplication %s" %dut.d.value)

def test_via_cocotb():
    """
    Main entry point for cocotb
    """
    verilog_sources = [os.path.abspath(os.path.join('.', 'alu.v'))]
    runner = get_runner("verilator")
    runner.build(
        verilog_sources=verilog_sources,
        vhdl_sources=[],
        hdl_toplevel="RISCALU",
        build_args=["--threads", "2"],
        build_dir=alu_sim_dir,
    )
    runner.test(hdl_toplevel="RISCALU", test_module="alu_sim")

if __name__ == '__main__':
    test_via_cocotb()
