# Phase Error Propagation

## Motivation 

This small study aims to investigate how phase errors propagate through the lattice, 
using alpha and beta and their errors as boundary conditions.

In particular, this is a test whether the first plus-sign in 
Eq. (2) of 10.18429/JACOW-IPAC2015-MOPJE054  
( http://jacow.org/ipac2015/doi/JACoW-IPAC2015-MOPJE054.html )
should in fact be a minus sign:
$$
\sigma^2_\phi(s) = \left(\frac{1}{2\beta_0}\left(\left(\cos(2\phi(s)) -1 \right)\alpha_0 + \sin(2\phi(s))\right) \right)^2\sigma_{\beta_0}^2 + \left(\frac{1}{2}\left(\cos(2\phi(s)) -1 \right)\right)\sigma_{\alpha_0}^2 \qquad (1)
$$
$$
\sigma^2_\phi(s) = \left(\frac{1}{2\beta_0}\left(\left(\cos(2\phi(s)) -1 \right)\alpha_0 - \sin(2\phi(s))\right) \right)^2\sigma_{\beta_0}^2 + \left(\frac{1}{2}\left(\cos(2\phi(s)) -1 \right)\right)\sigma_{\alpha_0}^2 \qquad (2)
$$

Suitable alpha0 and beta0, means and standard deviations, 
are choosen and realized as boundary conditions for the FODO-lattice from 
Gaussian distributions.

From the resulting phase advance distributions, 
shifted to zero by the phase advance of the realization with only mean-values, 
the standard deviation is calculated (dashed green line) and compared to
the analytically propagated results 
(red for Eq. (1) with plus, blue for Eq. (2) with minus).
The plots show that the error propagation formula Eq. (2), 
with a negative sign, is the correct one.

![Result for 1000 realizations](result_1000realizations.png "Result for 1000 realizations")

## Setup

Python 3.7+ is required and the dependencies can be installed from the `requirements.txt`. 
This file contains the exact versions this script has been tested with, but it might run with newer
versions as well.