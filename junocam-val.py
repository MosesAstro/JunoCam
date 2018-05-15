import math
import sys, os
from spice import *
import Image, ImageDraw
try:
  import DDDImagePluginJuno
except:
  pass

import junocamlib

furnsh("naif0012.tls")
furnsh("pck00010.tpc")
furnsh(os.getenv("NAIFSPK"))
furnsh(os.getenv("NAIFCK"))
furnsh("juno_v12.tf")
furnsh("jup310.bsp")
furnsh("/u/juno/naif/latest_sck.tsc")

im = Image.open(sys.argv[1]).convert("RGB")
nframes = im.size[1]/384 # only works for RGB images
t0 = scs2e(-61, im.info["time"])+4094/50e3-20e-3 # metadata start time is 61.88 milliseconds early
interframe = float(im.info["interframe"])+1e-3 # metadata interframe is 1 millisecond short
print t0, et2utc(t0, "isoc", 3), interframe

targ = "jupiter"
radii = bodvrd(targ, "RADII", 3)[1]

def mark(x, y, color):
  pw = 1
  draw.point((x, y), fill=color)

def scan(t, f_offset, band, color):
  """scan over the framelet with the given offsets and mark all pixels that hit the planet"""
  for y in range(0, 128, 4):
    for x in range(0, 1600, 4):
      # construct the vector in juno_junocam space...
      v = junocamlib.xy2vector(x, y, band)
      # and see if it intersects the target.
      vx = sincpt("Ellipsoid", "jupiter", t, "iau_jupiter", "lt+s", "juno", "juno_junocam", v)
      if vx:
        mark(x, y+f_offset, color)

def planet(t, f_offset, band, color):
  """plot the planet's nominal limb"""
  to_targ = spkezr(targ, t, "iau_jupiter", "LT+S", "juno")[0][0:3]
  e = edlimb(radii[0], radii[1], radii[2], vminus(to_targ))
  c = pxform("iau_jupiter", "juno_junocam", t)
  org = vadd(e.center, to_targ)
  for th in range(-1800, 1800):
    p = vadd(org, vadd(vscl(math.cos(math.radians(th/10.0)), e.semi_major), vscl(math.sin(math.radians(th/10.0)), e.semi_minor)))
    x, y = junocamlib.vector2xy(mxv(c, p), band)
    if x >= 0 and x < 1648 and y >= 0 and y < 128:
      mark(x, y+f_offset, color)
  
def find(f_offset, band, color):
 for dt in range(0, nframes, 1):
  t = t0+dt*(interframe)
  #scan(t, f_offset+128*3*dt, band, color)
  planet(t, f_offset+128*3*dt, band, color)

draw = ImageDraw.Draw(im)
find(0, 1, "blue")
find(128, 2, "green")
find(256, 3, "red")
im.save("map%s.ddd"%sys.argv[1][:-4])

