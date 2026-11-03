"""Reproduce and certify the golden-mean bound failure using exact fractions."""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from math import isqrt
from pathlib import Path
import argparse, hashlib, json, math

def atan_bounds(x,terms=60):
    total=sum(((-1)**k*x**(2*k+1)/F(2*k+1) for k in range(terms)),F(0))
    nxt=(-1)**terms*x**(2*terms+1)/F(2*terms+1)
    return min(total,total+nxt),max(total,total+nxt)

def sin_bounds(x,terms=40):
    term=x;total=x
    for k in range(1,terms):
        term=-term*x*x/F((2*k)*(2*k+1))
        total+=term
    nxt=-term*x*x/F((2*terms)*(2*terms+1))
    return min(total,total+nxt),max(total,total+nxt)

def dec(q):
    return Decimal(q.numerator)/Decimal(q.denominator)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True,exist_ok=True)
    a,b=atan_bounds(F(1,5)),atan_bounds(F(1,239))
    pi_lo,pi_hi=16*a[0]-4*b[1],16*a[1]-4*b[0]
    scale=10**80
    k=isqrt(5*scale**2)
    rt_lo,rt_hi=F(k,scale),F(k+1,scale)
    assert rt_lo**2<5<rt_hi**2
    theta_lo,theta_hi=(rt_lo-1)/2,(rt_hi-1)/2
    x_lo,x_hi=pi_lo*theta_lo,pi_hi*theta_hi
    # Both arguments lie strictly between pi/2 and pi, where sin decreases.
    assert x_lo>pi_hi/2 and x_hi<pi_lo and 0<x_lo<x_hi<2
    sin_lo=sin_bounds(x_hi)[0]
    sin_hi=sin_bounds(x_lo)[1]
    # Ratio = 2^(y+1)*|exp(2*pi*i*theta*y)-1| = 8*sin(pi*theta) at y=1.
    ratio_lo,ratio_hi=8*sin_lo,8*sin_hi
    # Round outward to manageable exact rational enclosures for the certificate.
    grid=10**40
    ratio_lo=F((ratio_lo*grid).numerator//(ratio_lo*grid).denominator,grid)
    ratio_hi=F(-((-ratio_hi*grid).numerator//(-ratio_hi*grid).denominator),grid)
    assert 1<ratio_lo<ratio_hi
    # EXACT comparison: log2(ratio)<29/10 iff ratio^10<2^29.
    assert ratio_hi**10<2**29
    # A corrected conservative lower bound 2.89 is also certified exactly.
    assert ratio_lo**100>2**289
    with localcontext() as ctx:
        ctx.prec=65
        lo=dec(ratio_lo).ln()/Decimal(2).ln()
        hi=dec(ratio_hi).ln()/Decimal(2).ln()
        details={"status":"CLAIM_FALSE","counterexample_y":1,
            "claimed_log2_lower_bound":"2.9",
            "log2_margin_lower_approx":str(lo),
            "log2_margin_upper_approx":str(hi),
            "exact_certificate":"ratio_upper^10 < 2^29",
            "exact_positive_certificate":"ratio_lower > 1",
            "exact_conservative_lower_bound":"ratio_lower^100 > 2^289 (margin > 2.89)",
            "ratio_lower_fraction":str(ratio_lo),
            "ratio_upper_fraction":str(ratio_hi),
            "pi_enclosure":"Machin formula with alternating arctan remainder bounds",
            "sqrt5_enclosure":"integer-square-root rational enclosure at 80 decimal places",
            "sine_enclosure":"alternating-series bounds, monotonicity on (pi/2,pi)",
            "scope":"Refutes the stated 2.9 margin only; not a counterexample to contractivity or the main type classifications.",
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    theta=(math.sqrt(5)-1)/2
    sweep=min((math.log2(abs(2*math.sin(math.pi*theta*y)))+y+1,y)
              for y in range(1,4000))
    details["double_precision_sweep"]={"minimum":sweep[0],"minimizer":sweep[1],"range":[1,3999]}
    with (out/"margin-failure.json").open("x",encoding="utf-8",newline="\n") as f:
        json.dump(details,f,indent=2,sort_keys=True);f.write("\n")
    text=("CONFIRMED: the claimed golden-mean log2 margin >= 2.9 is false.\n"
          "Counterexample y=1; full finite sweep has minimum %.16f at y=%d.\n"
          "Exact rational certificate: ratio_upper^10 < 2^29.\n"
          "Exact rational certificate: ratio_lower^100 > 2^289.\n"
          "Thus 2.89 < the y=1 log2 margin < 2.9.\n"
          "The contraction threshold (margin >= 0) is not refuted.\n")%sweep
    with (out/"margin-failure.txt").open("x",encoding="utf-8",newline="\n") as f:f.write(text)
    print(text,end="")
if __name__=="__main__":main()
