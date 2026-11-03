"""Portable finite checks for the type-ladder paper (Python standard library only).

Exact sparse rational identities replace the original floating matrix checks.
A stand-in is not a representation of an arbitrary Higman/HNN presentation.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import contextlib, io, runpy
from certify_rotation import certificate

class Mat:
    def __init__(self,n,entries=None):
        self.n=n
        self.e={k:F(v) for k,v in (entries or {}).items() if v}
    @staticmethod
    def eye(n):
        return Mat(n,{(i,i):1 for i in range(n)})
    @staticmethod
    def diag(v):
        return Mat(len(v),{(i,i):x for i,x in enumerate(v) if x})
    def __add__(self,b):
        assert self.n==b.n
        d=self.e.copy()
        for k,v in b.e.items():
            d[k]=d.get(k,F(0))+v
        return Mat(self.n,d)
    def __sub__(self,b):
        return self+(-1)*b
    def __rmul__(self,a):
        return Mat(self.n,{k:a*v for k,v in self.e.items()})
    def __matmul__(self,b):
        assert self.n==b.n
        rows={}
        for (r,c),v in b.e.items():
            rows.setdefault(r,[]).append((c,v))
        out={}
        for (r,k),v in self.e.items():
            for c,w in rows.get(k,[]):
                out[r,c]=out.get((r,c),F(0))+v*w
        return Mat(self.n,out)
    @property
    def star(self):
        return Mat(self.n,{(c,r):v for (r,c),v in self.e.items()})
    def tensor(self,b):
        return Mat(self.n*b.n,{(r*b.n+x,c*b.n+y):v*w
            for (r,c),v in self.e.items() for (x,y),w in b.e.items()})
    def power(self,k):
        if k<0:return self.star.power(-k)
        out=Mat.eye(self.n)
        for _ in range(k):out=out@self
        return out
    def trace(self):
        return sum((v for (r,c),v in self.e.items() if r==c),F(0))
    def same(self,b):
        assert self.n==b.n and self.e==b.e, "Exact matrix mismatch"

def tree(n):
    words=[w for d in range(n+1) for w in itertools.product((0,1),repeat=d)]
    idx={w:i for i,w in enumerate(words)}
    depth=[len(w) for w in words]
    B=[Mat(len(words),{(idx[w+(i,)],idx[w]):1
        for w in words if len(w)<n}) for i in (0,1)]
    P=Mat.diag([int(d==n) for d in depth])
    Q=Mat.diag([int(d==0) for d in depth])
    C=Mat.diag([F(1,2**d) for d in depth])
    h=Mat.diag([F(1,(n+1)*2**d) for d in depth])
    return words,depth,B,P,Q,C,h

def check_tree():
    reports=[]
    for n in range(8):
        words,depth,B,P,Q,C,h=tree(n);I=Mat.eye(len(words))
        for i in (0,1):
            for j in (0,1):
                (B[i].star@B[j]).same((I-P) if i==j else 0*I)
            (C@B[i]).same(F(1,2)*(B[i]@C))
            (h@B[i]).same(F(1,2)*(B[i]@h))
        (B[0]@B[0].star+B[1]@B[1].star).same(I-Q)
        (C@Q).same(Q);(C@P).same(P@C)
        assert h.trace()==1
        assert (h@P).trace()==(h@Q).trace()==F(1,n+1)
        X=Q
        total=0*I
        for j in range(n+1):
            E=Mat.diag([int(d==j) for d in depth])
            X.same(E);total=total+X
            X=B[0]@X@B[0].star+B[1]@X@B[1].star
        total.same(I);X.same(0*I)
        # Check the telescoping identity and range support at every cutoff.
        X=I
        accum=0*I
        Y=Q
        for m in range(n+2):
            (accum+X).same(I)
            support=Mat.diag([int(d>=m) for d in depth])
            X.same(support)
            accum=accum+Y
            X=B[0]@X@B[0].star+B[1]@X@B[1].star
            Y=B[0]@Y@B[0].star+B[1]@Y@B[1].star
        probs=[F(1,(n+1)*2**d) for d in depth]
        entropy=-sum(float(q)*math.log2(float(q)) for q in probs)
        expected=math.log2(n+1)+n/2
        assert abs(entropy-expected)<2e-12
        # Exact mean depth proves the non-logarithmic entropy term.
        assert sum((F(d)*q for d,q in zip(depth,probs)),F(0))==F(n,2)
        residual=2*P
        assert (h@residual.star@residual).trace()==F(4,n+1)
        reports.append({"depth":n,"dimension":len(words),
            "defect_state_mass":str(F(1,n+1)),
            "residual_squared_norm":str(F(4,n+1)),
            "entropy_bits":entropy})
    return reports

def check_separator_and_scaffolds():
    # Finite truncations explicitly retain the top boundary defect.
    # The formulas are finite evidence for the shift model, not finite isometries.
    truncations=[]
    for n in range(2,10):
        I=Mat.eye(n);bottom=Mat.diag([1]+[0]*(n-1));top=Mat.diag([0]*(n-1)+[1])
        A=Mat(n,{(m+1,m):1 for m in range(n-1)})
        h=Mat.diag([F(1,2**(m+1)) for m in range(n)])
        (A.star@A).same(I-top);(A@A.star).same(I-bottom)
        (h@A).same(F(1,2)*(A@h))
        mass=h.trace();entropy=sum((F(m+1,2**(m+1)) for m in range(n)),F(0))
        assert mass==1-F(1,2**n)
        assert entropy==2-F(n+2,2**n)
        assert (h@bottom).trace()==F(1,2)
        truncations.append({'dimension':n,'mass':str(mass),'entropy_partial_bits':str(entropy)})
    scaffolds=[]
    for k in range(1,6):
        weights=[1]+[2**g for g in range(1,k+1) for _ in range(4)]
        z=sum(weights);h=Mat.diag([F(w,z) for w in weights]);n=len(weights)
        source=Mat.diag([1]+[0]*(n-1));transport=source
        previous=0
        for g in range(1,k+1):
            selected=1+4*(g-1)
            w=Mat(n,{(selected,previous):1})
            (h@w).same(2*(w@h))
            transport=w@transport;previous=selected
        (transport.star@transport).same(source)
        (h@transport).same((2**k)*(transport@h))
        assert z==1+4*sum(2**g for g in range(1,k+1))
        scaffolds.append({'bridges':k,'cover_mass':z,'root_mass':str(F(1,z))})
    return {'shift_truncations':truncations,'chain_scaffolds':scaffolds,
            'scope':'Finite matrix and geometric-series checks; infinite extraction is proved in the paper.'}


def comm(a,b):
    return a@b@a.star@b.star

def check_reader():
    I2=Mat.eye(2);X=Mat(2,{(0,1):1,(1,0):1})
    Z=Mat.diag([1,-1])
    plus=F(1,2)*(I2+X);minus=F(1,2)*(I2-X)
    b=plus.tensor(I2)+minus.tensor(Z)
    g=Z.tensor(I2);W=comm(b,g);T=I2.tensor(X)
    W.same(I2.tensor(Z));(W@W).same(Mat.eye(4))
    assert W.trace()==0
    (T@W@T.star).same((-1)*W)
    a=Mat(4,{((i+1)%4,i):1 for i in range(4)})
    reports=[]
    for n in range(5):
        words,depth,B,P,Q,C,h=tree(n);It=Mat.eye(len(words));I4=Mat.eye(4)
        c=a.power(-n)@g@a.power(n)
        E=[Mat.diag([int(d==j) for d in depth]) for j in range(n+1)]
        gd=[a.power(j)@c@a.power(-j) for j in range(n+1)]
        L=Mat(len(words)*4)
        for Ej,gj in zip(E,gd):L=L+Ej.tensor(gj)
        aa=It.tensor(a);bb=It.tensor(b);cc=It.tensor(c);TT=It.tensor(T)
        Pt=P.tensor(I4);Qt=Q.tensor(I4);Ct=C.tensor(I4)
        Bt=[Bi.tensor(I4) for Bi in B]
        (L@Qt).same(cc@Qt)
        for Bi in Bt:
            (L@Bi).same(Bi@aa@L@aa.star)
            (aa@Bi).same(Bi@aa);(TT@Bi).same(Bi@TT)
        (L@Ct).same(Ct@L);(L@Pt).same(Pt@L)
        for Ej,gj in zip(E,gd):
            Et=Ej.tensor(I4)
            (L@Et).same(It.tensor(gj)@Et)
        word=comm(bb,L)
        (Pt@(TT@word@TT.star+word)).same(0*Pt)
        hn=h.tensor(F(1,4)*I4)
        residual=2*Pt
        assert (hn@residual.star@residual).trace()==F(4,n+1)
        # Terminal row graph expansion, for an arbitrary non-self-adjoint row.
        sP=2*Pt-Mat.eye(Pt.n)
        A=TT@word@TT.star+word
        (Pt@A).same(F(1,2)*(A+sP@A))
        # Construct the actual source-lifted residual and its qutrit graph.
        source=Mat.diag([1,0,0,0,0])
        scaffold_density=Mat.diag([F(1,9),F(2,9),F(2,9),F(2,9),F(2,9)]).tensor(hn)
        lifted=source.tensor(residual)
        E01=Mat(3,{(0,1):1})
        graph=E01.tensor(lifted)+E01.star.tensor(lifted.star)
        graph_density=(F(1,3)*Mat.eye(3)).tensor(scaffold_density)
        measured=(graph_density@graph.star@graph).trace()
        assert measured==F(2,27)*(hn@residual.star@residual).trace()
        reports.append({"depth":n,"stand_in_dimension":hn.n,
            "identities":"exact rational","terminal_residual":"zero"})
    return reports

def check_group():
    rng=random.Random(20261103);count=0
    for trial in range(20):
        good={n for n in range(12) if rng.randrange(2)}
        def beta(x,y):
            out=set()
            for m in x:
                for l in y:
                    k=l-m
                    if k in good:out.symmetric_difference_update({k})
            return frozenset(out)
        def mul(g,h):
            x,y,z=g;u,v,w=h
            return (x^u,y^v,z^w^beta(x,v))
        def inv(g):
            x,y,z=g
            return x,y,z^beta(x,y)
        unit=(frozenset(),)*3
        def rand():
            return (frozenset(i for i in range(-5,6) if rng.randrange(4)==0),
                    frozenset(i for i in range(-5,6) if rng.randrange(4)==0),
                    frozenset(i for i in good if rng.randrange(2)))
        def shift(g,k):
            x,y,z=g
            return frozenset(i+k for i in x),frozenset(i+k for i in y),z
        for _ in range(100):
            g,h,k=rand(),rand(),rand()
            assert mul(mul(g,h),k)==mul(g,mul(h,k))
            assert mul(g,inv(g))==mul(inv(g),g)==unit
            t=rng.randrange(-8,9)
            assert shift(mul(g,h),t)==mul(shift(g,t),shift(h,t))
            count+=1
        b=(frozenset({0}),frozenset(),frozenset())
        c=(frozenset(),frozenset({0}),frozenset())
        for n in range(12):
            cn=shift(c,n)
            w=mul(mul(b,cn),mul(inv(b),inv(cn)))
            expected=(frozenset(),frozenset(),frozenset({n}) if n in good else frozenset())
            assert w==expected and mul(w,w)==unit
    return {"seed":20261103,"random_good_sets":20,
        "exact_associativity_inverse_shift_trials":count,
        "exact_selected_word_checks":240}

def check_rotation():
    theta=(math.sqrt(5)-1)/2
    margin=[]
    for y in range(1,4000):
        distance=abs(2*math.sin(math.pi*theta*y))
        m=math.log2(distance)+(y+1)
        margin.append(m)
        assert distance>2.0**(-min(y+1,1074))
        # Exact rational sufficient certificate for global lower bound:
        assert F(2)**(y+3)>F(9*y,4)+F(1,2)
    worst=min(margin)
    exact=certificate()
    assert 2.89<worst<2.9
    assert margin.index(worst)+1==1
    return {"theta":"(sqrt(5)-1)/2","y_range":[1,3999],
        "minimum_log2_margin":worst,"minimizer":margin.index(worst)+1,
        "numerical_check":"double precision; no overflow from 2^y",
        "global_bound":"4/(sqrt(5)*y+1/2) > 2^(-y-1), proved in paper",
        "exact_all_y_certificate":exact,
        "rational_sufficient_certificate":"2^(y+3)>9*y/4+1/2 exact for 1<=y<4000"}

def check_profiles():
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):
        result=runpy.run_path(str(Path(__file__).with_name("difference_profiles.py")))
    assert all(result["res"])
    return {"status":"PASS", "profile_checks":len(result["res"]),
      "monotone_functions":len(result["MON5"]), "without_shared_family":len(result["f1"]),
      "optimistic_no_spatial_family":len(result["f2"]),
      "with_shared_family":len(result["f3"]), "transcript":capture.getvalue()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True,
        help="new directory, or empty directory; shipped files are never overwritten")
    args=parser.parse_args()
    out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error("output directory must be new or empty; refusing overwrite")
    out.mkdir(parents=True,exist_ok=True)
    results={"status":"PASS","tree_exact":check_tree(),
        "separator_and_scaffolds":check_separator_and_scaffolds(),
        "reader_exact":check_reader(),"group_exact":check_group(),
        "rotation_numerical":check_rotation(),
        "difference_profiles":check_profiles(),
        "scope":"Finite identities only; not a proof of Higman, HNN embeddings, KMS or core classification."}
    results["script_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    # Exclusive mode also prevents a race from overwriting a previous result.
    with (out/"results.json").open("x",encoding="utf-8",newline="\n") as f:
        json.dump(results,f,indent=2,sort_keys=True);f.write("\n")
    lines=["ALL CHECKS PASSED",
        "Separator shift truncations and chain scaffolds: exact rational identities.",
        "Exact finite trees: depths 0..7; relations, modular ratio, spectral levels, masses, residuals.",
        "Entropy: numerical logarithms plus exact rational mean depth.",
        "Exact tree x 4-dimensional stand-in: depths 0..4; (19)-(21) and graph expansion.",
        "Exact group model: 20 good sets, 2000 associativity/inverse/shift trials, 240 word checks.",
        "Golden mean: 1<=y<4000, minimum log2 margin %.12f." %
          results["rotation_numerical"]["minimum_log2_margin"],
        "Golden mean: exact y=1, y=2 enclosures, y=3 tail base and affine induction coefficient; the all-y conclusion is the paper's induction.",
        "Boolean table: adversarial profiles and all 7581 monotone five-input functions passed.",
        "All arithmetic for matrix and group identities is exact.",
        "No arbitrary Higman/HNN presentation is tested by the stand-in."]
    with (out/"run.txt").open("x",encoding="utf-8",newline="\n") as f:
        f.write("\n".join(lines)+"\n")
    print("\n".join(lines))

if __name__=="__main__":main()
