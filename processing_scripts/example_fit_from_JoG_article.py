# with the machine fit
g = 9.81


def funcFitDecay(frq, nuFit):
    return (nuFit**0.5) * ((2 * np.pi * frq)**(7. / 2.)) / (2**0.5) / (g**2)

# fit without taking into account uncertainty on spectra
viscosity, covariance = scipy.optimize.curve_fit(funcFitDecay, listFrequenciesForFit, listDampingForFit,p0=0.01,sigma=0.1)
perr = np.sqrt(np.diag(covariance))

print " "
print "Parameters and fit quality from machine fit"
print "Viscosity from machine fit: " + str(viscosity)
print "1 sigma confidence: " + str(perr)

# residuals in the fitting of the model
residuals = listDampingForFit - funcFitDecay(listFrequenciesForFit, viscosity)

# check the quality statistics
# from http://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
ss_res = np.sum(residuals**2)
ss_tot = np.sum((listDampingForFit-np.mean(listDampingForFit))**2)
r_squared = 1 - (ss_res / ss_tot)

print "R2: " + str(r_squared)

# compute MAE (Mean Absolute Error) and RMSE (Root Mean Square Error)
MAE = np.mean(np.abs(residuals))
RMSE = np.sqrt(np.mean(residuals**2))

print "MAE  of residuals damping: " + str(MAE)
print "RMSE of residuals damping: " + str(RMSE)
