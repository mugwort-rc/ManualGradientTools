# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ManualGradient
                                 A QGIS plugin
 Manual Gradient Tools
                             -------------------
        begin                : 2016-06-24
        copyright            : (C) 2016 by mugwort_rc
        email                : mugwort.rc@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ManualGradient class from file ManualGradient.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .manual_gradient import ManualGradient
    return ManualGradient(iface)
