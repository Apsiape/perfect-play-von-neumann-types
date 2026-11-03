"""Exact y=1, y=2 enclosures, y=3 tail base and affine induction coefficient; the all-y conclusion is the paper's induction (Python standard library)."""
from fractions import Fraction as F
from math import isqrt
from verify_margin_failure import atan_bounds, sin_bounds

def certificate():
    a,b=atan_bounds(F(1,5)),atan_bounds(F(1,239))
    pl,pu=16*a[0]-4*b[1],16*a[1]-4*b[0]
    scale=10**80; k=isqrt(5*scale**2)
    sl,su=F(k,scale),F(k+1,scale)
    assert sl**2<5<su**2
    tl,tu=(sl-1)/2,(su-1)/2
    xl,xu=pl*tl,pu*tu
    assert pl>3 and pu<F(22,7)
    assert xl>pu/2 and xu<pl and 0<xl<xu<2
    grid=10**40
    def down(x): return F((x*grid).numerator//(x*grid).denominator,grid)
    def up(x): return -down(-x)
    lo,hi=down(8*sin_bounds(xu)[0]),up(8*sin_bounds(xl)[1])
    assert 1<lo<hi<8
    assert lo**100>2**289 and hi**10<2**29
    yl,yu=pl*(2*tl-1),pu*(2*tu-1)
    assert 0<yl<yu<pl/2
    y2lo=down(16*sin_bounds(yl)[0]); assert y2lo>8
    assert F(9,4)**2>5
    assert 2**6>8*(F(9,4)*3+F(1,2))
    # For d_y=sqrt(5)*y+1/2, the paper uses 2*d_y>d_(y+1).
    # The interval lower bound is affine with positive slope on y>=3.
    slope=2*sl-su
    intercept=F(1,2)-su
    assert slope>0 and slope*3+intercept>0
    # Thus the ratio 2^(y+3)/d_y increases from its certified y=3 base.
    return {"status":"PASS", "ratio_y1_lower":str(lo),"ratio_y1_upper":str(hi),
      "ratio_y2_lower":str(y2lo), "log2_margin_y1":"strictly between 2.89 and 2.9",
      "global_minimizer":1,"domain":"all integers y>=1",
      "tail_certificate":"y>=3: r_y>8>r_1; exact base plus paper's affine denominator inequality",
      "induction_inequality":"2*(sqrt(5)*y+1/2)>sqrt(5)*(y+1)+1/2 for y>=3",
      "affine_lower_slope":str(slope),"affine_lower_at_3":str(slope*3+intercept),
      "contraction":"all y>=1: |exp(2*pi*i*theta*y)-1|>2^(-y-1)"}
