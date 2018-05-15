cx = 814.21
cy = [315.48, 158.48, 3.48, -151.52]
k1 = -5.9624209455667325e-08
k2 = 2.7381910042256151e-14
fl = 1480.5907441315994

def undistort(c):
  xd, yd = c[0], c[1]
  for i in range(5):
    r2 = (xd**2+yd**2)
    dr = 1+k1*r2+k2*r2*r2
    xd = c[0]/dr
    yd = c[1]/dr
  return [xd, yd]

def distort(c):
  xd, yd = c[0], c[1]
  r2 = (xd**2+yd**2)
  dr = 1+k1*r2+k2*r2**2
  xd *= dr
  yd *= dr
  return [xd, yd]

def vector2xy(v, band):
  alpha = v[2]/fl
  cam = [v[0]/alpha, v[1]/alpha]
  cam = distort(cam)
  x = cam[0]+cx
  y = cam[1]+cy[band]
  return (x, y)

def xy2vector(x, y, band):
  cam = [x-cx, y-cy[band]]
  cam = undistort(cam)
  v = (cam[0], cam[1], fl)
  return v

