# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os
import pytest
import numpy as np
import astropy.units as u
from astropy.tests.helper import remote_data
from astropy.utils.data import get_pkg_data_filename
import synphot
from ..dust import *
from ..units import VEGAmag, JMmag


def test_phase_HalleyMarcus():
    assert np.isclose(phase_HalleyMarcus(0 * u.deg), 1.0)
    assert np.isclose(phase_HalleyMarcus(15 * u.deg), 5.8720e-01)
    assert np.isclose(phase_HalleyMarcus(14.5 * u.deg), 0.5959274462322928)


Wm2um = u.W / u.m**2 / u.um


class TestAfrho:
    def test_init(self):
        afrho = Afrho(1000 * u.cm)
        assert afrho.value == 1000
        assert afrho.unit == u.cm

    def test_scaler_ops(self):
        afrho = Afrho(1000 * u.cm)
        afrho = afrho / 2
        assert afrho == 500 * u.cm

    def test_quantity_ops(self):
        afrho = Afrho(1000 * u.cm)
        v = afrho * 2 * u.cm
        assert v == 2000 * u.cm**2
        assert not isinstance(v, Afrho)

    @pytest.mark.parametrize('wfb, fluxd0, rho, rh, delta, S, afrho0, tol', (
        (0.55 * u.um, 6.7641725e-14 * Wm2um, '1 arcsec', 1.5, 1.0, None,
         1000, 0.001),
        (666.21 * u.THz, 6 * u.mJy, '1 arcsec', 1.5, 1.0, None,
         1000, 0.001),
        (None, 4.68e-15 * Wm2um, '5000 km', 4.582, 4.042, 1730 * Wm2um,
         1660, 0.01),
        (None, 16.98 * VEGAmag, '5000 km', 4.582, 4.042, -26.93 * VEGAmag,
         1660, 0.01),
        (None, 11.97 * u.ABmag, '19.2 arcsec', 1.098, 0.164,
         -26.93 * u.ABmag, 34.9, 0.01)
        ('WFC3 F606W', 16.98 * VEGAmag, '5000 km', 4.582, 4.042, None,
         1680, 0.01),
        ('WFC3 F438W', 17.91 * VEGAmag, '5000 km', 4.582, 4.042, None,
         1550, 0.01),
        ('Cousins I', 7.97 * JMmag, '10000 km', 1.45, 0.49, None,
         3188, 0.01),
        ('SDSS r', 11.97 * u.ABmag, '19.2 arcsec', 1.098, 0.164, None,
         34.9, 0.01),
        ('SDSS r', 12.23 * u.STmag, '19.2 arcsec', 1.098, 0.164, None,
         34.9, 0.01),
    ))
    def test_from_fluxd(self, wfb, fluxd0, rho, rh, delta, S, afrho0, tol):
        """Flux density to afrho conversions.

        HST/WFC3 photometry of C/2013 A1 (Siding Spring) (Li et
        al. 2014).  Uncertainty is 5%.  Li et al. (2013) quotes the
        Sun in F606W as 1730 W/m2/um.  Confirmed with J.-Y. Li that
        1707 W/m2/um is a better value (via effective stimulus
        formula).  Leaving the test with original values.

        Woodward et al. photometry of C/2007 N3 (Lulin) in I-band.
        Their magnitude has been modifιed from 8.49 to 7.97 according
        to their phase correction (0.03 mag/deg, phase angle 17.77
        deg).  Uncertainty is 0.06 mag.

        Li et al. (2017) DCT photometry of 252P/LINEAR in r'.  An
        additional test is performed with this observation after
        converting ABmag to STmag:

            synphot.units.convert_flux(6182, 11.97 * u.ABmag, u.STmag)

        """
        rho = u.Quantity(rho)
        eph = Ephem(dict(rh=rh * u.au, delta=delta * u.au))
        if isinstance(wfb, str):
            wfb = utils.get_bandpass(wfb)

        # test from_fluxd
        afrho = Afrho.from_fluxd(wfb, fluxd0, rho, eph, S=S).to('cm')
        assert np.isclose(afrho.value, afrho0, rtol=tol)

        # test to_fluxd
        fluxd = Afrho(afrho0 * u.cm).to_fluxd(wfb, rho, eph, unit=unit, S=S)
        k = 'atol' if isinstance(fluxd, u.Magnitude) else 'rtol'
        assert np.isclose(fluxd.value, fluxd0.value, **{k: tol})

    def test_phasecor(self):
        a0frho = Afrho(100 * u.cm)
        wave = 1 * u.um
        eph = {'rh': 1 * u.au, 'delta': 1 * u.au, 'phase': 100 * u.deg}
        aper = 10 * u.arcsec
        S = 1000 * Wm2um

        # fluxd at 0 deg phase
        fluxd0 = a0frho.to_fluxd(wave, aper, eph, S=S, phasecor=False)

        # fluxd at 100 deg phase
        fluxd = a0frho.to_fluxd(wave, aper, eph, S=S, phasecor=True)
        assert np.isclose(fluxd / fluxd0, phase_HalleyMarcus(eph['phase']))

        # convert back to 0 deg phase
        afrho = Afrho.from_fluxd(wave, fluxd, aper, eph, S=S, phasecor=True)
        assert np.isclose(a0frho.value, afrho.value)

    def test_to_phase(self):
        afrho = Afrho(10 * u.cm).to_phase(15 * u.deg, 0 * u.deg).to('cm')
        assert np.isclose(afrho.value, 5.8720)

    def test_from_fluxd_PR125(self):
        """Regression test for PR#125: User requested Phi was ignored."""
        afrho = Afrho(100 * u.cm)
        wave = 1 * u.um
        eph = {'rh': 1 * u.au, 'delta': 1 * u.au, 'phase': 100 * u.deg}
        aper = 10 * u.arcsec
        opts = {
            # nonsense phase function:
            'Phi': lambda phase: 1 + u.Quantity(phase, 'deg').value,
            'S': 1000 * Wm2um
        }

        f0 = afrho.fluxd(wave, aper, eph, phasecor=False, **opts)
        f1 = afrho.fluxd(wave, aper, eph, phasecor=True, **opts)
        assert np.isclose(f0.value * 101, f1.value)

        a0 = Afrho.from_fluxd(wave, f0, aper, eph, phasecor=False, **opts)
        a1 = Afrho.from_fluxd(wave, f0, aper, eph, phasecor=True, **opts)
        assert np.isclose(a0.value / 101, a1.value)


class TestEfrho:
    def test_init(self):
        efrho = Efrho(1000 * u.cm)
        assert efrho.value == 1000
        assert efrho.unit == u.cm

    def test_scaler_ops(self):
        efrho = Efrho(1000 * u.cm)
        efrho = efrho / 2
        assert efrho == 500 * u.cm

    def test_quantity_ops(self):
        efrho = Efrho(1000 * u.cm)
        v = efrho * 2 * u.cm
        assert v == 2000 * u.cm**2
        assert not isinstance(v, Efrho)

    @pytest.mark.parametrize('efrho0,wfb,fluxd0,rh,delta,unit,B,tol', (
        (1000, 10 * u.um, 3.824064-15 * Wm2um, 1.5, 1.0, None, None, 0.001),
        (33.0, 25.624 * u.THz, 0.0060961897 * u.Jy, 1.5, 1.0, None,
         None, 0.001),
        (33.0, 11.7 * u.um, 6.0961897 * u.mJy, 1.5, 1.0, u.mJy, None, 0.001),
        (33.0, synphot.SpectralElement(synphot.Box1D, x_0=11.7 * u.um,
                                       width=0.1 * u.um),
         6.0961897 * u.mJy, 1.5, 1.0, u.mJy, None, 0.001),
        (616.1, synphot.SpectralElement(synphot.Box1D, x_0=11.7 * u.um,
                                        width=0.1 * u.um),
         5 * VEGAmag, 1.0, 1.0, VEGAmag, None, 0.001),
        (78750, 11.7 * u.um, 5 * u.ABmag, 1.0, 1.0, u.ABmag, None, 0.001),
        (3.596e7, 11.7 * u.um, 5 * u.STmag, 1.0, 1.0, u.STmag, None, 0.001),
    ))
    def test_from_fluxd(self, wfb, fluxd, efrho, B, tol):
        rho = 1 * u.arcsec
        eph = dict(rh=1.5 * u.au, delta=1.0 * u.au)
        efrho = (Efrho.from_fluxd(wfb, fluxd, rho, eph, Tscale=1.1, B=B)
                 .to('cm'))
        k = 'atol' if isinstance(fluxd, u.Magnitude) else 'rtol'
        tol =
        assert np.isclose(efrho.value, 1000, **{k: 0.001})
