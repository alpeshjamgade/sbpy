# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
========================
SBPy Activity Gas Module
========================

Functions
---------
photo_lengthscale          - Photodissociation lengthscale.
photo_timescale            - Photodissociation timescale.
fluorescence_band_strength - Fluorescence band efficiency of a specific
                             species and transition.

Classes
-------
Activity            - Abstract base class for gas coma models.
Haser               - Haser coma model for gas (Haser 1957).
Vectorial           - Vectorial coma model for gas (Festou 1981).


"""

from abc import ABC, abstractmethod
import astropy.units as u
from .. import bib
from .core import Aperture


__all__ = [
    'photo_lengthscale',
    'photo_timescale',
    'fluorescence_band_strength',

    'Haser',
    'Vectorial',
]


def photo_lengthscale(species, source=None):
    """Photodissociation lengthscale for a gas species.

    Parameters
    ----------
    species : string
      The species to look up.
    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.

    Returns
    -------
    gamma : astropy Quantity
      The lengthscale at 1 au.

    Example
    -------
    >>> from sbpy.activity import photo_lengthscale
    >>> gamma = photo_lengthscale('OH')

    References
    ----------

    [CS93] H2O and OH from Table IV of Cochran & Schleicher 1993,
    Icarus 105, 235-253.  Quoted for intermediate solar activity.

    [CE83] CO2 from Crovisier & Encrenaz 1983, A&A 126, 170-182.

    """

    data = {   # (value, ADS bibcode)
        'H2O': {
            'CS93': (2.4e4 * u.s, '1993Icar..105..235C'),
        },
        'OH': {
            'CS93': (1.6e5 * u.s, '1993Icar..105..235C'),
        },
    }

    default_sources = {
        'H2O': 'CS93',
        'OH': 'CS93',
    }

    assert species.upper() in data, "No timescale available for {}.  Choose from: {}".format(
        species, ', '.join(data.keys()))

    gas = data[species.upper()]
    source = default_sources[species.upper()] if source is None else source

    assert source.upper() in gas, 'Source key {} not available for {}.  Choose from: {}'.format(
        source, species, ', '.join(gas.keys()))

    gamma, bibcode = gas[source.upper()]
    bib.register('activity.gas.photo_lengthscale', bibcode)

    return gamma

def photo_timescale(species, source=None):
    """Photodissociation timescale for a gas species.

    Parameters
    ----------
    species : string
      The species to look up.
    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.

    Returns
    -------
    tau : astropy Quantity
      The timescale at 1 au.

    Example
    -------
    >>> from sbpy.activity import photo_timescale
    >>> tau = photo_timescale('OH')

    References
    ----------

    [CS93] H2O and OH from Table IV of Cochran & Schleicher 1993,
    Icarus 105, 235-253.  Quoted for intermediate solar activity.

    [CE83] CO2 from Crovisier & Encrenaz 1983, A&A 126, 170-182.

    """

    data = {   # (value, ADS bibcode)
        'H2O': { 'CS93': (5.2e4 * u.s, '1993Icar..105..235C'), },
        'OH':  { 'CS93': (1.6e5 * u.s, '1993Icar..105..235C'), },
        'CO2': { 'CE83': (5.0e5 * u.s, '1983A%26A...126..170C'), },
        'CO':  { 'CE83': (1.5e6 * u.s, '1983A%26A...126..170C'), },
    }

    default_sources = {
        'H2O': 'CS93',
        'OH': 'CS93',
        'CO2': 'CE83',
        'CO': 'CE83',
    }

    assert species.upper() in data, "No timescale available for {}.  Choose from: {}".format(
        species, ', '.join(data.keys()))

    gas = data[species.upper()]
    source = default_sources[species.upper()] if source is None else source

    assert source.upper() in gas, 'Source key {} not available for {}.  Choose from: {}'.format(
        source, species, ', '.join(gas.keys()))

    tau, bibcode = gas[source.upper()]
    bib.register('activity.gas.photo_timescale', bibcode)

    return tau

def fluorescence_band_strength(species, rdot=0 * u.km / u.s,
                               eph=None, source=None):
    """Fluorescence band efficiency of a specific species and transition.

    Parameters
    ----------
    species : string
      The species to look up.
    rdot : astropy Quantity, optional
      Heliocentric radial speed, required for some species.
    eph : sbpy Ephem, optional
      The target ephemeris.  Must include heliocentric radial
      velocity.
    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.

    Returns
    -------
    tau : astropy Quantity
      The timescale, scaled to `rh` or `eph['rh']`.

    Notes
    -----
    One of `rdot` or `eph` is required for some species.

    Examples
    --------
    >>> from sbpy.activity import fluorescence_band_strength
    >>> LN = fluorescence_band_strength('OH')  # doctest: +SKIP

    References
    ----------
    [SA88] OH from Schleicher & A'Hearn 1988, ApJ 331, 1058-1077.
    Requires `rdot`.

    """

    raise NotImplemented

    # implement list treatment
    
    data = {   # (value, bibcode)
        'OH 0-0': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 1-0': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 1-1': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 2-2': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
    }

    default_sources = {
        'OH 0-0': (model, 'SA88'),
    }

    assert species.upper() in data, 'No data available for {}.  Choose one of: {}'.format(
        species, ', '.join(data.keys()))

    band = data[species.upper()]

    assert source.upper() in band, 'No source {} for {}.  Choose one of: {}'.format(
        source, sepcies, ', '.join(band.keys()))
    
    LN, bibcode = band[source.upper()]
    bib.register('activity.gas.fluorescence_band_strength', bibcode)

    something_about_rdot_here
    
    return LN


class GasComa(ABC):
    """Abstract base class for gas coma models."""
    
    def __init__(self, Q):
        assert Q.unit.is_equivalent((u.s**-1, u.mol / u.s))
        self.Q = Q

    def volume_density(self, aperture, eph):
        """Calculate coma volume density in aperture

        Parameters
        ----------
        aperture : `sbpy.activity.aperture.Aperture` instance, mandatory
            aperture
        eph : `sbpy.data.Ephem` instance, mandatory
            ephemerides at epoch, required: heliocentric distance `rh`

        Returns
        -------
        integer

        Examples
        --------
        TBD

        not yet implemented

        """
        pass


    def column_density(self, aperture, eph):
        """Calculate coma column density in aperture

        Parameters
        ----------
        aperture : `sbpy.activity.Aperture` instance, mandatory
            aperture
        eph : `sbpy.data.Ephem` instance, mandatory
            ephemerides at epoch, required: heliocentric distance `rh`

        Returns
        -------
        integer

        Examples
        --------
        TBD

        not yet implemented

        """
        pass
        
    def total_number(self, aperture, eph):
        """Calculate total number of molecules in aperture 

        Parameters
        ----------
        aperture : `sbpy.activity.Aperture` instance, mandatory
            aperture
        eph : `sbpy.data.Ephem` instance, mandatory
            ephemerides at epoch, required: heliocentric distance `rh`

        Returns
        -------
        integer

        Examples
        --------
        TBD

        not yet implemented

        """
        pass
        

class Haser(GasComa):
    """Haser model implementation"""
    
    def __init__(self, Q, gamma):
        """Parameters
        ----------
        Q : `Astropy.units` quantity or iterable, mandatory
            production rate usually in units of `u.molecule / u.s`
        gamma : `Astropy.units` quantity or iterable, mandatory
            scale length usually in units of `u.km`

        Returns
        -------
        Haser instance

        Examples
        --------
        TBD

        not yet implemented

        """
        
        pass
        


class Vectorial(GasComa):
    """Vectorial model implementation"""
    
    def __init__(self, Q, species):
        """Parameters
        ----------
        Q : `Astropy.units` quantity or iterable, mandatory
            production rate usually in units of `u.molecule / u.s`
        species : dictionary or list of dictionares, mandatory
            defines gas velocity, lifetimes, disassociative lifetimes 

        Returns
        -------
        Vectorial instance

        Examples
        --------
        TBD

        not yet implemented

        """

        pass
