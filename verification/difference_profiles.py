"""Adversarial Boolean profiles for the six perfect-play languages.

Engine: games are profiles over the six models (q, E, I, J, U, C), constrained by the
proved inclusions q<=E<=I<=U<=C and q<=J<=U.  AND = coordinatewise min, OR = coordinatewise
max (the exact game-operations lemma of Section 9.1).  Every unknown coordinate of a
family is quantified ADVERSARIALLY over all values consistent with the inclusions and with
the facts actually proved about that family.  A reduction passes only if membership in
X\\Y equals the target predicate for every truth assignment and every adversarial
completion.

Part B: exhaustive search over all monotone Boolean formulas in 5 inputs (7581 of them)
for a D_2-reduction to a NESTED difference without a shared family.  Part C: entropy
arithmetic for the one-bridge separator and the companion Fock root.
"""
import itertools, math

M = ['q', 'E', 'I', 'J', 'U', 'C']
IDX = {m: i for i, m in enumerate(M)}
ORDER = [('q', 'E'), ('E', 'I'), ('I', 'U'), ('U', 'C'), ('q', 'J'), ('J', 'U')]


def consistent(p):
    return all(p[IDX[a]] <= p[IDX[b]] for a, b in ORDER)


def completions(spec):
    """spec: dict model -> 0/1 or None (unknown). Yield all consistent full profiles."""
    free = [m for m in M if spec.get(m) is None]
    for vals in itertools.product([0, 1], repeat=len(free)):
        p = [0] * 6
        for m in M:
            if spec.get(m) is not None:
                p[IDX[m]] = spec[m]
        for m, v in zip(free, vals):
            p[IDX[m]] = v
        if consistent(p):
            yield tuple(p)


def AND(*ps):
    return tuple(min(c) for c in zip(*ps))


def OR(*ps):
    return tuple(max(c) for c in zip(*ps))


def diff(p, X, Y):
    return p[IDX[X]] == 1 and p[IDX[Y]] == 0


# ---- the families, with ONLY the proved facts fixed -------------------------------
def Gs(A):   # spatial Weyl-clock family, companion paper Theorem 7.1 and this paper Section 8
    # Only the companion's spatial coordinates and finite-dimension exclusion
    # are assumed. Finite-host and remaining coordinates are adversarial.
    return {'q': 0, 'E': A, 'I': A, 'J': None, 'U': None, 'C': None}


def Gs_known(A):  # with the Section 8 fact U = C = 1 (used only in Part B)
    return {'q': 0, 'E': A, 'I': A, 'J': 0, 'U': 1, 'C': 1}


def Gt(A):   # selector and group verifier, equations (30), (31)
    return {'q': None, 'E': None, 'I': None, 'J': A, 'U': A, 'C': 1}


def Mco(B):  # a Pi1-hard PERF_co family (Slofstra / MNY); everything else adversarial
    return {'q': None, 'E': None, 'I': None, 'J': None, 'U': None, 'C': B}


def GM(Hh):  # MIP*=RE perfect-completeness family: q = halts; NO => omega_q <= 1/2
    if Hh:
        return {'q': 1, 'E': 1, 'I': 1, 'J': 1, 'U': 1, 'C': 1}
    return {'q': 0, 'E': 0, 'I': 0, 'J': None, 'U': None, 'C': None}


const = lambda **kw: {m: kw[m] for m in M}
R = const(q=0, E=1, I=1, J=0, U=1, C=1)      # rooted isometry game, E \ J
T = const(q=0, E=0, I=0, J=1, U=1, C=1)      # tracial solution-group game, J \ I
KCat = const(q=0, E=0, I=1, J=0, U=1, C=1)   # Catalan game, I \ E (and not II_1)
Q = const(q=0, E=0, I=0, J=0, U=0, C=1)      # fixed III-only game


def check(name, X, Y, build, families, target, nargs):
    """build(list_of_profiles) -> profile; families(args) -> list of specs."""
    ok = True
    for args in itertools.product([0, 1], repeat=nargs):
        specs = families(*args)
        for profs in itertools.product(*[list(completions(s)) for s in specs]):
            p = build(*profs)
            assert consistent(p)
            if diff(p, X, Y) != target(*args):
                ok = False
                print('  FAIL', name, args, profs, p)
                break
    print(('PASS ' if ok else 'FAIL ') + name)
    return ok


res = []
c = lambda s: s  # identity for constant specs
# 1. q column
res.append(check('E\\q  Sigma2-hard  G^s_e', 'E', 'q', lambda g: g, lambda a: [Gs(a)], lambda a: a == 1, 1))
res.append(check('I\\q  Sigma2-hard  G^s_e', 'I', 'q', lambda g: g, lambda a: [Gs(a)], lambda a: a == 1, 1))
res.append(check('J\\q  Sigma2-hard  G^t_e AND T', 'J', 'q', lambda g, t: AND(g, t), lambda a: [Gt(a), T], lambda a: a == 1, 1))
res.append(check('U\\q  Sigma2-hard  G^t_e AND T', 'U', 'q', lambda g, t: AND(g, t), lambda a: [Gt(a), T], lambda a: a == 1, 1))
# 2. C row
for X, fam in [('E', Gs), ('I', Gs), ('J', Gt), ('U', Gt)]:
    res.append(check('C\\%s  Pi2-hard  G_X(e) OR Q' % X, 'C', X, lambda g, qq: OR(g, qq), lambda a, fam=fam: [fam(a), Q], lambda a: a == 0, 1))
res.append(check('C\\q  Pi1-hard  M_e AND R', 'C', 'q', lambda m, r: AND(m, r), lambda b: [Mco(b), R], lambda b: b == 1, 1))
res.append(check('C\\q  under omega_q=1: G_M OR KCat (Pi1 = not halts)', 'C', 'q', lambda g, k: OR(g, k), lambda h: [GM(h), KCat], lambda h: h == 0, 1))
# 3. incomparable pairs: Gamma(e,f) = (G_X(e) AND R_X) OR (G_Y(f) AND R_Y)
inc = [('I', 'J', Gs, R, Gt, T), ('J', 'I', Gt, T, Gs, R), ('E', 'J', Gs, R, Gt, T), ('J', 'E', Gt, T, Gs, R)]
for X, Y, FX, RX, FY, RY in inc:
    res.append(check('%s\\%s  D2-hard  Gamma' % (X, Y), X, Y,
                     lambda gx, rx, gy, ry: OR(AND(gx, rx), AND(gy, ry)),
                     lambda a, b, FX=FX, RX=RX, FY=FY, RY=RY: [FX(a), RX, FY(b), RY],
                     lambda a, b: a == 1 and b == 0, 2))
# 4. shared-family D2: Lambda(e,f) = L_e AND (H OR L_f)
res.append(check('I\\E  D2-hard  L=G^s (L_E holds by Thm 7.1), H=KCat', 'I', 'E',
                 lambda le, h, lf: AND(le, OR(h, lf)), lambda a, b: [Gs(a), KCat, Gs(b)],
                 lambda a, b: a == 1 and b == 0, 2))
res.append(check('U\\J  D2-hard  L=G^t (L_J holds by equation (31)), H=R', 'U', 'J',
                 lambda le, h, lf: AND(le, OR(h, lf)), lambda a, b: [Gt(a), R, Gt(b)],
                 lambda a, b: a == 1 and b == 0, 2))
# 5. both-sided hardness of the remaining nested entries
for X, Y, Fx, Fy, H in [('U', 'I', Gt, Gs, T), ('U', 'E', Gt, Gs, T), ('I', 'E', Gs, Gs, KCat), ('U', 'J', Gt, Gt, R)]:
    res.append(check('%s\\%s  Sigma2-hard  G_X(e) AND H' % (X, Y), X, Y, lambda g, h: AND(g, h), lambda a, Fx=Fx, H=H: [Fx(a), H], lambda a: a == 1, 1))
    res.append(check('%s\\%s  Pi2-hard    G_Y(e) OR H' % (X, Y), X, Y, lambda g, h: OR(g, h), lambda a, Fy=Fy, H=H: [Fy(a), H], lambda a: a == 0, 1))
# 6. no-universal-rate family H_e = KCat OR V_e
res.append(check('H_e = KCat OR V_e: in I always, in E iff FIN', 'I', 'E', lambda k, v: OR(k, v), lambda a: [KCat, Gs(a)], lambda a: a == 0, 1))
# promise paddings
ok = True
for spec in [Gs(0), Gs(1), Gt(0), Gt(1)]:
    for p in completions(spec):
        p1 = OR(p, tuple(Q[m] for m in M))
        p2 = AND(p, OR(tuple(R[m] for m in M), tuple(T[m] for m in M)))
        ok &= all(p1[IDX[m]] == p[IDX[m]] for m in 'qEIJU') and p1[IDX['C']] == 1
        ok &= all(p2[IDX[m]] == p[IDX[m]] for m in 'EIJUC') and p2[IDX['q']] == 0
print(('PASS ' if ok else 'FAIL ') + 'paddings: OR Q fixes q..U, sets C=1; AND (R OR T) fixes E..C, kills q')
res.append(ok)

# ---- Part B: monotone-formula obstruction for nested U\I without a shared family ------
def monotone(n):
    if n == 0:
        return [(0,), (1,)]
    prev = monotone(n - 1)
    out = []
    for f0 in prev:
        for f1 in prev:
            if all(x <= y for x, y in zip(f0, f1)):
                out.append(f0 + f1)  # index: top bit = last variable
    return out

MON5 = monotone(5)
print('monotone functions of 5 variables:', len(MON5), '(Dedekind number 7581)')


def ev(f, bits):  # bits[0] is least significant variable
    return f[sum(b << i for i, b in enumerate(bits))]


def search_nested(Xc, Yc, fams, label):
    """fams: list of 5 callables (Ae, Af) -> list of possible (x, y) pairs (adversarial)."""
    found = []
    for f in MON5:
        good = True
        for Ae, Af in itertools.product([0, 1], repeat=2):
            opts = [fam(Ae, Af) for fam in fams]
            for choice in itertools.product(*opts):
                xs = [c_[0] for c_ in choice]
                ys = [c_[1] for c_ in choice]
                if (ev(f, xs) == 1 and ev(f, ys) == 0) != (Ae == 1 and Af == 0):
                    good = False
                    break
            if not good:
                break
        if good:
            found.append(f)
    print('%s: %d monotone 5-input formulas realise A(e) & not A(f)' % (label, len(found)))
    return found

# (U, I) coordinates.  G^t_e: U = A(e), I = w <= A(e) adversarial.  G^s_e: I = A(e), U = 1 (known).
gt_e = lambda Ae, Af: [(Ae, w) for w in (0, 1) if w <= Ae]
gt_f = lambda Ae, Af: [(Af, w) for w in (0, 1) if w <= Af]
gs_e = lambda Ae, Af: [(1, Ae)]
gs_f = lambda Ae, Af: [(1, Af)]
sep = lambda Ae, Af: [(1, 0)]
f1 = search_nested('U', 'I', [gt_e, gt_f, gs_e, gs_f, sep], 'U\\I, families G^t, G^s, separator T (adversarial w)')
# even the optimistic case w == 0 (no selector-family instance is spatial-perfect):
gt_e0 = lambda Ae, Af: [(Ae, 0)]
gt_f0 = lambda Ae, Af: [(Af, 0)]
f2 = search_nested('U', 'I', [gt_e0, gt_f0, gs_e, gs_f, sep], 'U\\I, same, optimistic w = 0')
# control: with a shared family L (U = I = A) the search must succeed
L_e = lambda Ae, Af: [(Ae, Ae)]
L_f = lambda Ae, Af: [(Af, Af)]
f3 = search_nested('U', 'I', [L_e, L_f, sep, gs_e, gs_f], 'control: shared family L_H present')
res.append(len(f1) == 0 and len(f2) == 0 and len(f3) > 0)

# ---- Part C: entropy arithmetic -------------------------------------------------------
def H(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0)

# Fixed one-bridge separator: p_m=2^(-m-1), entropy exactly 2 bits.
separator_entropy=sum((m+1)*2.0**(-m-1) for m in range(200))
assert abs(separator_entropy-2)<1e-12
print('One-bridge separator root: entropy %.12f bits' % separator_entropy)
# 4-ary Fock tree of the companion paper: 4^m words of weight (3/4) 16^-m
SF = sum((4 ** m) * ((3 / 4) * 16 ** (-m)) * -math.log2((3 / 4) * 16 ** (-m)) for m in range(100))
print('Companion Fock root: H = %.12f, paper log2(4/3)+4/3 = %.12f' % (SF, math.log2(4 / 3) + 4 / 3))
# one FMS bridge has DENSITY ratio 2: a single-isometry one-bridge root would carry p_n = 2^-(n+1)
p1 = [2 ** (-(n + 1)) for n in range(200)]
print('one-bridge single isometry: H = %.12f (2 bits)' % H(p1))
print('scaffold mass check 1+4(2+4+8+16) =', 1 + 4 * (2 + 4 + 8 + 16))
print()
assert all(res), 'Boolean profile check failed'
assert len(MON5)==7581 and len(f1)==0 and len(f2)==0 and len(f3)==351
print('ALL PASS')
