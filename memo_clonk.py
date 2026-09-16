import numpy as np
from math import gcd
from sympy import symbols, Matrix, Integer
import pprint

mod = 12

# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------

def mod_inv(a, m):
    """Modular inverse of numeric a modulo m, assuming gcd(a, m) == 1."""
    a = int(round(float(a))) % m
    if gcd(a, m) != 1:
        raise ValueError(f"No inverse for {a} modulo {m}")
    t, new_t = 0, 1
    r, new_r = m, a
    while new_r != 0:
        q = r // new_r
        t, new_t = new_t, t - q * new_t
        r, new_r = new_r, r - q * new_r
    return t % m

def rref_mod(M, m):
    """Row-reduce matrix M modulo m. Returns reduced matrix and pivot columns."""
    M = M.copy()
    rows, cols = M.shape
    pivot_cols = []
    r = 0

    for c in range(cols):
        if r >= rows:
            break

        # Find pivot with numeric unit entry in column c
        pivot_row = None
        for i in range(r, rows):
            val = M[i, c]
            if val != 0 and val.is_number:
                iv = int(round(float(val))) % m
                if iv != 0 and gcd(iv, m) == 1:
                    pivot_row = i
                    break

        if pivot_row is None:
            continue

        if pivot_row != r:
            M.row_swap(pivot_row, r)

        pivot_val = M[r, c]
        inv = mod_inv(pivot_val, m)
        # Normalize pivot row
        for j in range(c, cols):
            M[r, j] = (M[r, j] * inv) % m

        # Clear column c
        for i in range(rows):
            if i != r:
                factor = M[i, c] % m
                if factor != 0:
                    for j in range(c, cols):
                        M[i, j] = (M[i, j] - factor * M[r, j]) % m

        pivot_cols.append(c)
        r += 1

    return M, pivot_cols


# ------------------------------------------------------------

# ------------------------------------------------------------
# Compute the left kernel space
# ------------------------------------------------------------

from sympy import lcm

def ker_AT_integer(A):
    """
    Compute a basis for ker(A^T) over Z.
    Returns a list of row vectors (Matrix(1, n)) with integer entries.
    """
    ker = A.T.nullspace()   # basis of kernel over Q
    basis = []
    for v in ker:
        # v is a column vector with rationals
        denoms = [c.as_numer_denom()[1] for c in v]
        L = Integer(1)
        for d in denoms:
            L = lcm(L, d)
        v_int = (L * v).applyfunc(lambda x: Integer(x))  # integer column
        basis.append(v_int.T)                            # row vector
    return basis


def reduce_mod12_basis(basis, m=12):
    """Reduce integer basis vectors modulo m and row-reduce to a simple basis."""
    if not basis:
        return []

    B = Matrix(basis)
    # Reduce entries mod m
    for i in range(B.rows):
        for j in range(B.cols):
            B[i, j] = Integer(int(B[i, j]) % m)
    
    # Row-reduce modulo m using your rref_mod
    B_rref, _ = rref_mod(B, m)

    # Extract nonzero rows as basis
    simple_basis = []
    for i in range(B_rref.rows):
        row = B_rref[i, :]
        if any(int(row[j]) % m != 0 for j in range(B_rref.cols)):
            simple_basis.append(row)
    return simple_basis


def basis_row_to_expr(row, b_vars, m=12):
    """Given row (1 x n) and b_vars, return expr = sum(row[i]*b_i) modulo m."""
    expr = Integer(0)
    for i, bi in enumerate(b_vars):
        coeff = int(row[0, i]) % m
        if coeff != 0:
            expr += Integer(coeff) * bi
    return expr  # meaning: expr == 0 (mod m)

def center_coeffs_expr(expr, m=12):
    """Map 0..m-1 to centered reps (e.g. 11 -> -1) for nicer printing."""
    def is_int(e): return isinstance(e, Integer)
    def map_int(e):
        n = int(e)
        return Integer(((n + m//2) % m) - m//2)
    return expr.replace(is_int, map_int).expand()


#------------------------------------------------------------------
# Setup the matrix and find solvability criterion
#------------------------------------------------------------------


pins = {
    'UL': 0,
    'UR': 1,
    'DR': 2,
    'DL': 3,
    'U': 4,
    '\\': 5,
    'L': 6,
    'R': 7,
    '/': 8,
    'D': 9,
    'dl': 10,
    'dr': 11,
    'ur': 12,
    'ul': 13,
    "ALL": 14,
    'all': 15
}

# 7 simul pin set:
# pin_set = np.array([0, 2, 5, 6, 7, 10, 12])

# pin set:
pin_names = ['UL', 'UR', 'dl', '\\', 'ur', 'D']
pin_names = ['UL', 'DL', 'dr', 'ur', '\\', 'R']

# These two gave same conditions
# pin_names = ['UL', 'UR', 'DR', 'U', '\\', 'L']
# pin_names = ['UL', 'UR', 'DR', 'U', '\\', 'dr']

pin_names = ['UL', 'UR', 'DR', 'U', '\\', 'ur']
# pin_names = ['UL', 'UR', 'DR', 'U', '/', 'ur']



# the "scramble", but we look at it as variables.
b_vars = symbols(
    # 'UL U UR L C R DL D DR yU yL yC yR yD'
    'UL U UR L C R DL D DR d r c l u'
)

U = np.array([
#   UL UR DR DL U  \\  L  R  /  D  dl dr ur ul ALL all
    [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0],
    [1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
], dtype=int)

D = np.array([
#    UL  UR  DR  DL  U   \\   L   R   /   D   dl  dr  ur  ul ALL all
    [ 0,  1,  1,  1,  0,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  1,  1,  0,  1,  1,  0,  0,  1,  0,  0,  1,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  1,  1,  0,  1,  1,  0,  1,  0,  0,  1,  0,  0,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  1,  0,  1,  1,  0,  1,  0,  1,  0,  0,  1,  0,  0,  0,  1],
    [-1, -1, -1, -1,  0, -1, -1, -1, -1, -1,  0,  0, -1, -1,  0, -1],
    [-1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1,  0,  0, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1],
    [-1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1,  0,  0, -1,  0, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0,  0,  0, -1],
], dtype=int)

pin_set = np.array([ pins[e] for e in pin_names])
# A = Matrix(np.concatenate((U[:, pin_set], np.zeros((14, 1), dtype=int), D[:, pin_set], np.zeros((14, 1), dtype=int)), axis=1))
A = Matrix(np.concatenate((U[:, pin_set], D[:, pin_set]), axis=1))


#------------------------------------------------------------------
# Using the left kernel method:
#------------------------------------------------------------------

# ker_int = ker_AT_integer(A)
#
# ker_mod12_basis = reduce_mod12_basis(ker_int, mod)
#
# print("Constraints on b (pretty, centered coeffs):")
# for row in ker_mod12_basis:
#     expr = basis_row_to_expr(row, b_vars, mod)
#     expr_pretty = center_coeffs_expr(expr, mod)
#     print(f"{expr_pretty} == 0 (mod {mod})")


#------------------------------------------------------------------
# Using the row reduce [A | b] method
#------------------------------------------------------------------

def center_int(n, m=12):
    """Map integer n to centered representative in [-m/2, m/2)."""
    return Integer(((int(n) + m//2) % m) - m//2)

def prettify_expr_mod12(expr, m=12):
    """
    - Remove Mod(·, m) wrappers (we interpret everything mod m anyway).
    - Reduce all Integer coefficients mod m.
    - Center coefficients around 0 (e.g. 11 -> -1).
    """
    # 1. strip Mod(...) wrappers
    def is_mod(e): return e.func.__name__ == 'Mod'
    def strip_mod(e): return e.args[0]
    expr = expr.replace(is_mod, strip_mod)

    # 2. center Integer coefficients mod m
    def is_int(e): return isinstance(e, Integer)
    def map_int(e): return center_int(e, m)
    expr = expr.replace(is_int, map_int)

    return expr.expand()

def prettify_rref_mod12(RREF, m=12):
    """
    Apply prettify_expr_mod12 to each entry of the row-reduced [A|b] matrix.
    Returns a new Matrix with cleaned expressions.
    """
    R = Matrix(RREF)  # copy
    for i in range(R.rows):
        for j in range(R.cols):
            R[i, j] = prettify_expr_mod12(R[i, j], m)
    return R

# ----- usage with your RREF from rref_mod(Aug, mod) -----
# RREF, pivots = rref_mod(Aug, mod)



Aug = A.row_join(-Matrix(b_vars))  # [A | b] with symbolic b

RREF, pivots = rref_mod(Aug, mod)


R_pretty = prettify_rref_mod12(RREF, mod)

print("Row-reduced [A | b] modulo 12 (prettified):")
for row in R_pretty.tolist():
    print(row)


for i in range(6):
    print(f"{pin_names[i]}: ({R_pretty.tolist()[i][-1]}, {R_pretty.tolist()[i+6][-1]})")

